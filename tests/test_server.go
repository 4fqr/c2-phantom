package main

import (
	"context"
	"encoding/json"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

// ============================================================================
// Test Setup
// ============================================================================

func setupTestServer() *C2Server {
	gin.SetMode(gin.TestMode)

	// Use in-memory SQLite for testing
	db, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{})
	if err != nil {
		panic(err)
	}

	// Auto migrate
	db.AutoMigrate(&Agent{}, &Task{}, &Operator{})

	ctx, cancel := context.WithCancel(context.Background())

	server := &C2Server{
		config: &ServerConfig{
			HTTPPort:    8080,
			HTTPSPort:   443,
			DatabaseURL: "",
			MaxAgents:   1000,
			LogLevel:    "silent",
		},
		db:     db,
		ctx:    ctx,
		cancel: cancel,
	}

	server.initRouter()
	return server
}

func createTestAgent(db *gorm.DB) *Agent {
	agent := &Agent{
		ID:           "test-agent-123",
		Hostname:     "test-host",
		Username:     "test-user",
		OS:           "Windows",
		Architecture: "x64",
		IP:           "127.0.0.1",
		PID:          1234,
		FirstSeen:    time.Now(),
		LastSeen:     time.Now(),
		Active:       true,
	}
	db.Create(agent)
	return agent
}

func createTestOperator(db *gorm.DB) *Operator {
	operator := &Operator{
		Username:  "test-operator",
		APIKey:    "test-api-key-123",
		CreatedAt: time.Now(),
	}
	db.Create(operator)
	return operator
}

// ============================================================================
// Agent Registration Tests
// ============================================================================

func TestAgentRegister(t *testing.T) {
	server := setupTestServer()
	defer server.cancel()

	payload := `{
		"hostname": "test-pc",
		"username": "testuser",
		"os": "Windows",
		"architecture": "x64",
		"pid": 5678
	}`

	req := httptest.NewRequest("POST", "/api/v1/agents/register", strings.NewReader(payload))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.router.ServeHTTP(w, req)

	if w.Code != 200 {
		t.Errorf("Expected status 200, got %d", w.Code)
	}

	var response map[string]interface{}
	if err := json.Unmarshal(w.Body.Bytes(), &response); err != nil {
		t.Fatalf("Failed to parse response: %v", err)
	}

	if !response["success"].(bool) {
		t.Error("Expected success=true")
	}

	if response["agent_id"] == nil {
		t.Error("Expected agent_id in response")
	}
}

func TestAgentRegisterInvalidPayload(t *testing.T) {
	server := setupTestServer()
	defer server.cancel()

	payload := `{"invalid": "data"}`

	req := httptest.NewRequest("POST", "/api/v1/agents/register", strings.NewReader(payload))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.router.ServeHTTP(w, req)

	if w.Code != 400 {
		t.Errorf("Expected status 400, got %d", w.Code)
	}
}

// ============================================================================
// Agent Beacon Tests
// ============================================================================

func TestAgentBeacon(t *testing.T) {
	server := setupTestServer()
	defer server.cancel()

	agent := createTestAgent(server.db)

	req := httptest.NewRequest("POST", "/api/v1/agents/"+agent.ID+"/beacon", nil)
	w := httptest.NewRecorder()

	server.router.ServeHTTP(w, req)

	if w.Code != 200 {
		t.Errorf("Expected status 200, got %d", w.Code)
	}

	var response map[string]interface{}
	if err := json.Unmarshal(w.Body.Bytes(), &response); err != nil {
		t.Fatalf("Failed to parse response: %v", err)
	}

	if response["beacon_interval"] == nil {
		t.Error("Expected beacon_interval in response")
	}
}

func TestAgentBeaconNotFound(t *testing.T) {
	server := setupTestServer()
	defer server.cancel()

	req := httptest.NewRequest("POST", "/api/v1/agents/nonexistent/beacon", nil)
	w := httptest.NewRecorder()

	server.router.ServeHTTP(w, req)

	if w.Code != 404 {
		t.Errorf("Expected status 404, got %d", w.Code)
	}
}

// ============================================================================
// Task Tests
// ============================================================================

func TestCreateTask(t *testing.T) {
	server := setupTestServer()
	defer server.cancel()

	agent := createTestAgent(server.db)
	operator := createTestOperator(server.db)

	payload := `{
		"agent_id": "` + agent.ID + `",
		"command": "whoami",
		"arguments": []
	}`

	req := httptest.NewRequest("POST", "/api/v1/tasks", strings.NewReader(payload))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-API-Key", operator.APIKey)
	w := httptest.NewRecorder()

	server.router.ServeHTTP(w, req)

	if w.Code != 200 {
		t.Errorf("Expected status 200, got %d", w.Code)
	}

	var task Task
	if err := json.Unmarshal(w.Body.Bytes(), &task); err != nil {
		t.Fatalf("Failed to parse response: %v", err)
	}

	if task.Command != "whoami" {
		t.Errorf("Expected command 'whoami', got '%s'", task.Command)
	}

	if task.Status != "pending" {
		t.Errorf("Expected status 'pending', got '%s'", task.Status)
	}
}

func TestCreateTaskUnauthorized(t *testing.T) {
	server := setupTestServer()
	defer server.cancel()

	agent := createTestAgent(server.db)

	payload := `{
		"agent_id": "` + agent.ID + `",
		"command": "whoami",
		"arguments": []
	}`

	req := httptest.NewRequest("POST", "/api/v1/tasks", strings.NewReader(payload))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.router.ServeHTTP(w, req)

	if w.Code != 401 {
		t.Errorf("Expected status 401, got %d", w.Code)
	}
}

func TestGetTasks(t *testing.T) {
	server := setupTestServer()
	defer server.cancel()

	agent := createTestAgent(server.db)
	operator := createTestOperator(server.db)

	// Create test task
	task := &Task{
		AgentID:   agent.ID,
		Command:   "whoami",
		Arguments: "[]",
		Status:    "pending",
		CreatedAt: time.Now(),
	}
	server.db.Create(task)

	req := httptest.NewRequest("GET", "/api/v1/agents/"+agent.ID+"/tasks", nil)
	w := httptest.NewRecorder()

	server.router.ServeHTTP(w, req)

	if w.Code != 200 {
		t.Errorf("Expected status 200, got %d", w.Code)
	}

	var tasks []Task
	if err := json.Unmarshal(w.Body.Bytes(), &tasks); err != nil {
		t.Fatalf("Failed to parse response: %v", err)
	}

	if len(tasks) != 1 {
		t.Errorf("Expected 1 task, got %d", len(tasks))
	}
}

func TestTaskResults(t *testing.T) {
	server := setupTestServer()
	defer server.cancel()

	agent := createTestAgent(server.db)

	task := &Task{
		AgentID:   agent.ID,
		Command:   "whoami",
		Arguments: "[]",
		Status:    "sent",
		CreatedAt: time.Now(),
	}
	server.db.Create(task)

	payload := `{
		"task_id": ` + string(rune(task.ID)) + `,
		"success": true,
		"output": "test-user"
	}`

	req := httptest.NewRequest("POST", "/api/v1/agents/"+agent.ID+"/results", strings.NewReader(payload))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.router.ServeHTTP(w, req)

	if w.Code != 200 {
		t.Errorf("Expected status 200, got %d", w.Code)
	}

	// Verify task was updated
	var updatedTask Task
	server.db.First(&updatedTask, task.ID)

	if updatedTask.Status != "completed" {
		t.Errorf("Expected status 'completed', got '%s'", updatedTask.Status)
	}
}

// ============================================================================
// Operator API Tests
// ============================================================================

func TestListAgents(t *testing.T) {
	server := setupTestServer()
	defer server.cancel()

	createTestAgent(server.db)
	operator := createTestOperator(server.db)

	req := httptest.NewRequest("GET", "/api/v1/agents", nil)
	req.Header.Set("X-API-Key", operator.APIKey)
	w := httptest.NewRecorder()

	server.router.ServeHTTP(w, req)

	if w.Code != 200 {
		t.Errorf("Expected status 200, got %d", w.Code)
	}

	var agents []Agent
	if err := json.Unmarshal(w.Body.Bytes(), &agents); err != nil {
		t.Fatalf("Failed to parse response: %v", err)
	}

	if len(agents) != 1 {
		t.Errorf("Expected 1 agent, got %d", len(agents))
	}
}

func TestGetAgent(t *testing.T) {
	server := setupTestServer()
	defer server.cancel()

	agent := createTestAgent(server.db)
	operator := createTestOperator(server.db)

	req := httptest.NewRequest("GET", "/api/v1/agents/"+agent.ID, nil)
	req.Header.Set("X-API-Key", operator.APIKey)
	w := httptest.NewRecorder()

	server.router.ServeHTTP(w, req)

	if w.Code != 200 {
		t.Errorf("Expected status 200, got %d", w.Code)
	}

	var retrievedAgent Agent
	if err := json.Unmarshal(w.Body.Bytes(), &retrievedAgent); err != nil {
		t.Fatalf("Failed to parse response: %v", err)
	}

	if retrievedAgent.ID != agent.ID {
		t.Errorf("Expected agent ID '%s', got '%s'", agent.ID, retrievedAgent.ID)
	}
}

func TestDeleteAgent(t *testing.T) {
	server := setupTestServer()
	defer server.cancel()

	agent := createTestAgent(server.db)
	operator := createTestOperator(server.db)

	req := httptest.NewRequest("DELETE", "/api/v1/agents/"+agent.ID, nil)
	req.Header.Set("X-API-Key", operator.APIKey)
	w := httptest.NewRecorder()

	server.router.ServeHTTP(w, req)

	if w.Code != 200 {
		t.Errorf("Expected status 200, got %d", w.Code)
	}

	// Verify agent was deleted
	var count int64
	server.db.Model(&Agent{}).Where("id = ?", agent.ID).Count(&count)

	if count != 0 {
		t.Error("Agent was not deleted")
	}
}

func TestGetStats(t *testing.T) {
	server := setupTestServer()
	defer server.cancel()

	createTestAgent(server.db)
	operator := createTestOperator(server.db)

	req := httptest.NewRequest("GET", "/api/v1/stats", nil)
	req.Header.Set("X-API-Key", operator.APIKey)
	w := httptest.NewRecorder()

	server.router.ServeHTTP(w, req)

	if w.Code != 200 {
		t.Errorf("Expected status 200, got %d", w.Code)
	}

	var stats map[string]interface{}
	if err := json.Unmarshal(w.Body.Bytes(), &stats); err != nil {
		t.Fatalf("Failed to parse response: %v", err)
	}

	if stats["total_agents"] == nil {
		t.Error("Expected total_agents in stats")
	}
}

// ============================================================================
// Health Check Test
// ============================================================================

func TestHealthCheck(t *testing.T) {
	server := setupTestServer()
	defer server.cancel()

	req := httptest.NewRequest("GET", "/health", nil)
	w := httptest.NewRecorder()

	server.router.ServeHTTP(w, req)

	if w.Code != 200 {
		t.Errorf("Expected status 200, got %d", w.Code)
	}

	var response map[string]interface{}
	if err := json.Unmarshal(w.Body.Bytes(), &response); err != nil {
		t.Fatalf("Failed to parse response: %v", err)
	}

	if response["status"] != "ok" {
		t.Error("Expected status 'ok'")
	}
}

// ============================================================================
// Benchmark Tests
// ============================================================================

func BenchmarkAgentRegister(b *testing.B) {
	server := setupTestServer()
	defer server.cancel()

	payload := `{
		"hostname": "bench-pc",
		"username": "benchuser",
		"os": "Windows",
		"architecture": "x64",
		"pid": 9999
	}`

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		req := httptest.NewRequest("POST", "/api/v1/agents/register", strings.NewReader(payload))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()
		server.router.ServeHTTP(w, req)
	}
}

func BenchmarkAgentBeacon(b *testing.B) {
	server := setupTestServer()
	defer server.cancel()

	agent := createTestAgent(server.db)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		req := httptest.NewRequest("POST", "/api/v1/agents/"+agent.ID+"/beacon", nil)
		w := httptest.NewRecorder()
		server.router.ServeHTTP(w, req)
	}
}

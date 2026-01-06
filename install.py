#!/usr/bin/env python3
"""
Installation and verification script for C2 Phantom.
Checks dependencies, installs package, and runs basic tests.
"""

import sys
import subprocess
import os
from pathlib import Path


def print_header(text: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_success(text: str) -> None:
    """Print success message."""
    print(f"✓ {text}")


def print_error(text: str) -> None:
    """Print error message."""
    print(f"✗ {text}")


def print_info(text: str) -> None:
    """Print info message."""
    print(f"ℹ {text}")


def check_python_version() -> bool:
    """Check if Python version is compatible."""
    print_header("Checking Python Version")
    version = sys.version_info

    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major == 3 and version.minor >= 9:
        print_success(f"Python {version.major}.{version.minor} is compatible")
        return True
    else:
        print_error(f"Python 3.9 or higher is required (found {version.major}.{version.minor})")
        return False


def install_package() -> bool:
    """Install C2 Phantom package."""
    print_header("Installing C2 Phantom")

    try:
        # Install in development mode
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", "."],
            capture_output=True,
            text=True,
            check=True,
        )

        print_success("Package installed successfully")
        return True

    except subprocess.CalledProcessError as e:
        print_error(f"Installation failed: {e.stderr}")
        return False


def install_dev_dependencies() -> bool:
    """Install development dependencies."""
    print_header("Installing Development Dependencies")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", ".[dev]"],
            capture_output=True,
            text=True,
            check=True,
        )

        print_success("Development dependencies installed")
        return True

    except subprocess.CalledProcessError as e:
        print_error(f"Installation failed: {e.stderr}")
        return False


def verify_installation() -> bool:
    """Verify C2 Phantom is installed correctly."""
    print_header("Verifying Installation")

    try:
        # Check if package can be imported
        import c2_phantom

        print_success(f"Package import successful (version {c2_phantom.__version__})")

        # Check if CLI is available
        result = subprocess.run(
            ["phantom", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )

        print_success(f"CLI available: {result.stdout.strip()}")
        return True

    except ImportError as e:
        print_error(f"Package import failed: {e}")
        return False
    except subprocess.CalledProcessError as e:
        print_error(f"CLI not available: {e}")
        return False


def initialize_phantom() -> bool:
    """Initialize C2 Phantom configuration."""
    print_header("Initializing C2 Phantom")

    try:
        # Check if already initialized
        config_path = Path.home() / ".phantom" / "config.yaml"

        if config_path.exists():
            print_info("Configuration already exists")
            response = input("Reinitialize? (y/N): ")
            if response.lower() != "y":
                return True

        # Initialize
        result = subprocess.run(
            ["phantom", "init", "--force"] if config_path.exists() else ["phantom", "init"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print_success("Initialization complete")
            print_info(f"Configuration: {config_path}")
            return True
        else:
            print_error(f"Initialization failed: {result.stderr}")
            return False

    except Exception as e:
        print_error(f"Initialization error: {e}")
        return False


def run_tests() -> bool:
    """Run test suite."""
    print_header("Running Tests")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-v", "--tb=short"],
            capture_output=True,
            text=True,
        )

        print(result.stdout)

        if result.returncode == 0:
            print_success("All tests passed")
            return True
        else:
            print_error("Some tests failed")
            print(result.stderr)
            return False

    except Exception as e:
        print_info(f"Tests not run: {e}")
        return True  # Don't fail if tests can't run


def show_next_steps() -> None:
    """Show next steps to user."""
    print_header("Next Steps")

    print("\n🎉 Installation complete! Here's what you can do next:\n")
    print("1. View help:")
    print("   phantom --help")
    print("\n2. List available commands:")
    print("   phantom --help")
    print("\n3. Check sessions:")
    print("   phantom list")
    print("\n4. Connect to a target:")
    print("   phantom connect https://example.com")
    print("\n5. Manage plugins:")
    print("   phantom plugin list")
    print("\n📖 Read the documentation:")
    print("   - README.md - Full documentation")
    print("   - QUICKSTART.md - Quick start guide")
    print("   - examples/ - Example scripts")
    print("\n⚠️  Remember: Use only for AUTHORIZED security testing!")
    print()


def main() -> int:
    """Main installation workflow."""
    print("\n🔮 C2 Phantom Installation Script\n")

    # Check Python version
    if not check_python_version():
        return 1

    # Install package
    if not install_package():
        return 1

    # Install dev dependencies (optional)
    print_info("Installing development dependencies...")
    install_dev_dependencies()  # Don't fail if this doesn't work

    # Verify installation
    if not verify_installation():
        return 1

    # Initialize
    if not initialize_phantom():
        return 1

    # Run tests (optional)
    print_info("Running tests (optional)...")
    run_tests()  # Don't fail if tests don't pass

    # Show next steps
    show_next_steps()

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)

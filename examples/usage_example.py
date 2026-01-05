"""
Example script demonstrating C2 Phantom usage.
"""

import asyncio
from c2_phantom.network.http import HTTPChannel
from c2_phantom.crypto.encryption import AESEncryption
from c2_phantom.core.session import SessionManager
from c2_phantom.plugins.loader import PluginLoader


async def main():
    """Main example function."""
    print("🔮 C2 Phantom - Example Usage\n")

    # Example 1: Create and manage sessions
    print("=" * 50)
    print("Example 1: Session Management")
    print("=" * 50)

    session_manager = SessionManager()
    session = session_manager.create_session(
        target="192.168.1.100",
        protocol="https",
        encryption="aes256-gcm",
    )

    print(f"Created session: {session.id}")
    print(f"Target: {session.target}")
    print(f"Protocol: {session.protocol}")
    print(f"Encryption: {session.encryption}")

    # Example 2: Encryption
    print("\n" + "=" * 50)
    print("Example 2: AES-256-GCM Encryption")
    print("=" * 50)

    aes = AESEncryption()
    plaintext = b"Secret C2 command: whoami"

    ciphertext, nonce = aes.encrypt(plaintext)
    print(f"Plaintext: {plaintext.decode()}")
    print(f"Ciphertext (hex): {ciphertext.hex()[:64]}...")
    print(f"Nonce (hex): {nonce.hex()}")

    decrypted = aes.decrypt(ciphertext, nonce)
    print(f"Decrypted: {decrypted.decode()}")

    # Example 3: HTTP Covert Channel
    print("\n" + "=" * 50)
    print("Example 3: HTTP Covert Channel")
    print("=" * 50)

    async with HTTPChannel("https://example.com") as http:
        print("HTTP channel initialized")
        print(f"Base URL: {http.base_url}")
        print(f"SSL verification: {http.verify_ssl}")
        print(f"Domain fronting: {http.domain_front or 'Not configured'}")

    # Example 4: Plugin System
    print("\n" + "=" * 50)
    print("Example 4: Plugin System")
    print("=" * 50)

    loader = PluginLoader()
    plugins = loader.discover_plugins()

    print(f"Discovered plugins: {plugins}")

    if plugins:
        for plugin_name in plugins:
            try:
                plugin = loader.load_plugin(plugin_name)
                info = plugin.get_info()
                print(f"\nPlugin: {info['name']}")
                print(f"  Version: {info['version']}")
                print(f"  Description: {info['description']}")
                print(f"  Author: {info['author']}")
            except Exception as e:
                print(f"  Failed to load: {e}")

    print("\n" + "=" * 50)
    print("Examples completed!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())

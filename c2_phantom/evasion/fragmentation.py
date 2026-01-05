"""
Payload fragmentation for evasion.

Splits payloads into smaller chunks to evade detection.
"""

import hashlib
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class Fragment:
    """Represents a payload fragment."""

    sequence: int
    total_fragments: int
    data: bytes
    checksum: str


class PayloadFragmenter:
    """Fragments payloads for evasion."""

    def __init__(self, chunk_size: int = 1024, add_checksums: bool = True) -> None:
        """
        Initialize payload fragmenter.

        Args:
            chunk_size: Size of each fragment in bytes
            add_checksums: Add checksums for integrity verification
        """
        self.chunk_size = chunk_size
        self.add_checksums = add_checksums

    def fragment(self, payload: bytes) -> List[Fragment]:
        """
        Fragment a payload into chunks.

        Args:
            payload: Payload data to fragment

        Returns:
            List of Fragment objects
        """
        fragments = []
        total_size = len(payload)
        total_fragments = (total_size + self.chunk_size - 1) // self.chunk_size

        for i in range(total_fragments):
            start = i * self.chunk_size
            end = min(start + self.chunk_size, total_size)
            chunk = payload[start:end]

            # Calculate checksum
            checksum = ""
            if self.add_checksums:
                checksum = hashlib.sha256(chunk).hexdigest()

            fragment = Fragment(
                sequence=i,
                total_fragments=total_fragments,
                data=chunk,
                checksum=checksum,
            )

            fragments.append(fragment)

        return fragments

    def defragment(self, fragments: List[Fragment]) -> bytes:
        """
        Reassemble fragments into original payload.

        Args:
            fragments: List of Fragment objects

        Returns:
            Reassembled payload

        Raises:
            ValueError: If fragments are invalid or incomplete
        """
        if not fragments:
            raise ValueError("No fragments provided")

        # Sort by sequence number
        sorted_fragments = sorted(fragments, key=lambda f: f.sequence)

        # Verify sequence
        expected_total = sorted_fragments[0].total_fragments
        if len(sorted_fragments) != expected_total:
            raise ValueError(
                f"Incomplete fragments: expected {expected_total}, got {len(sorted_fragments)}"
            )

        # Verify checksums and reassemble
        payload_parts = []
        for i, fragment in enumerate(sorted_fragments):
            if fragment.sequence != i:
                raise ValueError(f"Missing fragment {i}")

            # Verify checksum
            if self.add_checksums and fragment.checksum:
                calculated = hashlib.sha256(fragment.data).hexdigest()
                if calculated != fragment.checksum:
                    raise ValueError(f"Checksum mismatch for fragment {i}")

            payload_parts.append(fragment.data)

        return b"".join(payload_parts)

    def fragment_with_padding(self, payload: bytes, padding_size: int = 16) -> List[Fragment]:
        """
        Fragment payload with random padding.

        Args:
            payload: Payload data
            padding_size: Size of padding to add

        Returns:
            List of fragments with padding
        """
        import os

        # Add padding
        padding = os.urandom(padding_size)
        padded_payload = payload + padding

        # Fragment
        fragments = self.fragment(padded_payload)

        # Store original size in first fragment metadata
        # (In real implementation, this would be encoded in the fragment)

        return fragments

    def calculate_overhead(self, payload_size: int) -> int:
        """
        Calculate fragmentation overhead.

        Args:
            payload_size: Original payload size

        Returns:
            Overhead in bytes
        """
        total_fragments = (payload_size + self.chunk_size - 1) // self.chunk_size

        # Each fragment has overhead for:
        # - Sequence number (4 bytes)
        # - Total fragments (4 bytes)
        # - Checksum (32 bytes for SHA-256 hex)
        overhead_per_fragment = 4 + 4 + 32

        return total_fragments * overhead_per_fragment

    def optimal_chunk_size(self, payload_size: int, max_overhead: int = 1024) -> int:
        """
        Calculate optimal chunk size based on overhead constraints.

        Args:
            payload_size: Payload size in bytes
            max_overhead: Maximum acceptable overhead

        Returns:
            Optimal chunk size
        """
        # Start with default chunk size
        chunk_size = self.chunk_size

        while True:
            total_fragments = (payload_size + chunk_size - 1) // chunk_size
            overhead = total_fragments * 40  # Approximate overhead

            if overhead <= max_overhead:
                return chunk_size

            # Increase chunk size
            chunk_size += 512

            # Don't exceed payload size
            if chunk_size >= payload_size:
                return payload_size

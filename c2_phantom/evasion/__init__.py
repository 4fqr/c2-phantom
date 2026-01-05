"""Evasion techniques for C2 Phantom."""

from c2_phantom.evasion.timing import TimingObfuscator
from c2_phantom.evasion.fragmentation import PayloadFragmenter

__all__ = ["TimingObfuscator", "PayloadFragmenter"]

"""Network protocol implementations for C2 Phantom."""

from c2_phantom.network.http import HTTPChannel
from c2_phantom.network.dns import DNSTunnel
from c2_phantom.network.websocket import WebSocketChannel
from c2_phantom.network.proxy import ProxyChain

__all__ = [
    "HTTPChannel",
    "DNSTunnel",
    "WebSocketChannel",
    "ProxyChain",
]

"""
Beautiful user interface utilities for C2 Phantom.

Provides rich console output with colors, formatting, and styling.
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
from typing import Optional

from c2_phantom import __version__

console = Console()


def print_banner() -> None:
    """Print the C2 Phantom banner."""
    banner_text = f"""
[bold cyan]  ██████╗██████╗     ██████╗ ██╗  ██╗ █████╗ ███╗   ██╗████████╗ ██████╗ ███╗   ███╗[/bold cyan]
[bold cyan] ██╔════╝╚════██╗    ██╔══██╗██║  ██║██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗████╗ ████║[/bold cyan]
[bold cyan] ██║      █████╔╝    ██████╔╝███████║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║[/bold cyan]
[bold cyan] ██║     ██╔═══╝     ██╔═══╝ ██╔══██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║[/bold cyan]
[bold cyan] ╚██████╗███████╗    ██║     ██║  ██║██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║[/bold cyan]
[bold cyan]  ╚═════╝╚══════╝    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝[/bold cyan]

[dim]                       Advanced C2 Framework for Red Team Training[/dim]
[dim]                                     Version {__version__}[/dim]

[bold yellow]⚠️  WARNING: For AUTHORIZED security testing only[/bold yellow]
[dim]                     Use responsibly and ethically[/dim]
"""
    console.print(banner_text)


def print_success(message: str) -> None:
    """
    Print a success message.

    Args:
        message: Success message to display
    """
    console.print(f"[bold green]✓[/bold green] {message}")


def print_error(message: str) -> None:
    """
    Print an error message.

    Args:
        message: Error message to display
    """
    console.print(f"[bold red]✗[/bold red] {message}", style="red")


def print_info(message: str) -> None:
    """
    Print an info message.

    Args:
        message: Info message to display
    """
    console.print(f"[bold blue]ℹ[/bold blue] {message}")


def print_warning(message: str) -> None:
    """
    Print a warning message.

    Args:
        message: Warning message to display
    """
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")


def create_panel(
    content: str,
    title: Optional[str] = None,
    border_style: str = "cyan",
    box_style: box.Box = box.ROUNDED,
) -> Panel:
    """
    Create a styled panel.

    Args:
        content: Panel content
        title: Optional panel title
        border_style: Border color style
        box_style: Box drawing style

    Returns:
        Rich Panel object
    """
    return Panel(
        content,
        title=title,
        border_style=border_style,
        box=box_style,
    )


def format_bytes(bytes_count: int) -> str:
    """
    Format bytes to human-readable string.

    Args:
        bytes_count: Number of bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_count < 1024.0:
            return f"{bytes_count:.2f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.2f} PB"


def format_duration(seconds: float) -> str:
    """
    Format seconds to human-readable duration.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string (e.g., "2h 30m 15s")
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def create_status_text(status: str) -> Text:
    """
    Create colored status text.

    Args:
        status: Status string

    Returns:
        Rich Text object with appropriate styling
    """
    status_lower = status.lower()

    if status_lower in ["active", "success", "connected"]:
        return Text(f"● {status}", style="bold green")
    elif status_lower in ["inactive", "failed", "error"]:
        return Text(f"● {status}", style="bold red")
    elif status_lower in ["connecting", "pending", "processing"]:
        return Text(f"● {status}", style="bold yellow")
    else:
        return Text(f"● {status}", style="bold blue")

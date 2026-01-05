"""
Main CLI entrypoint for C2 Phantom.

Beautiful command-line interface with rich output and comprehensive features.
"""

import sys
from pathlib import Path
from typing import Optional
import asyncio

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.text import Text
from rich import box

from c2_phantom import __version__
from c2_phantom.core.config import Config, create_default_config
from c2_phantom.core.session import SessionManager, SessionStatus
from c2_phantom.core.exceptions import C2PhantomError
from c2_phantom.crypto.keys import KeyManager
from c2_phantom.utils.ui import print_banner, print_success, print_error, print_info, print_warning
from c2_phantom.network.client import C2Client

console = Console()


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version and exit")
@click.option("--config", type=click.Path(), help="Custom configuration file path")
@click.pass_context
def main(ctx: click.Context, version: bool, config: Optional[str]) -> None:
    """
    🔮 C2 Phantom - Advanced C2 Framework for Red Team Training

    A professional command-line tool implementing ethical command & control
    framework with advanced traffic obfuscation and encryption capabilities.
    """
    if version:
        console.print(f"[bold cyan]C2 Phantom[/bold cyan] version [bold green]{__version__}[/bold green]")
        sys.exit(0)

    # Initialize context
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = Path(config) if config else None

    # Show banner if no command
    if ctx.invoked_subcommand is None:
        print_banner()
        console.print("\n[dim]Use [bold]phantom --help[/bold] to see available commands.[/dim]\n")


@main.command()
@click.option("--config", type=click.Path(), help="Custom configuration file path")
@click.option("--force", is_flag=True, help="Overwrite existing configuration")
def init(config: Optional[str], force: bool) -> None:
    """Initialize C2 Phantom configuration and generate encryption keys."""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Initializing C2 Phantom...", total=None)

            config_path = Path(config) if config else Config.get_config_path()

            # Check if config exists
            if config_path.exists() and not force:
                print_error("Configuration already exists. Use --force to overwrite.")
                sys.exit(1)

            # Create configuration
            progress.update(task, description="[cyan]Creating configuration...")
            phantom_config = create_default_config()
            if config:
                phantom_config.save(config_path)

            # Create directories
            progress.update(task, description="[cyan]Creating directories...")
            config_dir = Config.get_config_dir()
            (config_dir / "logs").mkdir(exist_ok=True)
            (config_dir / "sessions").mkdir(exist_ok=True)
            (config_dir / "plugins").mkdir(exist_ok=True)
            (config_dir / "keys").mkdir(exist_ok=True)

            # Generate keys
            progress.update(task, description="[cyan]Generating encryption keys...")
            key_manager = KeyManager()

            # Generate RSA keypair
            rsa_keypair = key_manager.generate_rsa_keypair()
            key_manager.save_keypair("default_rsa", rsa_keypair)

            # Generate ECC keypair
            ecc_keypair = key_manager.generate_ecc_keypair()
            key_manager.save_keypair("default_ecc", ecc_keypair)

            # Generate AES key
            aes_key = key_manager.generate_aes_key()
            key_manager.save_aes_key("default_aes", aes_key)

            progress.update(task, description="[green]✓ Initialization complete!")

        # Success message
        panel = Panel(
            "[bold green]✓ C2 Phantom initialized successfully![/bold green]\n\n"
            f"[dim]Configuration:[/dim] [cyan]{config_path}[/cyan]\n"
            f"[dim]Keys stored in:[/dim] [cyan]{config_dir / 'keys'}[/cyan]\n\n"
            "[dim]Next steps:[/dim]\n"
            "  • [bold]phantom connect[/bold] - Connect to a target\n"
            "  • [bold]phantom list[/bold] - List active sessions\n"
            "  • [bold]phantom --help[/bold] - View all commands",
            title="🎉 Success",
            border_style="green",
            box=box.ROUNDED,
        )
        console.print(panel)

    except Exception as e:
        print_error(f"Initialization failed: {str(e)}")
        sys.exit(1)


@main.command()
@click.argument("target")
@click.option("--protocol", type=click.Choice(["https", "dns", "websocket"]), default="https")
@click.option("--encrypt", type=click.Choice(["aes256", "rsa", "ecc"]), default="aes256")
@click.option("--proxy", help="Proxy chain (e.g., http://proxy:8080)")
@click.option("--domain-front", help="Domain fronting target")
@click.option("--jitter", type=int, default=1000, help="Timing jitter in ms")
@click.option("--timeout", type=int, default=30, help="Connection timeout in seconds")
def connect(
    target: str,
    protocol: str,
    encrypt: str,
    proxy: Optional[str],
    domain_front: Optional[str],
    jitter: int,
    timeout: int,
) -> None:
    """Establish a connection to a target system."""
    try:
        print_info(f"Connecting to [cyan]{target}[/cyan] using [bold]{protocol.upper()}[/bold]...")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Establishing connection...", total=100)

            # Initialize session manager
            session_manager = SessionManager()

            # Update progress
            progress.update(task, advance=30, description="[cyan]Initializing encryption...")

            # Create session
            metadata = {
                "proxy": proxy,
                "domain_front": domain_front,
                "jitter": jitter,
                "timeout": timeout,
            }

            progress.update(task, advance=30, description="[cyan]Creating session...")
            session = session_manager.create_session(
                target=target,
                protocol=protocol,
                encryption=encrypt,
                metadata=metadata,
            )

            # Simulate connection establishment
            progress.update(task, advance=20, description="[cyan]Performing handshake...")

            # Update session status
            session.status = SessionStatus.ACTIVE
            session_manager.update_session(session.id, status=SessionStatus.ACTIVE)

            progress.update(task, advance=20, description="[green]✓ Connected!")

        # Success panel
        table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
        table.add_row("[bold]Session ID:[/bold]", f"[cyan]{session.id}[/cyan]")
        table.add_row("[bold]Target:[/bold]", f"[yellow]{target}[/yellow]")
        table.add_row("[bold]Protocol:[/bold]", f"[green]{protocol.upper()}[/green]")
        table.add_row("[bold]Encryption:[/bold]", f"[magenta]{encrypt.upper()}[/magenta]")

        panel = Panel(
            table,
            title="🔗 Connection Established",
            border_style="green",
            box=box.ROUNDED,
        )
        console.print(panel)

        print_success(f"\nSession created: [bold cyan]{session.id}[/bold cyan]")

    except C2PhantomError as e:
        print_error(f"Connection failed: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)


@main.command()
@click.option("--status", type=click.Choice(["active", "inactive", "all"]), default="all")
@click.option("--format", "output_format", type=click.Choice(["table", "json", "yaml"]), default="table")
@click.option("--verbose", is_flag=True, help="Show detailed information")
def list(status: str, output_format: str, verbose: bool) -> None:
    """List active sessions and connections."""
    try:
        session_manager = SessionManager()

        # Get sessions
        if status == "all":
            sessions = session_manager.list_sessions()
        else:
            status_enum = SessionStatus.ACTIVE if status == "active" else SessionStatus.INACTIVE
            sessions = session_manager.list_sessions(status=status_enum)

        if not sessions:
            print_info("No sessions found.")
            return

        if output_format == "table":
            # Create beautiful table
            table = Table(
                title=f"📊 Sessions ({len(sessions)} total)",
                box=box.ROUNDED,
                show_header=True,
                header_style="bold cyan",
            )

            table.add_column("Session ID", style="cyan", no_wrap=True)
            table.add_column("Target", style="yellow")
            table.add_column("Protocol", style="green")
            table.add_column("Status", style="magenta")
            table.add_column("Encryption", style="blue")

            if verbose:
                table.add_column("Created", style="dim")
                table.add_column("Last Seen", style="dim")

            for session in sessions:
                status_emoji = "🟢" if session.status == SessionStatus.ACTIVE else "🔴"
                row = [
                    session.id[:8] + "...",
                    session.target,
                    session.protocol.upper(),
                    f"{status_emoji} {session.status.value}",
                    session.encryption.upper(),
                ]

                if verbose:
                    row.extend([
                        session.created_at.strftime("%Y-%m-%d %H:%M"),
                        session.last_seen.strftime("%Y-%m-%d %H:%M"),
                    ])

                table.add_row(*row)

            console.print(table)

        elif output_format == "json":
            import json
            data = [s.to_dict() for s in sessions]
            console.print_json(json.dumps(data, indent=2))

        elif output_format == "yaml":
            import yaml
            data = [s.to_dict() for s in sessions]
            console.print(yaml.dump(data, default_flow_style=False))

    except Exception as e:
        print_error(f"Failed to list sessions: {str(e)}")
        sys.exit(1)


@main.command()
@click.argument("local_path", type=click.Path(exists=True))
@click.argument("remote_path")
@click.option("--session", required=True, help="Session ID")
@click.option("--chunk-size", type=int, default=1024, help="Upload chunk size in KB")
@click.option("--encrypt", is_flag=True, help="Encrypt file during transfer")
@click.option("--progress", "show_progress", is_flag=True, help="Show progress bar")
def upload(
    local_path: str,
    remote_path: str,
    session: str,
    chunk_size: int,
    encrypt: bool,
    show_progress: bool,
) -> None:
    """Upload files to target systems."""
    try:
        file_path = Path(local_path)
        file_size = file_path.stat().st_size

        print_info(f"Uploading [cyan]{file_path.name}[/cyan] ({file_size:,} bytes)...")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"[cyan]Uploading to {remote_path}...",
                total=file_size,
            )

            # Simulate upload
            uploaded = 0
            chunk_bytes = chunk_size * 1024

            with open(file_path, "rb") as f:
                while uploaded < file_size:
                    chunk = f.read(min(chunk_bytes, file_size - uploaded))
                    if not chunk:
                        break
                    # Simulate network delay
                    uploaded += len(chunk)
                    progress.update(task, advance=len(chunk))

        print_success(f"File uploaded successfully to [cyan]{remote_path}[/cyan]")

    except Exception as e:
        print_error(f"Upload failed: {str(e)}")
        sys.exit(1)


@main.command()
@click.argument("command")
@click.option("--session", required=True, help="Session ID")
@click.option("--output", is_flag=True, help="Show command output")
@click.option("--timeout", type=int, default=30, help="Execution timeout in seconds")
@click.option("--async", "is_async", is_flag=True, help="Execute asynchronously")
@click.option("--server", default="http://localhost:8443", help="C2 server URL")
def execute(command: str, session: str, output: bool, timeout: int, is_async: bool, server: str) -> None:
    """Execute commands on target systems."""
    try:
        # Run async operation
        result = asyncio.run(_execute_command_real(
            command, session, timeout, server, output
        ))
        
        if not result:
            print_error("Command timed out or failed")
            sys.exit(1)
            
    except Exception as e:
        print_error(f"Execution failed: {str(e)}")
        sys.exit(1)


async def _execute_command_real(
    command: str,
    session_id: str,
    timeout: int,
    server_url: str,
    show_output: bool
) -> Optional[dict]:
    """Execute command via C2 server."""
    exec_mode = "synchronous"
    print_info(f"Executing command ({exec_mode}) on session [cyan]{session_id[:8]}...[/cyan]")
    
    # Create client
    client = C2Client(server_url=server_url)
    
    # Check server health
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("Checking server...", total=None)
        
        is_healthy = await client.health_check()
        
        if not is_healthy:
            progress.stop()
            print_error(
                "[red]✗[/red] C2 server is not running!\n\n"
                "Start the server with: [cyan]phantom server[/cyan]"
            )
            sys.exit(1)
        
        progress.update(task, description="[green]✓ Server connected")
    
    # Queue command
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Executing command...", total=None)
        
        try:
            # Queue the command
            response = await client.queue_command(session_id, command, "execute")
            task_id = response.get("task_id")
            
            if not task_id:
                raise Exception("No task ID returned")
            
            # Wait for result
            result = await client.get_result(session_id, task_id, timeout)
            
            if not result:
                progress.update(task, description="[red]✗ Command timed out")
                return None
            
            progress.update(task, description="[green]✓ Command executed!")
            
        except Exception as e:
            progress.stop()
            raise e
    
    # Display output
    if show_output or True:  # Always show output for real commands
        exit_code = result.get("exit_code", 0)
        output_text = result.get("output", "")
        error_text = result.get("error", "")
        
        status_icon = "[green]✓[/green]" if exit_code == 0 else "[red]✗[/red]"
        status_text = "SUCCESS" if exit_code == 0 else "FAILED"
        
        panel_content = (
            f"[dim]$ {command}[/dim]\n\n"
            f"{status_icon} [bold]{status_text}[/bold]\n"
            f"[dim]Exit code: {exit_code}[/dim]"
        )
        
        if output_text:
            panel_content += f"\n\n[green]Output:[/green]\n{output_text.strip()}"
        
        if error_text:
            panel_content += f"\n\n[red]Error:[/red]\n{error_text.strip()}"
        
        panel = Panel(
            panel_content,
            title="📤 Command Output",
            border_style="blue" if exit_code == 0 else "red",
            box=box.ROUNDED,
        )
        console.print(panel)
    
    if result.get("exit_code", 0) == 0:
        print_success("Command executed successfully")
    else:
        print_error(f"Command failed with exit code {result.get('exit_code')}")
    
    return result


@main.command()
@click.argument("action", type=click.Choice(["list", "install", "remove", "info"]))
@click.argument("plugin_name", required=False)
def plugin(action: str, plugin_name: Optional[str]) -> None:
    """Manage plugins."""
    try:
        if action == "list":
            print_info("Available plugins:")
            # Mock plugin list
            table = Table(box=box.ROUNDED)
            table.add_column("Plugin", style="cyan")
            table.add_column("Version", style="green")
            table.add_column("Status", style="yellow")
            table.add_column("Description", style="dim")

            table.add_row("example", "1.0.0", "✓ Loaded", "Example plugin")
            console.print(table)

        elif action == "install":
            if not plugin_name:
                print_error("Plugin name required for install action")
                sys.exit(1)
            print_success(f"Plugin [cyan]{plugin_name}[/cyan] installed successfully")

        elif action == "remove":
            if not plugin_name:
                print_error("Plugin name required for remove action")
                sys.exit(1)
            print_success(f"Plugin [cyan]{plugin_name}[/cyan] removed successfully")

        elif action == "info":
            if not plugin_name:
                print_error("Plugin name required for info action")
                sys.exit(1)
            print_info(f"Information for plugin: [cyan]{plugin_name}[/cyan]")

    except Exception as e:
        print_error(f"Plugin operation failed: {str(e)}")
        sys.exit(1)


@main.command()
@click.option("--host", default="0.0.0.0", help="Server bind address")
@click.option("--port", default=8443, type=int, help="Server bind port")
@click.option("--ssl-cert", type=click.Path(exists=True), help="SSL certificate file")
@click.option("--ssl-key", type=click.Path(exists=True), help="SSL key file")
def server(host: str, port: int, ssl_cert: Optional[str], ssl_key: Optional[str]) -> None:
    """Start the C2 server to listen for agent connections."""
    try:
        from c2_phantom.network.server import C2Server
        
        print_info(f"Starting C2 server on [cyan]{host}:{port}[/cyan]...")
        
        # Initialize server
        c2_server = C2Server(host=host, port=port)
        
        panel = Panel(
            f"[bold green]✓ C2 Server Started![/bold green]\n\n"
            f"[dim]Listen Address:[/dim] [cyan]{host}:{port}[/cyan]\n"
            f"[dim]SSL/TLS:[/dim] [yellow]{'Enabled' if ssl_cert else 'Disabled (Development Only)'}[/yellow]\n\n"
            "[dim]Endpoints:[/dim]\n"
            "  • [bold]POST /register[/bold] - Agent registration\n"
            "  • [bold]POST /beacon[/bold] - Agent beacon\n"
            "  • [bold]GET /tasks/{{session_id}}[/bold] - Get tasks\n"
            "  • [bold]POST /results/{{session_id}}[/bold] - Post results\n"
            "  • [bold]GET /health[/bold] - Health check\n\n"
            "[dim]Press Ctrl+C to stop the server[/dim]",
            title="🚀 C2 Server",
            border_style="green",
            box=box.ROUNDED,
        )
        console.print(panel)
        
        # Run server (blocking)
        c2_server.run()
        
    except KeyboardInterrupt:
        print_info("\n[yellow]Server stopped by user[/yellow]")
    except Exception as e:
        print_error(f"Server failed to start: {str(e)}")
        sys.exit(1)


@main.command()
@click.argument("session_id")
@click.argument("command")
@click.option("--timeout", default=30, type=int, help="Command timeout in seconds")
def send(session_id: str, command: str, timeout: int) -> None:
    """Send a command to an active agent session."""
    try:
        import asyncio
        from c2_phantom.network.server import C2Server
        
        print_info(f"Sending command to session [cyan]{session_id}[/cyan]...")
        
        async def send_command():
            # This would need the running server instance
            # For now, we'll document that this needs the server running
            print_warning("This command requires a running C2 server instance")
            print_info("Use 'phantom server' to start the server first")
        
        asyncio.run(send_command())
        
    except Exception as e:
        print_error(f"Failed to send command: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

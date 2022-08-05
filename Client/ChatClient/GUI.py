from datetime import datetime
import socket
import keyboard
from rich.align import Align
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich import box


def chat_layout() -> Layout:
    """Creates a layout to chat."""
    layout = Layout(name="root")

    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3),
    )
    layout["main"].split_row(
        Layout(name="chat_body", ratio=4, minimum_size=60),
        Layout(name="side")
    )
    return layout


class Header:
    """Display header with clock."""

    def __rich__(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="right", ratio=1)
        grid.add_row(
            "Chat Client by Alicino",
            socket.gethostname(),
            datetime.now().ctime().replace(":", "[blink]:[/]")
        )
        return Panel(grid, style="white")


def messages_panel(message: str, ip_connected: str) -> Panel:
    """Creates the message panel."""
    message_panel = Panel(
        Align.left(
            message,
            vertical="bottom",
        ),
        box=box.ROUNDED,
        title=f"[b blue]Connected with {ip_connected}",
        border_style="bright_blue",
    )
    return message_panel


def messages_panel_helper() -> Panel:
    """Creates the message panel."""
    message_panel = Panel(
        Align.center(
            f"To connect to another user type: /connectwith <username>\n"
            f"For more commands type /help",
            vertical="middle",
        ),
        box=box.ROUNDED,
        title=f"[b blue]Connected with No One",
        border_style="bright_blue",
    )
    return message_panel


def active_users_panel(users: str) -> Panel:
    """Creates the active users panel."""
    message_panel = Panel(
        Align.right(
            users,
            vertical="top",
        ),
        box=box.ROUNDED,
        padding=(1, 2),
        title="[b green]Users available",
        border_style="white",
    )
    return message_panel


def input_section(buffer: str) -> Panel:
    input_table = Table.grid(expand=True)
    input_table.add_column(justify="left", ratio=1)
    input_table.add_column(justify="right", ratio=1)
    input_table.add_row(
        f">> {buffer}",
        f"Enter to Send"
    )
    input_box = Panel(
        input_table,
        box=box.ROUNDED,
        border_style="blue",
    )
    return input_box

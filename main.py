"""
AI-Powered Social Media Responder — CLI entry point.

Usage:
    python main.py              # interactive mode
    python main.py --demo       # run built-in demo messages
    python main.py --log        # print last 10 logged responses
"""

import argparse
import json
import os
import sys
from datetime import datetime

import anthropic
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
from rich import box

from config import PLATFORMS, RESPONSE_LOG
from responder import IncomingMessage, ResponseResult, process_message

console = Console()


# ── Banner ────────────────────────────────────────────────────────────────────

def print_banner():
    console.print(Panel(
        Text.assemble(
            ("  Social Media Responder\n", "bold cyan"),
            ("  Powered by Claude AI  |  ", "dim"),
            ("Reageert in het Nederlands", "bold white"),
        ),
        border_style="cyan",
        padding=(0, 2),
    ))


# ── Display helpers ───────────────────────────────────────────────────────────

def display_result(result: ResponseResult):
    is_escalation = result.status == ResponseResult.ESCALATE

    # Header
    status_text = (
        "[bold red]!! ESCALATE TO HUMAN[/bold red]"
        if is_escalation
        else "[bold green]OK AUTO-RESPONSE[/bold green]"
    )
    border = "red" if is_escalation else "green"

    msg = result.message
    console.print(f"\n  {status_text}")
    console.print(f"  [dim]Platform:[/dim] {msg.platform}  |  "
                  f"[dim]Afzender:[/dim] {msg.sender}  |  "
                  f"[dim]{msg.timestamp[:19]}[/dim]")

    # Original message
    console.print(Panel(
        f"[italic]{msg.text}[/italic]",
        title="Binnenkomend bericht",
        border_style="dim",
        padding=(0, 1),
    ))

    # Response / escalation notice
    console.print(Panel(
        result.reply,
        title="Antwoord" if not is_escalation else "Escalatie",
        border_style=border,
        padding=(0, 1),
    ))


# ── Demo mode ─────────────────────────────────────────────────────────────────

DEMO_MESSAGES = [
    ("Facebook",   "Marie Janssen",    "Hoe lang duurt de levering naar Gent?"),
    ("Instagram",  "@pietervdb",       "Kan ik betalen met Bancontact?"),
    ("WhatsApp",   "+32 498 12 34 56", "Ik heb een klacht over mijn bestelling, dit is onacceptabel!"),
    ("Facebook",   "Thomas De Backer", "Wanneer is mijn pakje er? Ik heb de trackingcode niet ontvangen."),
    ("WhatsApp",   "+32 471 98 76 54", "Dit is dringend! Ik wil juridisch advies inwinnen over mijn bestelling."),
    ("Instagram",  "@nathalie.moons",  "Hoeveel jaar garantie zit er op de koelkast?"),
]


def run_demo(client: anthropic.Anthropic):
    console.print("\n[bold yellow]Demo-modus — verwerken van voorbeeldberichten...[/bold yellow]\n")
    for platform, sender, text in DEMO_MESSAGES:
        msg = IncomingMessage(platform=platform, sender=sender, text=text)
        result = process_message(msg, client)
        display_result(result)


# ── Log viewer ────────────────────────────────────────────────────────────────

def show_log(n: int = 10):
    if not RESPONSE_LOG.exists():
        console.print("[yellow]Nog geen logbestand gevonden.[/yellow]")
        return

    data = json.loads(RESPONSE_LOG.read_text(encoding="utf-8"))
    recent = data[-n:]

    table = Table(
        title=f"Laatste {len(recent)} berichten",
        box=box.ROUNDED,
        border_style="cyan",
        show_lines=True,
    )
    table.add_column("Tijdstip",  style="dim",        no_wrap=True)
    table.add_column("Platform",  style="cyan",       no_wrap=True)
    table.add_column("Afzender",  style="white",      no_wrap=True)
    table.add_column("Status",    style="bold",       no_wrap=True)
    table.add_column("Bericht",   style="italic",     max_width=40)
    table.add_column("Antwoord",  max_width=50)

    for entry in recent:
        msg    = entry["message"]
        status = entry["status"]
        color  = "red" if status == "ESCALATE" else "green"
        table.add_row(
            msg["timestamp"][:19],
            msg["platform"],
            msg["sender"],
            f"[{color}]{status}[/{color}]",
            msg["text"][:80],
            entry["reply"][:120],
        )

    console.print(table)


# ── Interactive mode ──────────────────────────────────────────────────────────

def interactive_mode(client: anthropic.Anthropic):
    console.print("\n[bold]Interactieve modus[/bold] — typ [cyan]q[/cyan] om te stoppen\n")

    while True:
        # Choose platform
        platform_str = ", ".join(f"[cyan]{i+1}[/cyan] {p}" for i, p in enumerate(PLATFORMS))
        console.print(f"Platform: {platform_str}")
        choice = Prompt.ask("Keuze", default="1")
        if choice.lower() in ("q", "quit"):
            break
        try:
            platform = PLATFORMS[int(choice) - 1]
        except (ValueError, IndexError):
            platform = PLATFORMS[0]

        sender = Prompt.ask("Naam afzender")
        if sender.lower() in ("q", "quit"):
            break

        text = Prompt.ask("Bericht")
        if text.lower() in ("q", "quit"):
            break

        msg    = IncomingMessage(platform=platform, sender=sender, text=text)
        result = process_message(msg, client)
        display_result(result)

        console.print()


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AI Social Media Responder — reageert automatisch in het Nederlands",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--demo", action="store_true", help="Verwerk demo-berichten")
    parser.add_argument("--log",  action="store_true", help="Toon laatste 10 log-items")
    args = parser.parse_args()

    print_banner()

    # ── API key check ─────────────────────────────────────────────────────────
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        console.print(Panel(
            "[red]ANTHROPIC_API_KEY niet ingesteld.[/red]\n\n"
            "Stel de variabele in:\n"
            "  [cyan]$env:ANTHROPIC_API_KEY = 'sk-ant-...'[/cyan]  (PowerShell)\n"
            "  [cyan]export ANTHROPIC_API_KEY=sk-ant-...[/cyan]     (Linux/macOS)",
            title="Ontbrekende API-sleutel",
            border_style="red",
        ))
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    if args.log:
        show_log()
    elif args.demo:
        run_demo(client)
    else:
        interactive_mode(client)


if __name__ == "__main__":
    main()

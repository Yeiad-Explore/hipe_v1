"""Main CLI interface for the Q&A Agent."""
import sys
import argparse
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from loguru import logger

from utils.logger import setup_logger
from graph.workflow import QAAgent


def print_result(result: dict, console: Console):
    """
    Pretty print the query result.

    Args:
        result: Query result dictionary
        console: Rich console
    """
    # Answer section
    console.print("\n")
    console.print(
        Panel(
            Markdown(result["answer"]),
            title="[bold cyan]Answer[/bold cyan]",
            border_style="cyan",
        )
    )

    # Confidence and metadata
    confidence_color = "green" if result["confidence"] > 0.7 else "yellow" if result["confidence"] > 0.4 else "red"
    console.print(
        f"\n[bold]Confidence:[/bold] [{confidence_color}]{result['confidence']:.2%}[/{confidence_color}] | "
        f"[bold]Consensus:[/bold] {result['consensus_level']} | "
        f"[bold]Time:[/bold] {result['processing_time']}s"
    )

    # Perspectives
    if result.get("perspectives"):
        console.print("\n[bold cyan]Perspectives:[/bold cyan]")
        for key, value in result["perspectives"].items():
            console.print(f"  [bold]{key.title()}:[/bold] {value}")

    # Sources table
    if result.get("sources"):
        console.print("\n[bold cyan]Sources:[/bold cyan]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Platform", style="dim", width=10)
        table.add_column("Author", width=20)
        table.add_column("URL", width=50)
        table.add_column("Credibility", justify="right", width=10)

        for source in result["sources"][:10]:  # Show top 10 sources
            table.add_row(
                source["platform"].upper(),
                source["author"],
                source["url"][:47] + "..." if len(source["url"]) > 50 else source["url"],
                f"{source['credibility_score']:.2f}",
            )

        console.print(table)

    # Metadata
    if result.get("metadata"):
        metadata = result["metadata"]
        console.print(f"\n[dim]Sources used: {metadata.get('num_sources', 0)} | "
                      f"Platforms: {metadata.get('platforms', {})}[/dim]")


def interactive_mode(agent: QAAgent, console: Console):
    """
    Interactive CLI mode.

    Args:
        agent: QAAgent instance
        console: Rich console
    """
    console.print(Panel(
        "[bold cyan]AI Q&A Agent[/bold cyan]\n"
        "Ask questions and get answers from X and Reddit.\n"
        "Type 'exit' or 'quit' to exit.",
        border_style="cyan",
    ))

    while True:
        try:
            console.print("\n[bold yellow]Your question:[/bold yellow] ", end="")
            query = input().strip()

            if query.lower() in ["exit", "quit", "q"]:
                console.print("\n[cyan]Goodbye![/cyan]")
                break

            if not query:
                continue

            console.print("\n[dim]Processing... (this may take 10-30 seconds)[/dim]")

            # Execute query
            result = agent.query(query)

            # Print result
            print_result(result, console)

        except KeyboardInterrupt:
            console.print("\n\n[cyan]Goodbye![/cyan]")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            logger.error(f"Error in interactive mode: {e}")


def single_query_mode(agent: QAAgent, query: str, console: Console):
    """
    Single query mode.

    Args:
        agent: QAAgent instance
        query: Query string
        console: Rich console
    """
    console.print(f"\n[bold yellow]Question:[/bold yellow] {query}")
    console.print("[dim]Processing...[/dim]")

    result = agent.query(query)
    print_result(result, console)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI Q&A Agent - Search X and Reddit for answers"
    )
    parser.add_argument(
        "query",
        nargs="*",
        help="Question to ask (if not provided, enters interactive mode)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logger(args.log_level)

    # Initialize console
    console = Console()

    try:
        # Initialize agent
        console.print("[dim]Initializing agent...[/dim]")
        agent = QAAgent()
        console.print("[green]✓ Agent ready[/green]")

        # Determine mode
        if args.query:
            # Single query mode
            query = " ".join(args.query)
            single_query_mode(agent, query, console)
        else:
            # Interactive mode
            interactive_mode(agent, console)

    except KeyboardInterrupt:
        console.print("\n[cyan]Interrupted by user[/cyan]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Fatal error: {e}[/red]")
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

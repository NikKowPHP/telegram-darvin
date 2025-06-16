# src/code_context_tool/cli.py
import argparse
import json
import sys
from pathlib import Path

import qdrant_client

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from .core import VectorDB

def main():
    """The main entry point for the command-line interface."""
    console = Console()

    parser = argparse.ArgumentParser(
        description="A portable tool for creating and querying a vector database of a codebase.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # --- 'init' command ---
    init_parser = subparsers.add_parser(
        'init',
        help='Initialize a new project with a default .cct_config.json file.'
    )

    # --- 'index' command ---
    index_parser = subparsers.add_parser(
        'index',
        help='Perform a full scan and indexing of the current project directory.'
    )
    index_parser.add_argument(
        '--dir',
        type=str,
        default='.',
        help='The root directory to index (default: current directory).'
    )

    # --- 'update' command ---
    update_parser = subparsers.add_parser(
        'update',
        help='Update the vectors for one or more specific files.'
    )
    update_parser.add_argument(
        'files',
        nargs='+',
        help='The path(s) to the file(s) to update.'
    )

    # --- 'query' command ---
    query_parser = subparsers.add_parser(
        'query',
        help='Query the codebase with a natural language text search.'
    )
    query_parser.add_argument(
        'query_text',
        help='The natural language query to search for.'
    )
    query_parser.add_argument(
        '--limit',
        type=int,
        default=5,
        help='Number of results to return (default: 5).'
    )

    args = parser.parse_args()
    
    try:
        if args.command == 'init':
            config_path = Path(".cct_config.json")
            if config_path.exists():
                console.print(f"[yellow]Warning:[/] [cyan]{config_path.name}[/cyan] already exists in this directory.")
                overwrite = input("Do you want to overwrite it? (y/N): ")
                if overwrite.lower() != 'y':
                    console.print("Initialization cancelled.")
                    sys.exit(0)
            
            default_config_content = {
                "qdrant_url": "http://localhost:6333",
                "model_name": "BAAI/bge-large-en-v1.5",
                "collection_name_prefix": "cct",
                "ignore_list": [
                    ".git", "node_modules", ".vscode", "dist", "build", ".DS_Store",
                    "__pycache__", "*.pyc", "*.egg-info", "venv", ".venv", "target",
                    "package-lock.json", "yarn.lock", "poetry.lock",
                    "repomix-output.xml", "*.log"
                ]
            }
            with open(config_path, 'w') as f:
                json.dump(default_config_content, f, indent=4)
            console.print(f"[green]✅ Successfully created default [cyan]{config_path.name}[/cyan] file.[/green]")

        else:
            # For all other commands, we need to connect to the VectorDB
            db = VectorDB()

            if args.command == 'index':
                db.index_project(args.dir)
            
            elif args.command == 'update':
                for file_path in args.files:
                    db.update_file(file_path)
                console.print(f"[green]✅ Update process completed for {len(args.files)} file(s).[/green]")

            elif args.command == 'query':
                results = db.query(args.query_text, args.limit)
                if not results:
                    console.print("[yellow]No relevant code chunks found for your query.[/yellow]")
                    sys.exit(0)
                
                console.print(Panel(f"Top {len(results)} results for: '[bold magenta]{args.query_text}[/bold magenta]'", expand=False))
                
                for i, hit in enumerate(results):
                    panel_title = f"[bold]Result {i+1} | Score: {hit['score']:.4f} | Path: [cyan]{hit['file_path']}[/cyan]:{hit['start_line']}[/bold]"
                    
                    # Try to determine the lexer for syntax highlighting
                    lexer_name = "python" # default
                    file_ext = Path(hit['file_path']).suffix
                    if file_ext == ".js": lexer_name = "javascript"
                    elif file_ext == ".ts": lexer_name = "typescript"
                    elif file_ext == ".md": lexer_name = "markdown"
                    elif file_ext in [".yml", ".yaml"]: lexer_name = "yaml"

                    code_snippet = Syntax(
                        hit['code_chunk'],
                        lexer_name,
                        theme="monokai",
                        line_numbers=True,
                        start_line=hit['start_line']
                    )
                    console.print(Panel(code_snippet, title=panel_title, border_style="blue"))

    except qdrant_client.http.exceptions.ResponseHandlingException as e:
        console.print(f"[bold red]Qdrant Error:[/bold red] Could not connect to Qdrant at the configured URL.")
        console.print(f"Please ensure the Qdrant Docker container is running and accessible.")
        console.print(f"Error details: {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
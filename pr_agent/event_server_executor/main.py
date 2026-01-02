"""
Main module for Event Server Executor.

This module provides functionality to run the Event Server Executor.
"""

import argparse
import asyncio
import os
import threading
from typing import Optional

from pr_agent.log import get_logger
from pr_agent.event_server_executor.db.manager import DatabaseManager
from pr_agent.event_server_executor.server.event_server import create_server, run_server
from pr_agent.event_server_executor.dashboard.app import create_dashboard, run_dashboard


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Event Server Executor")
    parser.add_argument(
        "--server-only",
        action="store_true",
        help="Run only the server",
    )
    parser.add_argument(
        "--dashboard-only",
        action="store_true",
        help="Run only the dashboard",
    )
    parser.add_argument(
        "--server-port",
        type=int,
        default=int(os.environ.get("PORT", "3000")),
        help="Port to run the server on",
    )
    parser.add_argument(
        "--dashboard-port",
        type=int,
        default=int(os.environ.get("DASHBOARD_PORT", "7860")),
        help="Port to run the dashboard on",
    )
    parser.add_argument(
        "--db-type",
        type=str,
        default=os.environ.get("EVENT_DB_TYPE", "sqlite"),
        choices=["sqlite", "supabase"],
        help="Database type to use",
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default=os.environ.get("EVENT_DB_PATH", "events.db"),
        help="Path to the SQLite database file",
    )
    
    return parser.parse_args()


def run_server_thread(port: int, db_manager: Optional[DatabaseManager] = None):
    """Run the server in a separate thread.
    
    Args:
        port: The port to run the server on.
        db_manager: The database manager to use. If None, a new one will be created.
    """
    os.environ["PORT"] = str(port)
    if db_manager:
        server = create_server()
        server.db_manager = db_manager
        server.run(port=port)
    else:
        run_server()


def run_dashboard_thread(port: int, db_manager: Optional[DatabaseManager] = None):
    """Run the dashboard in a separate thread.
    
    Args:
        port: The port to run the dashboard on.
        db_manager: The database manager to use. If None, a new one will be created.
    """
    os.environ["DASHBOARD_PORT"] = str(port)
    if db_manager:
        dashboard = create_dashboard()
        dashboard.db_manager = db_manager
        dashboard.run(port=port)
    else:
        run_dashboard()


def main():
    """Run the Event Server Executor."""
    args = parse_args()
    
    # Set environment variables
    os.environ["EVENT_DB_TYPE"] = args.db_type
    os.environ["EVENT_DB_PATH"] = args.db_path
    os.environ["PORT"] = str(args.server_port)
    os.environ["DASHBOARD_PORT"] = str(args.dashboard_port)
    
    # Create a shared database manager
    db_manager = DatabaseManager(db_type=args.db_type)
    
    # Run the server and dashboard
    if args.server_only:
        run_server_thread(args.server_port, db_manager)
    elif args.dashboard_only:
        run_dashboard_thread(args.dashboard_port, db_manager)
    else:
        # Run both the server and dashboard in separate threads
        server_thread = threading.Thread(
            target=run_server_thread,
            args=(args.server_port, db_manager),
            daemon=True,
        )
        server_thread.start()
        
        # Run the dashboard in the main thread
        run_dashboard_thread(args.dashboard_port, db_manager)


if __name__ == "__main__":
    main()

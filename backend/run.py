#!/usr/bin/env python3
"""
Run the Airfeeld API server.

Usage:
    python run.py [--host HOST] [--port PORT] [--reload]

Options:
    --host HOST    Bind to host (default: 127.0.0.1)
    --port PORT    Bind to port (default: 8000)
    --reload       Enable auto-reload for development
"""

import argparse
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main() -> None:
    """Run the server."""
    parser = argparse.ArgumentParser(description="Run Airfeeld API server")
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development",
    )
    
    args = parser.parse_args()
    
    # Import uvicorn here to avoid import errors if not installed
    try:
        import uvicorn
    except ImportError:
        print("Error: uvicorn not installed. Run: pip install uvicorn")
        sys.exit(1)
    
    print(f"Starting Airfeeld API on http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop")
    
    uvicorn.run(
        "src.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()

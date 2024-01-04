import argparse
import asyncio

from server import __version__
from server.handler import RequestHandler


def cli_args():
    parser = argparse.ArgumentParser(
        description="chatter-py:A simple chat server written in Python using asyncio and tcp sockets."
    )

    # Add version argument
    parser.add_argument(
        "--version", "-v", action="version", version=f"%(prog)s v{__version__}"
    )

    # Add ports argument
    parser.add_argument(
        "--port", "-p", type=int, default=8081, help="Port to run the server on"
    )

    # Number of recent messages to store
    parser.add_argument(
        "--history",
        "-n",
        type=int,
        default=10,
        help="Number of recent messages to store",
    )

    args = parser.parse_args()
    return args


def main():
    async def run_server(port: int, callback):
        srv = await asyncio.start_server(callback, "0.0.0.0", port)
        async with srv:
            await srv.serve_forever()

    args = cli_args()

    try:
        handler = RequestHandler(args.history)
        asyncio.run(run_server(args.port, handler.callback))

    except KeyboardInterrupt:
        print("Server stopped")


if __name__ == "__main__":
    main()

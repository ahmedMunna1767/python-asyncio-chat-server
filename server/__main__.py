import argparse
import asyncio

from server import __version__
from server.handler import tcp_request_handler


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

    args = parser.parse_args()
    return args


def main():
    async def run_server(port: int):
        srv = await asyncio.start_server(tcp_request_handler, "0.0.0.0", port)
        async with srv:
            await srv.serve_forever()

    args = cli_args()

    try:
        asyncio.run(run_server(args.port))

    except KeyboardInterrupt:
        print("Server stopped")


if __name__ == "__main__":
    main()

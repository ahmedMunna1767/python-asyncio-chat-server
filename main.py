import asyncio

from client_map import client_addr_map
from handler_utils import client_setup, handle_message
from stream_utils import StreamUtils, ctx_client_id


async def tcp_request_handler(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter
):
    # Set up a new client connection and get a unique ID / Name for the client
    client_id = await client_setup(reader, writer)
    if client_id is None:
        return

    # Continuously handle messages from the client until the connection is closed
    while True:
        # Receive a message from the client
        msg = await StreamUtils.recv(reader)

        # Handle the message and check if the connection should be closed
        shouldClose = await handle_message(writer, msg)

        # If the connection should be closed, break out of the loop
        if shouldClose:
            break

    # Close the connection
    writer.close()


async def main():
    srv = await asyncio.start_server(tcp_request_handler, "0.0.0.0", 8081)
    async with srv:
        await srv.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())

import asyncio

from client_map import client_addr_map
from utils import StreamUtils, ctx_client_id, handle_message


async def client_setup(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    await StreamUtils.render_hello(writer)
    await StreamUtils.send(writer, "Enter your name(should be unique): ", False)

    try:
        client_id = await StreamUtils.recv(reader)
        await client_addr_map.set(client_id, writer)
        ctx_client_id.set(client_id)
        await StreamUtils.send(writer, f"Welcome, '{client_id}'")
        return client_id

    except ValueError as e:
        print(e)
        await StreamUtils.send(writer, "Sorry, the name is already taken")
        await StreamUtils.render_goodbye(writer)
        return None


async def handle_request(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    client_id = await client_setup(reader, writer)
    if client_id is None:
        return

    while True:
        msg = await StreamUtils.recv(reader)
        shouldClose = await handle_message(writer, msg)
        if shouldClose:
            break

    writer.close()


async def main():
    srv = await asyncio.start_server(handle_request, "0.0.0.0", 8081)
    async with srv:
        await srv.serve_forever()


asyncio.run(main())

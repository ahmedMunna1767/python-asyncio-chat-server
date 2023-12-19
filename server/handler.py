import asyncio

from server.stores import recent_messages_store, writers_store
from server.utils import generate_random_code


async def tcp_request_handler(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter
):
    writer.write("Hello from py-chatter 🤩. Please Enter your name: ".encode())
    await writer.drain()

    name = (await reader.read(100)).decode().strip()
    id = name + "-" + generate_random_code()
    print(f"New client connected with id: {id}")

    await writers_store.add_writer(writer)
    await recent_messages_store.send_recent_messages(writer)

    while True:
        message = (await reader.readline()).decode().strip()
        if message == "":
            continue

        print(f"New message from {id}: {message}")

        if message == "exit":
            break

        await recent_messages_store.add_message(f"{id}: {message}")
        await writers_store.broadcast(f"{id}: {message}")

    await writers_store.remove_writer(writer)
    writer.close()
    print(f"Client {id} disconnected")

import asyncio

from server.stores import RecentMessagesStore, StreamWriterStore
from server.utils import generate_random_code


class RequestHandler:
    def __init__(self, history: int):
        self.writers_store = StreamWriterStore()
        self.recent_messages_store = RecentMessagesStore(history)

    async def callback(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        writer.write("Hello from py-chatter 🤩. Please Enter your name: ".encode())
        await writer.drain()

        name = (await reader.read(100)).decode().strip()
        id = name + "-" + generate_random_code()
        print(f"New client connected with id: {id}")

        await self.writers_store.add_writer(writer)
        await self.recent_messages_store.send_recent_messages(writer)

        while True:
            message = (await reader.readline()).decode().strip()
            if message == "":
                continue

            print(f"New message from {id}: {message}")

            if message == "exit":
                break

            await self.recent_messages_store.add_message(f"{id}: {message}")
            await self.writers_store.broadcast(f"{id}: {message}")

        await self.writers_store.remove_writer(writer)
        writer.close()
        print(f"Client {id} disconnected")

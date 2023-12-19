import asyncio


class StreamWriterStore:
    def __init__(self):
        self.stream_writers: list[asyncio.StreamWriter] = []
        self.lock = asyncio.Lock()

    async def add_writer(self, writer: asyncio.StreamWriter):
        async with self.lock:
            self.stream_writers.append(writer)

    async def remove_writer(self, writer: asyncio.StreamWriter):
        async with self.lock:
            self.stream_writers.remove(writer)

    async def broadcast(self, message: str):
        async with self.lock:
            for sw in self.stream_writers:
                sw.write(f"{message}\n".encode())
                await sw.drain()


class RecentMessagesStore:
    def __init__(self, max_messages=10):
        self.recent_messages: list[str] = []
        self.lock = asyncio.Lock()
        self.max_messages = max_messages

    async def add_message(self, message: str):
        async with self.lock:
            self.recent_messages.append(message)
            if len(self.recent_messages) > self.max_messages:
                self.recent_messages.pop(0)

    async def send_recent_messages(self, writer):
        async with self.lock:
            for message in self.recent_messages:
                writer.write(f"{message}\n".encode())
                await writer.drain()


writers_store = StreamWriterStore()
recent_messages_store = RecentMessagesStore()

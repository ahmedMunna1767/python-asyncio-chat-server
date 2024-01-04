import asyncio
import curses


class ChatCLient:
    def __init__(self, addr: str, port: int) -> None:
        self.addr = addr
        self.port = port

        self.queue = asyncio.Queue()

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.addr, self.port)
        self.welcome_message = await self.reader.read(100)

        name = input(self.welcome_message.decode())
        self.writer.write(name.encode())
        await self.writer.drain()

    def create_chat_window(self, stdscr):
        stdscr.clear()

        self.input_height, self.chat_height = 1, curses.LINES - 2
        self.chat_window = curses.newwin(self.chat_height, curses.COLS, 0, 0)
        self.input_window = curses.newwin(
            self.input_height, curses.COLS, self.chat_height, 0
        )
        # self.chat_window.scrollok(True)

    async def load_history(self):
        num_messages = int((await self.reader.readline()).decode())
        for _ in range(num_messages):
            message = (await self.reader.readline()).decode().strip()
            await self.queue.put(message)

    def print_msg(self, message):
        self.chat_window.scroll()
        self.chat_window.addstr(self.chat_height - 1, 0, message)
        self.chat_window.refresh()

    async def recv_message(self):
        while True:
            message = (await self.reader.readline()).decode().strip()
            await self.queue.put(message)

    async def update_chat(self):
        while True:
            message = await self.queue.get()
            self.print_msg(message)

    async def send_messages(self):
        # curses.echo()
        while True:
            self.input_window.refresh()
            self.input_window.addstr(0, 0, "> ")
            message = self.input_window.getstr(0, 2).decode()
            self.input_window.clear()

            self.writer.write(f"{message}\n".encode())
            await self.writer.drain()
            await asyncio.sleep(0.1)

    async def run(self, stdscr):
        await self.connect()
        self.create_chat_window(stdscr)
        await self.load_history()

        # Create tasks for each coroutine
        recv_task = asyncio.create_task(self.recv_message())
        send_task = asyncio.create_task(self.send_messages())
        update_task = asyncio.create_task(self.update_chat())

        # Use asyncio.gather to run the tasks concurrently
        await asyncio.gather(recv_task, send_task, update_task)


def main():
    client = ChatCLient("localhost", 8081)
    asyncio.run(curses.wrapper(client.run))


if __name__ == "__main__":
    main()

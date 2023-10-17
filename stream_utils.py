from asyncio import StreamReader, StreamWriter
from contextvars import ContextVar

from client_map import client_addr_map

ctx_client_id = ContextVar("client_id", default="X")
"""A ContextVar object used to store the ID of the client that is currently being handled by the server."""


class StreamUtils:
    @staticmethod
    async def send(writer: StreamWriter, data: str, new_line=True) -> None:
        """
        Sends the given data to the provided StreamWriter.

        Args:
        - writer: An instance of asyncio.StreamWriter.
        - data: A string containing the data to be sent.
        - new_line: A boolean indicating whether to append a newline character to the end of the data.

        Returns:
        - None
        """
        msg = data.encode("utf-8") + b"\n" if new_line else data.encode("utf-8")
        writer.write(msg)
        await writer.drain()

    @staticmethod
    async def recv(reader: StreamReader) -> str:
        """
        Receives data from the provided StreamReader.

        Args:
        - reader: An instance of asyncio.StreamReader.

        Returns:
        - A string containing the received data.
        """
        inp_bytes = await reader.readline()
        return inp_bytes.decode("utf-8").strip()

    @staticmethod
    async def render_hello(writer: StreamWriter) -> None:
        """
        Renders a hello message to the provided StreamWriter.

        Args:
        - writer: An instance of asyncio.StreamWriter.

        Returns:
        - None
        """
        ids = await client_addr_map.get_all_ids()
        msg = f"Hello, client {ctx_client_id.get()}, members present: {list(ids)}"
        await StreamUtils.send(writer, msg)

    @staticmethod
    async def send_message(writer: StreamWriter, data: str) -> None:
        """
        Sends a message to the provided StreamWriter.

        Args:
        - writer: An instance of asyncio.StreamWriter.
        - data: A string containing the message to be sent.

        Returns:
        - None
        """
        await StreamUtils.send(
            writer, f"MESSAGE FROM '{ctx_client_id.get()}' :: {data}"
        )

    @staticmethod
    async def render_goodbye(writer: StreamWriter):
        """
        Renders a goodbye message to the provided StreamWriter.

        Args:
        - writer: An instance of asyncio.StreamWriter.

        Returns:
        - None
        """
        msg = f"Good bye, client @ {ctx_client_id.get()}"
        await StreamUtils.send(writer, msg)

    @staticmethod
    async def exit(id: str, writer: StreamWriter):
        """
        Sends an exit message to the provided StreamWriter and closes it.

        Args:
        - id: A string containing the ID of the client to be exited.
        - writer: An instance of asyncio.StreamWriter.

        Returns:
        - None
        """
        msg = f"gotta go client {id}, bye"
        await StreamUtils.send(writer, msg)
        writer.close()

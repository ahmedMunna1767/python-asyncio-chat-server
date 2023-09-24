from asyncio import StreamReader, StreamWriter
from contextvars import ContextVar

from client_map import client_addr_map

ctx_client_id = ContextVar("client_id", default="X")


class StreamUtils:
    @staticmethod
    async def send(writer: StreamWriter, data: str, new_line=True) -> None:
        msg = data.encode("utf-8") + b"\n" if new_line else data.encode("utf-8")
        writer.write(msg)
        await writer.drain()

    @staticmethod
    async def recv(reader: StreamReader) -> str:
        inp_bytes = await reader.readline()
        return inp_bytes.decode("utf-8").strip()

    @staticmethod
    async def render_hello(writer: StreamWriter) -> None:
        ids = await client_addr_map.get_all_ids()
        msg = f"Hello, client {ctx_client_id.get()}, members present: {list(ids)}"
        await StreamUtils.send(writer, msg)

    @staticmethod
    async def send_message(writer: StreamWriter, data: str) -> None:
        await StreamUtils.send(
            writer, f"MESSAGE FROM '{ctx_client_id.get()}' :: {data}"
        )

    @staticmethod
    async def render_goodbye(writer: StreamWriter):
        msg = f"Good bye, client @ {ctx_client_id.get()}"
        await StreamUtils.send(writer, msg)

    @staticmethod
    async def exit(id: str, writer: StreamWriter):
        msg = f"gotta go client {id}, bye"
        await StreamUtils.send(writer, msg)
        writer.close()


async def handle_message(writer: StreamWriter, msg: str):
    id = ctx_client_id.get()
    print(f"Got message from {id}: {msg}")

    if msg == "":
        return

    if msg == "hello":
        return await StreamUtils.render_hello(writer)

    elif msg == "goodbye":
        await StreamUtils.render_goodbye(writer)
        await client_addr_map.delete(id)
        return True

    else:
        parts = msg.split(">")
        if len(parts) != 2:
            return await StreamUtils.send(writer, "invalid message format")
        msg, target_id = parts
        target_id = target_id.strip()

        if target_id == id:
            return await StreamUtils.send(writer, "no fun sending message to self")

        target_writer = await client_addr_map.get(target_id)
        if target_writer is None:
            return await StreamUtils.send(
                writer, f"no client online with id {target_id}"
            )

        return await StreamUtils.send_message(target_writer, msg)

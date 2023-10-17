from asyncio import StreamReader, StreamWriter

from client_map import client_addr_map
from stream_utils import StreamUtils, ctx_client_id


async def handle_message(writer: StreamWriter, msg: str):
    """
    Handles a message received from a client with the given ID.

    Args:
        msg (str): The message to handle.
        writer (StreamWriter): The StreamWriter object for the client.
        id (str): The unique ID of the client.

    Returns:
        bool: True if the connection should be closed else false.
    """

    id = ctx_client_id.get()
    print(f"Got message from {id}: {msg}")

    if msg == "":
        return False

    if msg == "hello":
        await StreamUtils.render_hello(writer)
        return False

    if msg == "goodbye":
        await StreamUtils.render_goodbye(writer)
        await client_addr_map.delete(id)
        return True

    parts = msg.split(">")
    if len(parts) != 2:
        await StreamUtils.send(writer, "invalid message format")
        return False

    msg, target_id = parts
    target_id = target_id.strip()

    if target_id == id:
        await StreamUtils.send(writer, "no fun sending message to self")
        return False

    target_writer = await client_addr_map.get(target_id)
    if target_writer is None:
        await StreamUtils.send(writer, f"no client online with id {target_id}")
        return False

    await StreamUtils.send_message(target_writer, msg)
    return False


async def client_setup(reader: StreamReader, writer: StreamWriter):
    """
    Sets up a new client connection by sending a welcome message and asking for a unique ID.

    Args:
        reader (StreamReader): The StreamReader object for the client.
        writer (StreamWriter): The StreamWriter object for the client.

    Returns:
        str | None: The unique ID of the client if available else none.
    """

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

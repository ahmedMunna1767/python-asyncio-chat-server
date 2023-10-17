import asyncio
from asyncio import StreamWriter


class ClientAddrMap:
    """
    A coroutine-safe dictionary-like object that maps client IDs to their corresponding handlers.

    Attributes:
        _map (dict): A dictionary that maps client IDs to their corresponding handlers.
        lock (asyncio.Lock): A lock that ensures thread safety when accessing the dictionary.
    """

    def __init__(self):
        self._map: dict[str, StreamWriter] = {}
        self.lock = asyncio.Lock()

    async def set(self, id: str, handler: StreamWriter):
        async with self.lock:
            if id in self._map.keys():
                raise ValueError(f"Id {id} already exists")
            self._map[id] = handler

    async def get(self, id: str):
        async with self.lock:
            return self._map.get(id, None)

    async def delete(self, id: str):
        async with self.lock:
            del self._map[id]

    async def get_all_ids(self):
        async with self.lock:
            return list(self._map.keys())


# Create an instance of the ClientAddrMap class to use throughout the program
client_addr_map = ClientAddrMap()

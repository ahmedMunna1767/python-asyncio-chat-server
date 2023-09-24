import asyncio
from asyncio import StreamWriter


class ClientAddrMap:
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


client_addr_map = ClientAddrMap()

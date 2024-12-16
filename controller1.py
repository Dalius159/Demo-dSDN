import asyncio
from base_controller import BaseController

class Controller1(BaseController):
    def __init__(self):
        super().__init__(port=6633, peer_ports=[6634])

    async def run(self):
        await self.start_server()
        await self.install_default_flows()
        # Simulate handling traffic dynamically
        while True:
            await self.handle_packet_in("s1", 1, "ff:ff:ff:ff:ff:ff")  # Broadcast
            await asyncio.sleep(10)

if __name__ == '__main__':
    controller = Controller1()
    asyncio.run(controller.run())

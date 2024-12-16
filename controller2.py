import asyncio
from base_controller import BaseController

class Controller2(BaseController):
    def __init__(self):
        super().__init__(port=6634, peer_ports=[6633])

    async def run(self):
        await self.start_server()
        await self.install_default_flows()
        # Simulate handling traffic dynamically
        while True:
            await self.handle_packet_in("s2", 2, "00:00:00:00:00:02")  # Unicast to h2
            await asyncio.sleep(10)

if __name__ == '__main__':
    controller = Controller2()
    asyncio.run(controller.run())

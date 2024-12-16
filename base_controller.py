import asyncio
import aiohttp
from aiohttp import web
import os
import subprocess

class BaseController:
    def __init__(self, port, peer_ports):
        self.port = port
        self.peer_ports = peer_ports
        self.app = web.Application()
        self.app.add_routes([web.post('/update', self.handle_update)])
        self.runner = web.AppRunner(self.app)

    async def handle_update(self, request):
        data = await request.json()
        print(f"Received update from peer: {data}")
        switch = data["switch"]
        dst = data["dst"]
        action = f"actions=output:all"  # Example action for inter-switch communication
        os.system(f'ovs-ofctl -O OpenFlow13 add-flow {switch} dl_dst={dst},{action}')
        return web.Response(text="Update received")

    async def start_server(self):
        await self.runner.setup()
        site = web.TCPSite(self.runner, 'localhost', self.port)
        await site.start()
        print(f"Controller running on port {self.port}")

    async def send_update(self, data):
        for peer_port in self.peer_ports:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(f'http://localhost:{peer_port}/update', json=data) as resp:
                        if resp.status == 200:
                            print(f"Sent update to controller on port {peer_port}")
            except Exception as e:
                print(f"Failed to send update to port {peer_port}: {e}")

    async def install_default_flows(self):
        print("Waiting for switches to be ready...")
        # Retry until switches are detected
        for i in range(10):
            try:
                result = subprocess.check_output(['ovs-vsctl', 'list-br'])
                bridges = result.decode().splitlines()
                if 's1' in bridges and 's2' in bridges:
                    print("Switches are ready. Installing default flows...")
                    os.system('ovs-ofctl -O OpenFlow13 add-flow s1 actions=NORMAL')
                    os.system('ovs-ofctl -O OpenFlow13 add-flow s2 actions=NORMAL')
                    print("Default flows installed.")
                    return
            except subprocess.CalledProcessError as e:
                print("Error checking switches:", e)
            await asyncio.sleep(1)

        print("Switches not found after waiting. Exiting.")

    async def broadcast_topology(self, switch, in_port, dst):
        data = {
            "switch": switch,
            "in_port": in_port,
            "dst": dst
        }
        for peer_port in self.peer_ports:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(f'http://localhost:{peer_port}/update', json=data) as resp:
                        if resp.status == 200:
                            print(f"Sent topology update to controller on port {peer_port}")
            except Exception as e:
                print(f"Failed to send topology update to port {peer_port}: {e}")

    async def handle_packet_in(self, switch, in_port, dst):
        print(f"Handling PACKET_IN for switch: {switch}, in_port: {in_port}, dst: {dst}")
        if dst == "ff:ff:ff:ff:ff:ff":  # Broadcast address
            action = "actions=FLOOD"
        else:
            action = f"actions=output:{in_port}"
        print(f"Installing flow: {switch} dl_dst={dst}, {action}")
        os.system(f'ovs-ofctl -O OpenFlow13 add-flow {switch} dl_dst={dst},{action}')
        # Broadcast the topology update to peer controllers
        await self.broadcast_topology(switch, in_port, dst)


    async def process_packet_in(self, switch):
        print(f"Processing PACKET_IN for switch: {switch}")
        # Example flow for handling broadcast traffic
        os.system(f'ovs-ofctl -O OpenFlow13 add-flow {switch} dl_dst=ff:ff:ff:ff:ff:ff actions=FLOOD')

    async def run(self):
        await self.start_server()
        await self.install_default_flows()
        while True:
            # Simulate processing PACKET_IN events dynamically
            await self.process_packet_in("s1")
            await self.process_packet_in("s2")
            await asyncio.sleep(10)

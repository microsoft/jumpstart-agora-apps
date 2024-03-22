import asyncio
import sys
from threading import Thread, Event
from typing import Dict, Any, List

from asyncua import Client, Node


class SubscriptionHandler:
    def __init__(self, node_samples: Dict[str, int]):
        self.values = {nid: [] for nid, _ in node_samples.items()}
        self.remaining = {
            nid: num_samples if num_samples >= 0 else sys.maxsize
            for nid, num_samples in node_samples.items()
        }
        self.data_collection_done = Event()

    def datachange_notification(self, node: Node, val, _):
        node_id = node.nodeid.to_string()
        self.values[node_id].append(val)
        if node_id in self.remaining:
            to_collect = self.remaining[node_id]
            to_collect -= 1
            if to_collect <= 0:
                del self.remaining[node_id]
            else:
                self.remaining[node_id] = to_collect

        if not self.remaining:
            self.data_collection_done.set()


class OpcUaClientDataCapture:
    def __init__(self, url: str, node_samples: Dict[str, int], publish_interval_ms=500):
        self.thread = None
        self.url = url.replace("0.0.0.0", "127.0.0.1")
        self.node_samples = node_samples
        self.stop_client_event = asyncio.Event()
        self.publish_interval_ms = publish_interval_ms
        self.sub_handler = SubscriptionHandler(node_samples)

    def start_capture(self):
        self.stop_client_event.clear()
        self.thread = Thread(target=self._worker)
        self.thread.start()

    def wait_for_completion(self, timeout=60) -> Dict[str, List[Any]]:
        self.sub_handler.data_collection_done.wait(timeout)
        self.stop_client_event.set()
        self.thread.join()
        return self.get_collected_data()

    def end_capture(self):
        self.stop_client_event.set()
        self.thread.join()
        return self.get_collected_data()

    def get_collected_data(self):
        return self.sub_handler.values

    async def _capture_data(self):
        async with Client(url=self.url) as client:
            subscription = await client.create_subscription(
                self.publish_interval_ms, self.sub_handler
            )
            nodes = [client.get_node(nid) for nid in self.node_samples.keys()]
            await subscription.subscribe_data_change(nodes)
            await self.stop_client_event.wait()

    def _worker(self):
        loop = asyncio.new_event_loop()
        try:
            main_task = asyncio.ensure_future(self._capture_data(), loop=loop)
            loop.run_until_complete(main_task)
        finally:
            loop.close()

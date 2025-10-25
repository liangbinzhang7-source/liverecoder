"""Chaturbate直播录制"""

import asyncio
from streamlink.stream import HLSStream
from ..recorder import LiveRecorder


class Chaturbate(LiveRecorder):
    """Chaturbate直播录制器"""
    
    async def run(self):
        """检测并录制Chaturbate直播"""
        url = f'https://chaturbate.com/{self.id}'
        if url not in self.recording:
            response = (await self.request(
                method='POST',
                url='https://chaturbate.com/get_edge_hls_url_ajax/',
                headers={
                    'X-Requested-With': 'XMLHttpRequest'
                },
                data={
                    'room_slug': self.id
                }
            )).json()
            if response['room_status'] == 'public':
                title = self.id
                streams = HLSStream.parse_variant_playlist(
                    session=self.get_streamlink(),
                    url=response['url']
                )
                stream = list(streams.values())[2]
                await asyncio.to_thread(self.run_record, stream, url, title, 'ts')

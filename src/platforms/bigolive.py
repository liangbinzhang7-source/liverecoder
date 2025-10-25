"""Bigolive直播录制"""

import asyncio
from streamlink.stream import HLSStream
from ..recorder import LiveRecorder


class Bigolive(LiveRecorder):
    """Bigolive直播录制器"""
    
    async def run(self):
        """检测并录制Bigolive直播"""
        url = f'https://www.bigo.tv/cn/{self.id}'
        if url not in self.recording:
            response = (await self.request(
                method='POST',
                url='https://ta.bigo.tv/official_website/studio/getInternalStudioInfo',
                params={'siteId': self.id}
            )).json()
            if response['data']['alive']:
                title = response['data']['roomTopic']
                stream = HLSStream(
                    session=self.get_streamlink(),
                    url=response['data']['hls_src']
                )  # HLSStream[mpegts]
                await asyncio.to_thread(self.run_record, stream, url, title, 'ts')

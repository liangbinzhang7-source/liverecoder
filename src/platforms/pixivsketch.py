"""Pixiv Sketch直播录制"""

import asyncio
import json
import re
from streamlink.stream import HLSStream
from ..recorder import LiveRecorder


class Pixivsketch(LiveRecorder):
    """Pixiv Sketch直播录制器"""
    
    async def run(self):
        """检测并录制Pixiv Sketch直播"""
        url = f'https://sketch.pixiv.net/{self.id}'
        if url not in self.recording:
            response = (await self.request(
                method='GET',
                url=url
            )).text
            next_data = json.loads(re.search(r'<script id="__NEXT_DATA__".*?>(.*?)</script>', response)[1])
            initial_state = json.loads(next_data['props']['pageProps']['initialState'])
            if lives := initial_state['live']['lives']:
                live = list(lives.values())[0]
                title = live['name']
                streams = HLSStream.parse_variant_playlist(
                    session=self.get_streamlink(),
                    url=live['owner']['hls_movie']
                )
                stream = list(streams.values())[0]  # HLSStream[mpegts]
                await asyncio.to_thread(self.run_record, stream, url, title, 'ts')

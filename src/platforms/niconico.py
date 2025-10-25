"""NicoNico直播录制"""

import asyncio
import json
import re
from ..recorder import LiveRecorder


class Niconico(LiveRecorder):
    """NicoNico直播录制器"""
    
    async def run(self):
        """检测并录制NicoNico直播"""
        url = f'https://live.nicovideo.jp/watch/{self.id}'
        if url not in self.recording:
            response = (await self.request(
                method='GET',
                url=url
            )).text
            if '"content_status":"ON_AIR"' in response:
                title = json.loads(
                    re.search(r'<script type="application/ld\+json">(.*?)</script>', response).group(1)
                )['name']
                stream = self.get_streamlink().streams(url).get('best')  # HLSStream[mpegts]
                await asyncio.to_thread(self.run_record, stream, url, title, 'ts')

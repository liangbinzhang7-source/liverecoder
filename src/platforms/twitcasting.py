"""Twitcasting直播录制"""

import asyncio
import re
from ..recorder import LiveRecorder


class Twitcasting(LiveRecorder):
    """Twitcasting直播录制器"""
    
    async def run(self):
        """检测并录制Twitcasting直播"""
        url = f'https://twitcasting.tv/{self.id}'
        if url not in self.recording:
            response = (await self.request(
                method='GET',
                url='https://twitcasting.tv/streamserver.php',
                params={
                    'target': self.id,
                    'mode': 'client'
                }
            )).json()
            if response:
                response = (await self.request(
                    method='GET',
                    url=url
                )).text
                title = re.search('<meta name="twitter:title" content="(.*?)">', response).group(1)
                stream = self.get_streamlink().streams(url).get('best')  # Stream[mp4]
                await asyncio.to_thread(self.run_record, stream, url, title, 'mp4')

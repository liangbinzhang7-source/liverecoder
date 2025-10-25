"""Afreeca直播录制"""

import asyncio
from ..recorder import LiveRecorder


class Afreeca(LiveRecorder):
    """Afreeca直播录制器"""
    
    async def run(self):
        """检测并录制Afreeca直播"""
        url = f'https://play.afreecatv.com/{self.id}'
        if url not in self.recording:
            response = (await self.request(
                method='POST',
                url='https://live.afreecatv.com/afreeca/player_live_api.php',
                data={'bid': self.id}
            )).json()
            if response['CHANNEL']['RESULT'] != 0:
                title = response['CHANNEL']['TITLE']
                stream = self.get_streamlink().streams(url).get('best')  # HLSStream[mpegts]
                await asyncio.to_thread(self.run_record, stream, url, title, 'ts')

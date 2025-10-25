"""Pandalive直播录制"""

import asyncio
from ..recorder import LiveRecorder


class Pandalive(LiveRecorder):
    """Pandalive直播录制器"""
    
    async def run(self):
        """检测并录制Pandalive直播"""
        url = f'https://www.pandalive.co.kr/live/play/{self.id}'
        if url not in self.recording:
            response = (await self.request(
                method='POST',
                url='https://api.pandalive.co.kr/v1/live/play',
                headers={
                    'x-device-info': '{"t":"webMobile","v":"1.0","ui":0}'
                },
                data={
                    'action': 'watch',
                    'userId': self.id
                }
            )).json()
            if response['result']:
                title = response['media']['title']
                stream = self.get_streamlink().streams(url).get('best')  # HLSStream[mpegts]
                await asyncio.to_thread(self.run_record, stream, url, title, 'ts')

"""哔哩哔哩直播录制"""

import asyncio
from ..recorder import LiveRecorder


class Bilibili(LiveRecorder):
    """哔哩哔哩直播录制器"""
    
    async def run(self):
        """检测并录制B站直播"""
        url = f'https://live.bilibili.com/{self.id}'
        if url not in self.recording:
            response = (await self.request(
                method='GET',
                url='https://api.live.bilibili.com/room/v1/Room/get_info',
                params={'room_id': self.id}
            )).json()
            if response['data']['live_status'] == 1:
                title = response['data']['title']
                stream = self.get_streamlink().streams(url).get('best')  # HTTPStream[flv]
                await asyncio.to_thread(self.run_record, stream, url, title, 'flv')

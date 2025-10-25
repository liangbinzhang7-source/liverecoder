"""虎牙直播录制"""

import asyncio
import re
from ..recorder import LiveRecorder


class Huya(LiveRecorder):
    """虎牙直播录制器"""
    
    async def run(self):
        """检测并录制虎牙直播"""
        url = f'https://www.huya.com/{self.id}'
        if url not in self.recording:
            response = (await self.request(
                method='GET',
                url=url
            )).text
            if '"isOn":true' in response:
                title = re.search('"introduction":"(.*?)"', response).group(1)
                stream = self.get_streamlink().streams(url).get('best')  # HTTPStream[flv]
                await asyncio.to_thread(self.run_record, stream, url, title, 'flv')

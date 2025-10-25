"""抖音直播录制"""

import asyncio
import json
from streamlink.stream import HTTPStream
from ..recorder import LiveRecorder


class Douyin(LiveRecorder):
    """抖音直播录制器"""
    
    async def run(self):
        """检测并录制抖音直播"""
        url = f'https://live.douyin.com/{self.id}'
        if url not in self.recording:
            if not self.client.cookies:
                await self.client.get(url='https://live.douyin.com/')  # 获取ttwid
            response = (await self.request(
                method='GET',
                url='https://live.douyin.com/webcast/room/web/enter/',
                params={
                    'aid': 6383,
                    'device_platform': 'web',
                    'browser_language': 'zh-CN',
                    'browser_platform': 'Win32',
                    'browser_name': 'Chrome',
                    'browser_version': '100.0.0.0',
                    'web_rid': self.id
                },
            )).json()
            if data := response['data']['data']:
                data = data[0]
                if data['status'] == 2:
                    title = data['title']
                    live_url = ''
                    stream_data = json.loads(data['stream_url']['live_core_sdk_data']['pull_data']['stream_data'])
                    for quality_code in ('origin', 'uhd', 'hd', 'sd', 'md', 'ld'):
                        if quality_data := stream_data['data'].get(quality_code):
                            live_url = quality_data['main']['flv']
                            break
                    stream = HTTPStream(
                        self.get_streamlink(),
                        live_url
                    )  # HTTPStream[flv]
                    await asyncio.to_thread(self.run_record, stream, url, title, 'flv')

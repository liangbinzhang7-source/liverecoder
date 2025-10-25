"""YouTube直播录制"""

import asyncio
import json
from jsonpath_ng.ext import parse
from ..recorder import LiveRecorder


class Youtube(LiveRecorder):
    """YouTube直播录制器"""
    
    async def run(self):
        """检测并录制YouTube直播"""
        response = (await self.request(
            method='POST',
            url='https://www.youtube.com/youtubei/v1/browse',
            params={
                'key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
                'prettyPrint': False
            },
            json={
                'context': {
                    'client': {
                        'hl': 'zh-CN',
                        'clientName': 'MWEB',
                        'clientVersion': '2.20230101.00.00',
                        'timeZone': 'Asia/Shanghai'
                    }
                },
                'browseId': self.id,
                'params': 'EgdzdHJlYW1z8gYECgJ6AA%3D%3D'
            }
        )).json()
        jsonpath = parse('$..videoWithContextRenderer').find(response)
        for match in jsonpath:
            video = match.value
            if '"style": "LIVE"' in json.dumps(video):
                url = f"https://www.youtube.com/watch?v={video['videoId']}"
                title = video['headline']['runs'][0]['text']
                if url not in self.recording:
                    stream = self.get_streamlink().streams(url).get('best')  # HLSStream[mpegts]
                    # FIXME:多开直播间中断
                    asyncio.create_task(asyncio.to_thread(self.run_record, stream, url, title, 'ts'))

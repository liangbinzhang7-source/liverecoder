"""Twitch直播录制"""

import asyncio
from streamlink.options import Options
from ..recorder import LiveRecorder


class Twitch(LiveRecorder):
    """Twitch直播录制器"""
    
    async def run(self):
        """检测并录制Twitch直播"""
        url = f'https://www.twitch.tv/{self.id}'
        if url not in self.recording:
            response = (await self.request(
                method='POST',
                url='https://gql.twitch.tv/gql',
                headers={'Client-Id': 'kimne78kx3ncx6brgo4mv6wki5h1ko'},
                json=[{
                    'operationName': 'StreamMetadata',
                    'variables': {'channelLogin': self.id},
                    'extensions': {
                        'persistedQuery': {
                            'version': 1,
                            'sha256Hash': 'a647c2a13599e5991e175155f798ca7f1ecddde73f7f341f39009c14dbf59962'
                        }
                    }
                }]
            )).json()
            if response[0]['data']['user']['stream']:
                title = response[0]['data']['user']['lastBroadcast']['title']
                options = Options()
                options.set('disable-ads', True)
                stream = self.get_streamlink().streams(url, options).get('best')  # HLSStream[mpegts]
                await asyncio.to_thread(self.run_record, stream, url, title, 'ts')

"""斗鱼直播录制"""

import asyncio
import time
import uuid
from urllib.parse import parse_qs

import jsengine
from loguru import logger
from streamlink.stream import HTTPStream

from ..recorder import LiveRecorder


class Douyu(LiveRecorder):
    """斗鱼直播录制器"""
    
    async def run(self):
        """检测并录制斗鱼直播"""
        url = f'https://www.douyu.com/{self.id}'
        if url not in self.recording:
            response = (await self.request(
                method='GET',
                url=f'https://open.douyucdn.cn/api/RoomApi/room/{self.id}',
            )).json()
            state = response['data']['room_status']
            self.mState = state
            logger.info(
                f'直播状态[1已开播，2未开播]：{state} 上一次开播时间：{response["data"]["start_time"]}')
            if state == '1':
                liveUrl = await self.get_live()
                if liveUrl != '':
                    title = response['data']['room_name']
                    stream = HTTPStream(
                        self.get_streamlink(),
                        liveUrl
                    )  # HTTPStream[flv]
                    await asyncio.to_thread(self.run_record, stream, url, title, 'flv')
            else:
                self.ssl = True
    
    async def get_js(self):
        """获取斗鱼加密JS"""
        response = (await self.request(
            method='POST',
            url=f'https://www.douyu.com/swf_api/homeH5Enc?rids={self.id}'
        )).json()
        js_enc = response['data'][f'room{self.id}']
        getUrl = self.crypto_js_url
        crypto_js = (await self.request(
            method='GET',
            url=getUrl
        )).text
        return jsengine.JSEngine(js_enc + crypto_js)
    
    async def get_live(self):
        """获取斗鱼直播流地址"""
        did = uuid.uuid4().hex
        tt = str(int(time.time()))
        params = {
            'cdn': 'tct-h5',
            'did': did,
            'tt': tt,
            'rate': 0
        }
        js = await self.get_js()
        query = js.call('ub98484234', self.id, did, tt)
        params.update({k: v[0] for k, v in parse_qs(query).items()})
        response = (await self.request(
            method='POST',
            url=f'https://www.douyu.com/lapi/live/getH5Play/{self.id}',
            params=params
        )).json()
        if response['data'] == '' and response['msg'] != '':
            logger.info(f'直播状态：{response["error"]} {response["msg"]}')
            return ''
        return f"{response['data']['rtmp_url']}/{response['data']['rtmp_live']}"

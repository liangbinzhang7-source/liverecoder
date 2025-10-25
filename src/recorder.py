"""直播录制基类"""

import asyncio
from http.cookies import SimpleCookie
from typing import Dict, Tuple, Union

import anyio
import httpx
import streamlink
from httpx_socks import AsyncProxyTransport
from loguru import logger
from streamlink.stream import StreamIO, HTTPStream, HLSStream

from .utils.file_handler import FileHandler


class LiveRecorder:
    """直播录制基类"""
    
    def __init__(self, config: dict, user: dict, recording: Dict[str, Tuple[StreamIO, any]]):
        """
        初始化录制器
        
        Args:
            config: 全局配置
            user: 用户配置
            recording: 正在录制的字典（共享）
        """
        self.id = user['id']
        platform = user['platform']
        name = user.get('name', self.id)
        self.flag = f'[{platform}][{name}]'
        
        self.interval = user.get('interval', 10)
        self.crypto_js_url = user.get('crypto_js_url', '')
        self.headers = user.get('headers', {'User-Agent': 'Chrome'})
        self.cookies = user.get('cookies')
        self.format = user.get('format')
        self.proxy = user.get('proxy', config.get('proxy'))
        self.output = user.get('output', config.get('output', 'output'))
        self.recording = recording  # 共享的录制字典
        
        if not self.crypto_js_url:
            self.crypto_js_url = 'https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.1.1/crypto-js.min.js'
        
        self._get_cookies()
        self.client = self._get_client()
    
    async def start(self):
        """开始监控直播状态"""
        self.ssl = True
        self.mState = 0
        while True:
            try:
                logger.info(f'{self.flag}正在检测直播状态')
                logger.info(f'预配置刷新间隔：{self.interval}s')
                try:
                    await self.run()   
                except Exception as run_error:
                    logger.error(f"{self.flag}直播检测内部错误\n{repr(run_error)}")
                state = self.mState
                timeI = self.interval
                if state == '1':
                    timeI = 2
                logger.info(f'->直播状态：{state}  实际刷新间隔：{timeI}s')
                await asyncio.sleep(timeI)
            except ConnectionError as error:
                if '直播检测请求协议错误' not in str(error):
                    logger.error(error)
                await self.client.aclose()
                self.client = self._get_client()
            except Exception as error:
                logger.exception(f'{self.flag}直播检测错误\n{repr(error)}')
    
    async def run(self):
        """子类需要实现的检测逻辑"""
        pass
    
    async def request(self, method: str, url: str, **kwargs):
        """
        发送HTTP请求
        
        Args:
            method: 请求方法
            url: 请求URL
            **kwargs: 其他参数
            
        Returns:
            响应对象
        """
        try:
            response = await self.client.request(method, url, **kwargs)
            return response
        except httpx.ProtocolError as error:
            raise ConnectionError(f'{self.flag}直播检测请求协议错误\n{error}')
        except httpx.HTTPStatusError as error:
            raise ConnectionError(
                f'{self.flag}直播检测请求状态码错误\n{error}\n{response.text}')
        except anyio.EndOfStream as error:
            raise ConnectionError(f'{self.flag}直播检测代理错误\n{error}')
        except httpx.HTTPError as error:
           logger.error(f'网络异常 重试...')
           raise ConnectionError(f'{self.flag}直播检测请求错误\n{repr(error)}')
    
    def _get_client(self) -> httpx.AsyncClient:
        """创建HTTP客户端"""
        client_kwargs = {
            'http2': True,
            'timeout': self.interval,
            'limits': httpx.Limits(max_keepalive_connections=100, keepalive_expiry=self.interval * 2),
            'headers': self.headers,
            'cookies': self.cookies
        }
        # 检查是否有设置代理
        if self.proxy:
            if 'socks' in self.proxy:
                client_kwargs['transport'] = AsyncProxyTransport.from_url(self.proxy)
            else:
                # httpx 新版本使用 'proxy' (单数) 而不是 'proxies'
                client_kwargs['proxy'] = self.proxy
        return httpx.AsyncClient(**client_kwargs)
    
    def _get_cookies(self):
        """解析cookies字符串"""
        if self.cookies:
            cookies = SimpleCookie()
            cookies.load(self.cookies)
            self.cookies = {k: v.value for k, v in cookies.items()}
    
    def get_streamlink(self):
        """创建streamlink会话"""
        session = streamlink.session.Streamlink({
            'stream-segment-timeout': 60,
            'hls-segment-queue-threshold': 10
        })
        ssl = self.ssl
        logger.info(f'是否验证SSL：{ssl}')
        session.set_option('http-ssl-verify', ssl)
        # 添加streamlink的http相关选项
        if proxy := self.proxy:
            # 代理为socks5时，streamlink的代理参数需要改为socks5h，防止部分直播源获取失败
            if 'socks' in proxy:
                proxy = proxy.replace('://', 'h://')
            session.set_option('http-proxy', proxy)
        if self.headers:
            session.set_option('http-headers', self.headers)
        if self.cookies:
            session.set_option('http-cookies', self.cookies)
        return session
    
    def run_record(self, stream: Union[StreamIO, HTTPStream, HLSStream], url: str, title: str, format: str):
        """
        执行录制
        
        Args:
            stream: 直播流对象
            url: 直播URL
            title: 直播标题
            format: 文件格式
        """
        # 获取输出文件名
        filename = FileHandler.get_filename(self.flag, title, format)
        if stream:
            logger.info(f'{self.flag}开始录制：{filename}')
            # 调用streamlink录制直播
            result = self._write_stream(stream, url, filename)
            # 处理SSL错误
            if result == 'ssl_error':
                self.ssl = False
            # 录制成功、format配置存在且不等于直播平台默认格式时运行ffmpeg封装
            if result is True and self.format and self.format != format:
                FileHandler.run_ffmpeg(self.output, filename, format, self.format, self.flag)
            self.recording.pop(url, None)
            logger.info(f'{self.flag}停止录制：{filename}')
        else:
            logger.error(f'{self.flag}无可用直播源：{filename}')
    
    def _write_stream(self, stream: Union[StreamIO, HTTPStream, HLSStream], url: str, filename: str) -> Union[bool, str]:
        """
        将直播流写入文件
        
        Args:
            stream: 直播流对象
            url: 直播URL
            filename: 输出文件名
            
        Returns:
            录制结果：True=成功, False=失败, 'ssl_error'=SSL错误
        """
        import re
        from pathlib import Path
        from streamlink_cli.main import open_stream
        from streamlink_cli.output import FileOutput
        from streamlink_cli.streamrunner import StreamRunner
        
        logger.info(f'{self.flag}获取到直播流链接：{filename}\n{stream.url}')
        output = FileOutput(Path(f'{self.output}/{filename}'))
        try:
            stream_fd, prebuffer = open_stream(stream)
            output.open()
            self.recording[url] = (stream_fd, output)
            logger.info(f'{self.flag}正在录制：{filename}')
            StreamRunner(stream_fd, output).run(prebuffer)
            return True
        except Exception as error:
            if 'timeout' in str(error):
                logger.warning(f'{self.flag}直播录制超时：{filename}\n{error}')
            elif re.search(r'SSL: CERTIFICATE_VERIFY_FAILED', str(error)):
                logger.warning(f'{self.flag}SSL错误：{filename}\n{error}')
                return 'ssl_error'
            elif re.search(r'(Unable to open URL|No data returned from stream)', str(error)):
                logger.warning(f'{self.flag}直播流打开错误：{filename}\n{error}')
            else:
                logger.exception(f'{self.flag}直播录制错误：{filename}\n{error}')
            return False
        finally:
            output.close()

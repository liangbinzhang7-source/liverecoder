#!/usr/bin/env python3
"""
LiveRecorder - 统一启动入口
支持命令行模式和Web界面模式
"""

import argparse
import asyncio
import sys
import threading
import time
from typing import Dict, Tuple

from loguru import logger
from streamlink.stream import StreamIO

from src.config import Config
from src.platforms import PLATFORMS
from src.utils import setup_logger

# 全局录制状态字典
recording: Dict[str, Tuple[StreamIO, any]] = {}


async def run_cli_mode(config_file: str = 'config.json'):
    """命令行模式 - 从config.json读取配置"""
    logger.info('=' * 60)
    logger.info('LiveRecorder 命令行模式启动')
    logger.info('=' * 60)
    
    # 加载配置
    config = Config(config_file)
    global_config = config.get_global_config()
    users = config.get_users()
    
    if not users:
        logger.error('配置文件中没有主播配置，请编辑 config.json')
        return
    
    try:
        tasks = []
        for user in users:
            platform_name = user['platform']
            if platform_name not in PLATFORMS:
                logger.warning(f'不支持的平台: {platform_name}')
                continue
            
            # 创建平台录制器实例
            platform_class = PLATFORMS[platform_name]
            recorder = platform_class(global_config, user, recording)
            coro = recorder.start()
            tasks.append(asyncio.create_task(coro))
        
        if not tasks:
            logger.error('没有有效的录制任务')
            return
        
        logger.info(f'已启动 {len(tasks)} 个录制任务')
        await asyncio.wait(tasks)
    except (asyncio.CancelledError, KeyboardInterrupt, SystemExit):
        logger.warning('用户中断录制，正在关闭直播流')
        for stream_fd, output in recording.copy().values():
            stream_fd.close()
            output.close()


def run_web_server(host: str = "0.0.0.0", port: int = 8888):
    """在单独线程中运行Web服务器"""
    import uvicorn
    from src import web_api
    
    # 将recording字典共享给web_api
    web_api.set_shared_recording(recording)
    
    logger.info(f'Web服务器启动在 http://{host}:{port}')
    uvicorn.run("src.web_api:app", host=host, port=port, log_level="info")


async def run_recorders_web(config_file: str = 'web_config.json'):
    """运行录制器（Web模式 - 从web_config.json读取）"""
    logger.info('录制监控服务已启动')
    
    try:
        while True:
            # 动态加载配置
            config = Config(config_file)
            global_config = config.get_global_config()
            users = config.get_users()
            
            if not users:
                logger.info('当前没有配置主播，等待通过Web界面添加...')
                await asyncio.sleep(30)
                continue
            
            tasks = []
            for user in users:
                platform_name = user['platform']
                if platform_name not in PLATFORMS:
                    logger.warning(f'不支持的平台: {platform_name}')
                    continue
                
                # 创建平台录制器实例
                platform_class = PLATFORMS[platform_name]
                recorder = platform_class(global_config, user, recording)
                coro = recorder.start()
                tasks.append(asyncio.create_task(coro))
            
            if tasks:
                logger.info(f'启动了 {len(tasks)} 个录制任务')
                await asyncio.wait(tasks)
            else:
                logger.warning('没有有效的录制任务，30秒后重试...')
                await asyncio.sleep(30)
                
    except (asyncio.CancelledError, KeyboardInterrupt, SystemExit):
        logger.warning('用户中断录制，正在关闭直播流')
        for stream_fd, output in recording.copy().values():
            stream_fd.close()
            output.close()


async def run_web_mode(host: str = "0.0.0.0", port: int = 8888):
    """Web模式 - 启动Web界面和录制服务"""
    logger.info('=' * 60)
    logger.info('LiveRecorder Web模式启动')
    logger.info('=' * 60)
    
    # 在单独线程中启动Web服务器
    web_thread = threading.Thread(target=run_web_server, args=(host, port), daemon=True)
    web_thread.start()
    
    # 等待Web服务器启动
    time.sleep(2)
    
    logger.info(f'请访问 http://localhost:{port} 查看Web管理界面')
    logger.info('录制服务正在启动...')
    
    # 在主线程中运行录制器
    await run_recorders_web()


def main():
    """主函数 - 解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='LiveRecorder - 多平台直播录制工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 命令行模式（从 config.json 读取配置）
  python app.py
  python app.py --mode cli --config config.json
  
  # Web界面模式（从 web_config.json 读取配置）
  python app.py --mode web
  python app.py --mode web --host 0.0.0.0 --port 8888
        """
    )
    
    parser.add_argument(
        '--mode', 
        choices=['cli', 'web'], 
        default='cli',
        help='运行模式: cli=命令行模式, web=Web界面模式 (默认: cli)'
    )
    
    parser.add_argument(
        '--config',
        default='config.json',
        help='配置文件路径 (仅CLI模式, 默认: config.json)'
    )
    
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Web服务器监听地址 (仅Web模式, 默认: 0.0.0.0)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8888,
        help='Web服务器端口 (仅Web模式, 默认: 8888)'
    )
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logger()
    
    # 根据模式运行
    try:
        if args.mode == 'cli':
            asyncio.run(run_cli_mode(args.config))
        else:  # web
            asyncio.run(run_web_mode(args.host, args.port))
    except KeyboardInterrupt:
        logger.info('程序已退出')
    except Exception as e:
        logger.exception(f'程序异常退出: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()

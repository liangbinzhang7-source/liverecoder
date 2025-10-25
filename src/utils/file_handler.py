"""文件处理工具"""

import os
import time
import ffmpeg
from loguru import logger


class FileHandler:
    """文件处理类"""
    
    @staticmethod
    def get_filename(flag: str, title: str, format: str) -> str:
        """
        生成录制文件名
        
        Args:
            flag: 平台和主播标识
            title: 直播标题
            format: 文件格式
            
        Returns:
            文件名
        """
        live_time = time.strftime('%Y.%m.%d %H.%M.%S')
        # 文件名特殊字符转换为全角字符
        char_dict = {
            '"': '＂',
            '*': '＊',
            ':': '：',
            '<': '＜',
            '>': '＞',
            '?': '？',
            '/': '／',
            '\\': '＼',
            '|': '｜'
        }
        for half, full in char_dict.items():
            title = title.replace(half, full)
        filename = f'[{live_time}]{flag}{title[:50]}.{format}'
        return filename
    
    @staticmethod
    def run_ffmpeg(output_dir: str, filename: str, old_format: str, new_format: str, flag: str):
        """
        使用ffmpeg转换文件格式
        
        Args:
            output_dir: 输出目录
            filename: 原文件名
            old_format: 原格式
            new_format: 新格式
            flag: 平台和主播标识
        """
        logger.info(f'{flag}开始ffmpeg封装：{filename}')
        new_filename = filename.replace(f'.{old_format}', f'.{new_format}')
        ffmpeg.input(f'{output_dir}/{filename}').output(
            f'{output_dir}/{new_filename}',
            codec='copy',
            map_metadata='-1',
            movflags='faststart'
        ).global_args('-hide_banner').run()
        os.remove(f'{output_dir}/{filename}')

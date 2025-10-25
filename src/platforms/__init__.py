"""直播平台实现模块"""

from .bilibili import Bilibili
from .douyu import Douyu
from .huya import Huya
from .douyin import Douyin
from .youtube import Youtube
from .twitch import Twitch
from .niconico import Niconico
from .twitcasting import Twitcasting
from .afreeca import Afreeca
from .pandalive import Pandalive
from .bigolive import Bigolive
from .pixivsketch import Pixivsketch
from .chaturbate import Chaturbate

# 平台类映射字典
PLATFORMS = {
    'Bilibili': Bilibili,
    'Douyu': Douyu,
    'Huya': Huya,
    'Douyin': Douyin,
    'Youtube': Youtube,
    'Twitch': Twitch,
    'Niconico': Niconico,
    'Twitcasting': Twitcasting,
    'Afreeca': Afreeca,
    'Pandalive': Pandalive,
    'Bigolive': Bigolive,
    'Pixivsketch': Pixivsketch,
    'Chaturbate': Chaturbate
}

__all__ = [
    'Bilibili', 'Douyu', 'Huya', 'Douyin', 'Youtube', 'Twitch',
    'Niconico', 'Twitcasting', 'Afreeca', 'Pandalive', 'Bigolive',
    'Pixivsketch', 'Chaturbate', 'PLATFORMS'
]

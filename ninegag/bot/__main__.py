from aiogram.utils import executor

from .bot import dp, channel_publish

if __name__ == '__main__':
    executor.start(dp, channel_publish())

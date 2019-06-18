from aiogram.utils import executor

from .bot import channel_publish, dp

if __name__ == "__main__":
    executor.start(dp, channel_publish())

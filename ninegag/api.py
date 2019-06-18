import asyncio
import logging
from pathlib import Path

import aiofiles
import aiohttp

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

BASE_PATH = Path(__file__).absolute().parents[1] / "posts"


def get_file_url(post):
    if post["type"] == "Photo":
        url = post["images"]["image700"]["url"]
    elif post["type"] == "Animated":
        url = post["images"]["image460sv"]["url"]

    logger.info(url)
    return url


async def download(session, url):
    filename = BASE_PATH / url.split("/")[-1]
    if filename.exists():
        return
    logger.info("starting %s", filename)
    async with aiofiles.open(filename, mode="wb") as f:
        async with session.get(url) as resp:
            while True:
                chunk = await resp.content.read(1024 * 1024)
                logger.debug("downloading %s", filename)
                if not chunk:
                    logger.info("fininshed %s", filename)
                    break
                await f.write(chunk)


async def get_posts(session, url):
    async with session.get(url) as resp:
        response = await resp.json()

        await asyncio.gather(
            *[
                download(session, get_file_url(post))
                for post in response["data"]["posts"]
            ]
        )

        return response["data"]["nextCursor"]


async def get_hot(base_url):
    next_url = ""
    async with aiohttp.ClientSession() as session:
        for page in range(3):
            logger.info("getting page %s", page)
            url = base_url + next_url
            next_url = await get_posts(session, url)


def main():
    url = "https://9gag.com/v1/group-posts/group/default/type/hot?"
    asyncio.run(get_hot(url))


if __name__ == "__main__":
    main()

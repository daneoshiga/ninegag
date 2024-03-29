import logging

import aiohttp
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from prettyconf import config
from tortoise import Tortoise

from ninegag.api import get_file_url
from ninegag.models import Post, Section

BOT_TOKEN = config("BOT_TOKEN")
CHAT_ID = config("CHAT_ID")
COOKIE_ID = config("COOKIE_ID")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


logger = logging.getLogger(__name__)


async def channel_publish():
    await Tortoise.init(
        db_url=config("DATABASE_URL"), modules={"models": ["ninegag.models"]}
    )

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "DNT": "1",
        "Host": "9gag.com",
        "Referer": "https://9gag.com/",
        "TE": "Trailers",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:73.0) Gecko/20100101 Firefox/73.0",
    }

    cookies = {"__cfduid": COOKIE_ID, "____ri": "6195", "____lo": "US", "gag_tz": "-3"}

    async with aiohttp.ClientSession(headers=headers, cookies=cookies) as session:
        url = "https://9gag.com/v1/group-posts/group/default/type/hot"
        async with session.get(url) as resp:
            response = await resp.json()
            posts = response["data"]["posts"]

    for post in posts:
        section, _ = await Section.get_or_create(
            name=post["postSection"]["name"],
            slug=post["postSection"]["url"].split("/")[-1],
        )
        post_obj, created = await Post.get_or_create(
            id=post["id"],
            url=post["url"],
            file_url=get_file_url(post),
            title=post["title"],
            section=section,
            post_type=post["type"],
            has_audio=bool(
                post["type"] == "Animated" and post["images"]["image460sv"]["hasAudio"]
            ),
            tags=",".join(tag["url"].split("/tag/")[1] for tag in post["tags"]),
        )
        if not created:
            continue
        if section.name == "Promoted":
            continue

        params = {
            "chat_id": CHAT_ID,
            "caption": await post_obj.caption(),
            "parse_mode": types.ParseMode.HTML,
        }
        if post_obj.is_photo():
            send_method = bot.send_photo
            params["photo"] = post_obj.file_url
        elif post_obj.is_gif():
            send_method = bot.send_animation
            params["animation"] = post_obj.file_url
        elif post_obj.is_video():
            send_method = bot.send_video
            params["video"] = post_obj.file_url

        await send_method(**params)
    await Tortoise.close_connections()

import asyncio
import tomllib

import aiohttp
from loguru import logger
from WechatAPI import WechatAPIClient
from utils.decorators import *
from utils.plugin_base import PluginBase


class WarcraftLogsScreenshot(PluginBase):
    description = "WarcraftLogs"
    author = "刚某人"
    version = "1.0.0"

    def __init__(self):
        super().__init__()

        with open("plugins/WarcraftLogsScreenshot/config.toml", "rb") as f:
            plugin_config = tomllib.load(f)

        config = plugin_config["WarcraftLogs"]

        self.enable = config["enable"]
        self.command = config["command"]

    @on_text_message
    async def handle_text(self, bot: WechatAPIClient, message: dict):
        if not self.enable:
            return

        content = str(message["Content"]).strip()
        command = content.split(" ")

        if command[0] not in self.command:
            return

        if len(command) < 3:
            await bot.send_text_message(message["FromWxid"], "-----刚某人-----\n请提供正确的命令格式，例如：查分 祈福 抓隔命促生产")
            return

        realm = command[1]
        character_name = command[2]
       

        request_url = (
            f"https://api.dudunas.top/api/datashot?"
            f"AppSecret=123&types=pc&url="
            f"https://cn.classic.warcraftlogs.com/character/cn/{realm}/{character_name}"
        )
        logger.warning(f"查分:{request_url}")
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get(request_url) as resp:
                data = await resp.json()

        if data["code"] != 200:
            await bot.send_text_message(message["FromWxid"], "-----刚某人-----\n截图获取失败！")
            return

        share_link = data["data"]["share_link"]
        title = data["data"]["title"]
        description = data["data"]["description"]

        response_text = (
            f"-----刚某人-----\n"
            f"标题: {title}\n"
            f"描述: {description}\n"
        )

        await bot.send_text_message(message["FromWxid"], response_text)

        async with aiohttp.ClientSession() as session:
            async with session.get(share_link) as img_resp:
                image_byte = await img_resp.read()

        await bot.send_image_message(message["FromWxid"], image_byte)




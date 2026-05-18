import discord

from pytexbot.constants import WELCOME_DM_MESSAGE


async def send_welcome_dm(member: discord.Member):
    try:
        await member.send(WELCOME_DM_MESSAGE)
    except discord.Forbidden:
        pass

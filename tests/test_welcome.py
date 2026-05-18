from unittest.mock import AsyncMock, MagicMock

import discord
import pytest

from pytexbot.handlers import send_welcome_dm
from pytexbot.constants import WELCOME_DM_MESSAGE


async def test_sends_welcome_dm_to_new_member():
    member = MagicMock(spec=discord.Member)
    member.send = AsyncMock()

    await send_welcome_dm(member)

    member.send.assert_called_once_with(WELCOME_DM_MESSAGE)


async def test_silently_ignores_forbidden_when_dms_disabled():
    member = MagicMock(spec=discord.Member)
    member.send = AsyncMock(side_effect=discord.Forbidden(MagicMock(), "Cannot send messages to this user"))

    await send_welcome_dm(member)  # should not raise

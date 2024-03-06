"""Discord bot for PyTexas

required scopes:
- bot


requires permissions:
- Manage Roles
- Send Messages

"""
import os
import sys

import discord

from pytexbot.constants import (CONFERENCE_ORGANIZERS_ROLEID,
                                CONFERENCE_2024_ATTENDEES_ROLEID,
                                PYTEXAS_GUILD_ID)

token = os.getenv("DISCORD_TOKEN")
my_guild = os.getenv("DISCORD_GUILD")
# "PyTexas"

pytexas_guild_obj = discord.Object(id=PYTEXAS_GUILD_ID)
print(f"global guild object? {pytexas_guild_obj} {type(pytexas_guild_obj)}")


# TODO: This is a refactoring of the above functions into a class...finish me!
class PyTexBotClient(discord.Client):
    """Client subclass representing our bot.
    """

    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)

        self.tree = discord.app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global
    # commands instead. By doing so, we don't have to wait up to an hour until
    # they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=pytexas_guild_obj)
        cmds = await self.tree.sync(guild=pytexas_guild_obj)

        nlt = '\n\t'
        print(f"commands synced: {nlt}"
              f"{nlt.join((cmd.name + ':' + cmd.description) for cmd in cmds)}")


intents = discord.Intents.default()
client = PyTexBotClient(intents=intents)

# alias because reasons
bot = client


@client.event
async def on_ready():

    # TODO: we don't need this any more, right?
    #       but maybe we don't want to hardcode the guild id...
    for guild in client.guilds:
        print(guild)
        if guild.name == my_guild:
            break
    else:
        print(f"Could not find guild: {my_guild}")
        sys.exit()

    print(
        f"{client.user} is connected to the following guild:\n"
        f"{guild.name}(id: {guild.id}) [{type(guild)}]\n"
    )


@client.event
async def on_message(message):
    print("Received message...")
    if message.author == client.user:
        return

    print(f" -> {message.content or '<empty>'}")
    message_content = message.content.lower()

    if "ping" in message_content:
        await message.channel.send("Pong!")


# @client.tree.command(description="Simple test command",
#                   guild=pytexas_guild_obj)
@client.tree.command(description="Simple test command")
async def ping(interaction):
    print("Received /ping")
    print(f"{interaction.guild}")
    print(f"{interaction.channel}")
    print(f"{interaction.user}")

    await interaction.response.send_message("Pong!")


# @client.tree.command(description="Check in 2024",
#                   guild=pytexas_guild_obj)
@client.tree.command()
async def checkin2024(interaction):
    """Adds Conference Attendees Role to user.

    Currently limited to users with Conference Organizers Role
    """
    print("Received /checkin_2024")

    print(f"{interaction.guild}")
    print(f"{interaction.channel}")
    print(f"{interaction.user}")

    organizer_role = interaction.guild.get_role(CONFERENCE_ORGANIZERS_ROLEID)
    attendee_role = (interaction.guild
                                .get_role(CONFERENCE_2024_ATTENDEES_ROLEID))

    print(f"{organizer_role}")
    print(f"{attendee_role}")

    # TODO: replace with app_commands.check.has_role?
    if organizer_role in interaction.user.roles:
        await interaction.user.add_roles(attendee_role)

    await interaction.response.send_message("Checked in!")


# @client.tree.command(description="Check out 2024",
#                   guild=pytexas_guild_obj)
@client.tree.command()
async def checkout2024(interaction):
    """Removes Conference Attendees Role from user.

    Currently limited to users with Conference Organizers Role
    """
    print("Received /checkout_2024")

    print(f"{interaction.guild}")
    print(f"{interaction.channel}")
    print(f"{interaction.user}")

    organizer_role = interaction.guild.get_role(CONFERENCE_ORGANIZERS_ROLEID)
    attendee_role = (interaction.guild
                                .get_role(CONFERENCE_2024_ATTENDEES_ROLEID))

    print(f"{organizer_role}")
    print(f"{attendee_role}")

    # TODO: replace with app_commands.check.has_role?
    if organizer_role in interaction.user.roles:
        await interaction.user.remove_roles(attendee_role)

    await interaction.response.send_message("Checked out!")


def cli_main():

    client.run(token)


if __name__ == "__main__":
    cli_main()

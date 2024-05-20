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
from dotenv import load_dotenv
import requests

from pytexbot.constants import (CONFERENCE_ORGANIZERS_ROLEID,
                                CONFERENCE_2024_ATTENDEES_ROLEID,
                                PYTEXAS_GUILD_ID)

# Load config from environment or dotenv file
load_dotenv()

discord_token = os.getenv("DISCORD_TOKEN")
if not discord_token:
    sys.exit(f"Could not find DISCORD_TOKEN.  Exiting...")

my_guild = os.getenv("DISCORD_GUILD")
if not my_guild:
    sys.exit(f"Could not find DISCORD_GUILD.  Exiting...")

pretix_api_token = os.getenv("PRETIX_API_TOKEN")
if not pretix_api_token:
    sys.exit(f"Could not find PRETIX_API_TOKEN.  Exiting...")

pytexas_guild_obj = discord.Object(id=PYTEXAS_GUILD_ID)
print(f"global guild object? {pytexas_guild_obj} {type(pytexas_guild_obj)}")


# TODO: This is a refactoring of the above functions into a class...finish me!
class PyTexBotClient(discord.Client):
    """Client subclass representing our bot.
    """

    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)

        self.tree = discord.app_commands.CommandTree(self)
        self.attendee_emails = []
        self.base_pretix_api_url = (
            'https://pretix.eu/api/v1/organizers/pytexas/events/''2024/orders/'
        )
        self.headers = {"Authorization": f'Token {pretix_api_token}'}

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

    def build_attendee_emails_list(self):
        """
        Gets the list of all registered attendees' emails from pretix by paginating
        through the API response.
        """
        self.attendee_emails = []
        pretix_api_url = self.base_pretix_api_url
        print("Fetching attendee emails from pretix API...")
        while pretix_api_url:
            print(f'{pretix_api_url}')
            response = requests.get(pretix_api_url, headers=self.headers)
            attendee_data = response.json()
            self.attendee_emails += [record['email'] for record in
                                attendee_data['results']]  # noqa
            print(f"got {len(self.attendee_emails)} attendee emails from pretix...")
            pretix_api_url = attendee_data['next']

        print("Done fetching emails from pretix.")
        print(f'total {len(self.attendee_emails)=}')


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

    # Build initial attendee emails list
    client.build_attendee_emails_list()


@client.event
async def on_message(message):
    print("Received message...")
    if message.author == client.user:
        return

    print(f" -> {message.content or '<empty>'}")
    message_content = message.content.lower()

    if "ping" in message_content:
        await message.channel.send("Pong!",
                                   ephemeral=True)


# @client.tree.command(description="Simple test command",
#                   guild=pytexas_guild_obj)
@client.tree.command(description="Simple test command")
async def ping(interaction):
    print("Received /ping")
    print(f"{interaction.guild}")
    print(f"{interaction.channel}")
    print(f"{interaction.user}")

    await interaction.response.send_message("Pong!",
                                            ephemeral=True)


@client.tree.command()
async def register(interaction, attendee_email: str):
    """Adds Conference Attendees Role to users registered with PreTix.

    /register my@email.here

    If the given email is registered for the conference in Pretix, then the
    Conference Attendee Role will be added to the discord user.

    Currently limited to users with Conference Organizers Role
    """
    print("Received /register")

    print(f"{interaction.guild}")
    print(f"{interaction.channel}")
    print(f"{interaction.user}")

    organizer_role = interaction.guild.get_role(CONFERENCE_ORGANIZERS_ROLEID)
    attendee_role = (interaction.guild
                                .get_role(CONFERENCE_2024_ATTENDEES_ROLEID))

    print(f"{attendee_role}")

    # TODO: replace requests with httpx for extra async-ness?

    print("Deferring response")
    await interaction.response.defer(ephemeral=True)

    # Check if the provided email is in the attendee_emails list. If we can't find it
    # immediately, re-build the list and check again. If the still can't be found,
    # give up and send a response.
    if attendee_email in client.attendee_emails:
        print(
            f"User with email {attendee_email} found in attendee email list, sending"
            f" response."
        )
        await interaction.followup.send("Registered!", ephemeral=True)
    else:
        print(
            f"User with {attendee_email} not found. "
            f"Re-populating attendee email list."
        )
        client.build_attendee_emails_list()
        if attendee_email in client.attendee_emails:
            print(
                f"{attendee_email} now found in attendee email list, sending response."
            )
            await interaction.followup.send("Registered!", ephemeral=True)
        else:
            print(f"{attendee_email} still not found. Giving up and sending response.")
            await interaction.followup.send(
                "Oh noes! I couldn't find your email!", ephemeral=True
            )


def cli_main():

    client.run(discord_token)


if __name__ == "__main__":
    cli_main()

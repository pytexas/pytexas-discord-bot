import os
import asyncio
import discord
from discord import app_commands
from dotenv import load_dotenv
import serial
import time

# 1. Load configuration from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SERIAL_PORT = os.getenv('SERIAL_PORT', 'COM5')

# 2. Setup Serial Connection
try:
    arduino = serial.Serial(SERIAL_PORT, 9600, timeout=1)
    time.sleep(2)
    print(f"✅ Connected to Arduino on {SERIAL_PORT}!")
except Exception as e:
    print(f"❌ Hardware Error on {SERIAL_PORT}: {e}")

# 3. Discord Bot Logic
class HardwareBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

client = HardwareBot()

# --- COMMANDS WITH COOLDOWNS ---

@client.tree.command(name="wave", description="Send a long wave blink")
@app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id) # 1 use every 10s
async def wave(interaction: discord.Interaction):
    arduino.write(b'W')
    await interaction.response.send_message(f"👋 {interaction.user.display_name} sent a wave!")

@client.tree.command(name="love", description="Send fast blinks of love")
@app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id) # 1 use every 10s
async def love(interaction: discord.Interaction):
    arduino.write(b'L')
    await interaction.response.send_message(f"❤️ {interaction.user.display_name} is sending love!")

@client.tree.command(name="question", description="Send a pulse for a question")
@app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
async def question(interaction: discord.Interaction):
    arduino.write(b'Q')
    await interaction.response.send_message(f"❓ {interaction.user.display_name} has a question!")

# --- GLOBAL ERROR HANDLER ---
# This one function handles the "Rate Limit" message for ALL commands above
@client.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"⏳ Slow down, {interaction.user.display_name}! Try again in {error.retry_after:.1f}s.", 
            ephemeral=True # Only the spammer sees this
        )
    else:
        # Log other errors so you can see them in your terminal
        print(f"Command Error: {error}")

def main():
    # 4. Run the Bot using the hidden Token
    if TOKEN:
        client.run(TOKEN)
    else:
        print("❌ Error: No token found. Did you create the .env file?")

if __name__ == "__main__":
    main()

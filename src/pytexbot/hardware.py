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
ALLOWED_CHANNEL_ID = os.getenv('ALLOWED_CHANNEL_ID') # NEW: Re-load from .env

# 2. Setup Serial Connection Utility
__ARDUINO = None

def get_arduino():
    global __ARDUINO
    if __ARDUINO is None:
        try:
            # Only init when first needed
            __ARDUINO = serial.Serial(SERIAL_PORT, 9600, timeout=1)
            time.sleep(2) # Allow Arduino to reset
            print(f"✅ Connected to Arduino on {SERIAL_PORT}!")
        except Exception as e:
            print(f"❌ Hardware Error on {SERIAL_PORT}: {e}")
            return None
    return __ARDUINO

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
    if ALLOWED_CHANNEL_ID and str(interaction.channel.id) != str(ALLOWED_CHANNEL_ID):
        await interaction.response.send_message("❌ This command is not allowed in this channel.", ephemeral=True)
        return
    
    arduino = get_arduino()
    if arduino:
        arduino.write(b'W')
        await interaction.response.send_message(f"👋 {interaction.user.display_name} sent a wave!")
    else:
        await interaction.response.send_message("⚠️ Hardware not connected.", ephemeral=True)

@client.tree.command(name="love", description="Send fast blinks of love")
@app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id) # 1 use every 10s
async def love(interaction: discord.Interaction):
    if ALLOWED_CHANNEL_ID and str(interaction.channel.id) != str(ALLOWED_CHANNEL_ID):
        await interaction.response.send_message("❌ This command is not allowed in this channel.", ephemeral=True)
        return
    
    arduino = get_arduino()
    if arduino:
        arduino.write(b'L')
        await interaction.response.send_message(f"❤️ {interaction.user.display_name} is sending love!")
    else:
        await interaction.response.send_message("⚠️ Hardware not connected.", ephemeral=True)

@client.tree.command(name="question", description="Send a pulse for a question")
@app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
async def question(interaction: discord.Interaction):
    if ALLOWED_CHANNEL_ID and str(interaction.channel.id) != str(ALLOWED_CHANNEL_ID):
        await interaction.response.send_message("❌ This command is not allowed in this channel.", ephemeral=True)
        return
    
    arduino = get_arduino()
    if arduino:
        arduino.write(b'Q')
        await interaction.response.send_message(f"❓ {interaction.user.display_name} has a question!")
    else:
        await interaction.response.send_message("⚠️ Hardware not connected.", ephemeral=True)

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

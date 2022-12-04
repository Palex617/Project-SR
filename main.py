import asyncio
import os
import discord
from discord.ext import commands
import config

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='d!', intents=intents, application_id=config.APPLICATION)

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
    print("Slash commands syncing...")
    synced = await bot.tree.sync()
    print("Slash commands synced " + str(len(synced)) + " commands")
    print(f"{'':=^32}")
    print(f"{'READY': ^32}")
    print(f"{'':=^32}")

async def load():
    print('Setting up...')
    for file in os.listdir('./commands'):
            if file.endswith('.py'):
                await bot.load_extension(f'commands.{file[:-3]}')

async def main():
    await load() 
    await bot.start(config.TOKEN)

asyncio.run(main())
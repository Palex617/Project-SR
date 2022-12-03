import requests
import discord
from discord.ext import commands
from discord import app_commands

class Numbers(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Numbers cog loaded.')
    
    @app_commands.command(name="numberfact", description="number pls")
    async def number(self, interaction: discord.Interaction, number:str):
        response = requests.get(f'http://numbersapi.com/{number}')
        embed = discord.Embed(description=response.text)
        await interaction.response.send_message(embed=embed)
        print('Fact sent for number ' + number)

async def setup(bot):
    await bot.add_cog(Numbers(bot))
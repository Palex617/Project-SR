import discord
from discord.ext import commands
from discord import app_commands

class testButton(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Test Button cog loaded.')
    
    @app_commands.command(name="testbutton", description="this never works")
    async def testbutton(self, interaction: discord.Interaction):
        await interaction.response.send_message("This message is a test!", view=Buttons())

class Buttons(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
        
    @discord.ui.button(label="Button",style=discord.ButtonStyle.gray)
    async def gray_button(self,button:discord.ui.Button,interaction:discord.Interaction):
        await interaction.response.edit_message(content=f"This is an edited button response!")

async def setup(bot):
    await bot.add_cog(testButton(bot))
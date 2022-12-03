import discord
from discord.ui import Select, View
from discord.ext import commands
from discord import app_commands

class testMenu(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Menu Test cog loaded.')

    @app_commands.command(name="testmenu", description="please work")
    async def testmenu(self, interaction: discord.Interaction):
        select = Select(placeholder="Choose a weather!", options=[
            discord.SelectOption(label='Cloudy', emoji='⛅', description="Cloudy weather"),
            discord.SelectOption(label='Rainy', emoji='⛈️', description="It's raining")
        ])

        async def my_callback(interaction):
            await interaction.response.send_message(f"You chose: {select.values[0]}")
        select.callback = my_callback
        view = View()
        view.add_item(select)

        await interaction.response.send_message("This message is a test!", view=view)

async def setup(bot):
    await bot.add_cog(testMenu(bot))
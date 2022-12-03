import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View

class Register(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Register cog loaded.')

    @app_commands.command(name="register", description="Register your Genshin account")
    async def register(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Registration", 
            description = "Register your Genshin account info for commands!\n\n**Commands such as:**\n> `/profile` Displays your Genshin account\n> `/wishhistory` Shows your wish history\n> `/resin` Returns your current resin count",
            color=0xad5550)
        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/280430625872412693/60543c62566b6be7f90182ea1d6b80e7.png?size=256")

        await interaction.response.send_message(embed=embed, view=registerButtons(), ephemeral=True)

class registerButtons(discord.ui.View):
    def __init__(self, *, timeout = 180):
        super().__init__(timeout=timeout)

    @discord.ui.button(label = "Link UID", style = discord.ButtonStyle.blurple, emoji = "<a:poroPls:1034990868526018661>")
    async def firstButton(self, button:discord.ui.Button, interaction:discord.Interaction):
        await interaction.response.edit_message(view=uidButtons())
    @discord.ui.button(label = "Wish History", style = discord.ButtonStyle.blurple, emoji = "<:kms:889343329903464469>")
    async def secondButton(self, button:discord.ui.Button, interaction:discord.Interaction):
        await interaction.response.edit_message(view=uidButtons())
    @discord.ui.button(label = "Link HoYoLab", style = discord.ButtonStyle.blurple, emoji = "<:kms:889343329903464469>")
    async def thirdButton(self, button:discord.ui.Button, interaction:discord.Interaction):
        await interaction.response.edit_message(view=uidButtons())

class uidButtons(discord.ui.View):
    def __init__(self, *, timeout = 180):
        super().__init__(timeout=timeout)

    @discord.ui.button(label = "Go Back", style = discord.ButtonStyle.gray, emoji = "◀️")
    async def uidfirst_button(self, button:discord.ui.Button, interaction:discord.Interaction):
        await interaction.response.edit_message(view=registerButtons())

    @discord.ui.button(label = "Set UID", style = discord.ButtonStyle.blurple, emoji = "<:kms:889343329903464469>")
    async def uidsecond_button(self, button:discord.ui.Button, interaction:discord.Interaction):
        await interaction.response.edit_message(view=self)

async def setup(bot):
    await bot.add_cog(Register(bot))
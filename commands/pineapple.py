import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View, Button

class Pineapple(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Pineapple cog loaded.')
    
    @app_commands.command(name="pineapple", description="pineapple")
    async def Pineapple(self, interaction: discord.Interaction):
        print('Pineapple has been used')
        user = interaction.user

        embed = discord.Embed(title='Does pineapple belong on pizza?', description='Think long and hard about this...', color=0xFF6600)
        embed.set_image(url='https://www.vincenzosplate.com/wp-content/uploads/2021/10/610x350-Photo-7_861-How-to-Make-PINEAPPLE-PIZZA-Like-an-Italian-V2.jpg')
        buttonY = Button(label='Yes', style=discord.ButtonStyle.danger, emoji='<a:NOOOVanish:1092699690228781066>')
        buttonN = Button(label='No', style=discord.ButtonStyle.green)

        # kicks user from server
        async def button_callbackY(interaction): 
            embed.title = 'Does pineapple belong on pizza? No... it does not'
            embed.description = f'{user.display_name} has been taken care of...'
            embed.color = 0xf54242
            embed.set_image(url=None)
            await interaction.response.edit_message(embed=embed, view=None)
            #await discord.guild.kick(user)
            #await user.kick()

        # affirms user of the correct response
        async def button_callbackN(interaction):
            embed.title = 'Does pineapple belong on pizza? Correct! It does not!'
            embed.description = f'{user.display_name}\'s opinion is a fact and they are indeed based'
            embed.color = 0x05e326
            embed.set_image(url=None)
            await interaction.response.edit_message(embed=embed, view=None)

        buttonY.callback = button_callbackY
        buttonN.callback = button_callbackN
        view = View()
        view.add_item(buttonY)
        view.add_item(buttonN)
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Pineapple(bot))

# https://discordpy.readthedocs.io/en/stable/interactions/api.html?highlight=app_commands#discord.app_commands.command
    
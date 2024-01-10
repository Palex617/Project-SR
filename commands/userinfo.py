import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta, timezone

class userInfo(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('userInfo cog loaded.')
    
    @app_commands.command(name="userinfo", description="Returns user information") 
    async def userInfo(self, interaction:discord.Interaction, user:discord.Member=None):
        user = user or interaction.user
        userFetch = await interaction.client.fetch_user(user.id)

        embed = discord.Embed(title=f'{user.display_name}\'s information', color=user.color)
        embed.set_thumbnail(url=f'{user.avatar.url}')
        if userFetch.banner is not None:
            embed.set_image(url=f'{userFetch.banner.url}')

        fields = [('ID', user.id, False),
                  ('Username', user, True),
                  ('Top role', user.top_role.mention, True),
                  ('Status', user.status, True),
                  ('Activity', str(user.activity), True),
                  ('Account created', f'<t:{timestamp(user.created_at)}:f>', True),
                  ('Joined server', f'<t:{timestamp(user.joined_at)}:f>', True),
                  ('Roles:', roles(user.roles), True)]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        
        await interaction.response.send_message(embed=embed)

def timestamp(time):
    return int((time - datetime(1970, 1, 1, 0, 0, 0, 0, timezone.utc)) / timedelta(seconds=1))

def roles(roles):
    allRoles = '@everyone '
    for i in range(len(roles)):
        if i != 0:
            allRoles = allRoles + '<@&' + str(roles[i].id) + '> '
    return allRoles

async def setup(bot):
    await bot.add_cog(userInfo(bot))

# https://discordpy.readthedocs.io/en/stable/api.html#member
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View
from enkanetwork import EnkaNetworkAPI
import dictionaries.characterInfo

class Profile(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Terminal display of command loaded
    @commands.Cog.listener()
    async def on_ready(self):
        print('Profile cog loaded.')
    
    @app_commands.command(name='profile', description='Enter UID')
    async def questions(self, interaction:discord.Interaction, uid:str):
        client = EnkaNetworkAPI()
        
        async with client:
            # Grabbing player data from Enka.Network API
            data = await client.fetch_user(uid)
            
            # Returning imported dictionaries for character's name, element, icon name, and skin icon name
            charDict = dictionaries.characterInfo.charDict
                        
            # Defining fuctions to return hex color and emote from an element
            def elementColor(element):
                if element == "Anemo":
                    return 0x72e2c2
                elif element == "Cryo":
                    return 0xa0e9e5
                elif element == "Dendro":
                    return 0x23c18a
                elif element == "Electro":
                    return 0xa757cb
                elif element == "Geo":
                    return 0xe3b342
                elif element == "Hydro":
                    return 0x21e1eb
                elif element == "Pyro":
                    return 0xfe925d
                else:
                    return 0xffffff
            def elementEmote(element):
                if element == "Anemo":
                    return "<:anemo:1041200472104640532>"
                elif element == "Cryo":
                    return "<:cryo:1041200473128046592>"
                elif element == "Dendro":
                    return "<:dendro:1041200474138890250>"
                elif element == "Electro":
                    return "<:electro:1041200475258761296>"
                elif element == "Geo":
                    return "<:geo:1041200476672249876>"
                elif element == "Hydro":
                    return "<:hydro:1041200477896982599>"
                elif element == "Pyro":
                    return "<:pyro:1041200478928781352>"
                else:
                    return "⚪"
            embedcolor = elementColor(charDict.get(int(data.player.avatar.id)).get('element'))

            # Creating player info into an embed message
            embed = discord.Embed(title=data.player.nickname, color=embedcolor)
            embed.set_thumbnail(url=f"{data.player.avatar.icon.url}")
            embed.add_field(name='AR', value=data.player.level, inline=True)
            embed.add_field(name='WL', value=data.player.world_level, inline=True)
            embed.add_field(name='Abyss', value=f"{data.player.abyss_floor}-{data.player.abyss_room}", inline=True)
            embed.add_field(name='Signature', value=data.player.signature, inline=False)
            embed.set_footer(text='UID: ' + uid)
            
            # Making list of characters from player's profile and adding to embed
            characterList = ""
            charName = charDict.get(int(data.player.characters_preview[0].id)).get('name')
            charElement = charDict.get(int(data.player.characters_preview[0].id)).get('element')

            selectMenu = Select(placeholder="Choose a character!", options=[
                discord.SelectOption(label=charName, emoji=elementEmote(charElement))])

            for char in range(len(data.player.characters_preview)):
                charID = int(data.player.characters_preview[char].id)
                charName = data.player.characters_preview[char].name
                charElement = charDict.get(charID).get('element')
                if char != 0:
                    selectMenu.append_option(discord.SelectOption(label=charName, emoji=elementEmote(charElement)))
                if char == len(data.player.characters_preview):
                    characterList = f"{characterList}> {elementEmote(charElement)} {charName}"
                else:
                    characterList = f"{characterList}> {elementEmote(charElement)} {charName}\n"
            embed.add_field(name='Characters', value=characterList)
            
            # Setting up menu drop down
            async def charDetails(interaction):
                charName = selectMenu.values[0]
                charID = 0
                # Searching what character we have from name to get ID
                for ID in list(charDict):
                    if charDict.get(ID).get('name') == charName:
                        charID = ID
                charElement = charDict.get(charID).get('element')
                embedcolor = elementColor(charElement)

                # Finding the index of selected character
                index = 0
                for x in range(len(data.player.characters_preview)):
                    if charID == int(data.player.characters_preview[x].id):
                        index = x
                
                cons = data.characters[index].constellations_unlocked

                # Another embed
                charEmbed = discord.Embed(title=f"{data.player.nickname}'s C{cons} {charName}",
                    description=f"> **Level:** {data.characters[index].level}\n"
                                f"> **Friendship:** {data.characters[index].friendship_level}\n"
                                f"> **Weapon:** {data.characters[index].equipments[-1].detail.name}\n"
                                f"> **Max HP:** {data.characters[index].stats.FIGHT_PROP_MAX_HP.value:,.0f}\n"
                                f"> **Atk:** {data.characters[index].stats.FIGHT_PROP_CUR_ATTACK.value:,.0f}\n"
                                f"> **Def:** {data.characters[index].stats.FIGHT_PROP_CUR_DEFENSE.value:,.0f}\n"
                                f"> **EM:** {data.characters[index].stats.FIGHT_PROP_ELEMENT_MASTERY.value:,.0f}\n"
                                f"> **CR:** {data.characters[index].stats.FIGHT_PROP_CRITICAL.value*100:.1f} %\n"
                                f"> **CD:** {data.characters[index].stats.FIGHT_PROP_CRITICAL_HURT.value*100:.1f} %\n"
                                f"> **ER:** {data.characters[index].stats.FIGHT_PROP_CHARGE_EFFICIENCY.value*100:.1f} %",
                    color=embedcolor)
                charEmbed.set_thumbnail(url=f"{data.characters[index].image.icon.url}")
                charEmbed.set_footer(text='UID: ' + uid)
                await interaction.response.send_message(embed=charEmbed, ephemeral=False)
            selectMenu.callback = charDetails
            view = View()
            view.add_item(selectMenu)
            
            await interaction.response.send_message(embed=embed, view=view) # Sending embed message
            print(f"Profile displayed for user {uid}") # Confirm completion on terminal

async def setup(bot):
    await bot.add_cog(Profile(bot))
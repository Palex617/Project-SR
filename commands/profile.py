import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View
import requests
import json
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
        # Grabbing player data from Enka.Network API
        response = requests.get(f"https://enka.network/u/{uid}/__data.json")
        data = json.loads(response.text)
        playerInfo = data.get("playerInfo")
        
        # Returning imported dictionaries for character's name, element, icon name, and skin icon name
        charDict = dictionaries.characterInfo.charDict
        skinDict = dictionaries.characterInfo.skinDict
        
        # Returning url name and element of profile character icon
        profileAvatarId = playerInfo.get('profilePicture').get('avatarId')
        profileAvatarElement = charDict.get(profileAvatarId).get('element')
        profileAvatarIcon = charDict.get(profileAvatarId).get('icon')
        profileSkinId = playerInfo.get('profilePicture').get('costumeId')
        profileSkinIcon = skinDict.get(profileSkinId)
        profileAvatarIcon = profileAvatarIcon if profileSkinIcon is None else profileSkinIcon
        
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
        embedcolor = elementColor(profileAvatarElement)

        # Creating player info into an embed message
        embed = discord.Embed(title=playerInfo.get('nickname'), color=embedcolor)
        embed.set_thumbnail(url=f"https://enka.network/ui/UI_AvatarIcon_{profileAvatarIcon}.png")
        embed.add_field(name='AR', value=playerInfo.get('level'), inline=True)
        embed.add_field(name='WL', value=playerInfo.get('worldLevel'), inline=True)
        embed.add_field(name='Abyss', value=f"{playerInfo.get('towerFloorIndex')}-{playerInfo.get('towerLevelIndex')}", inline=True)
        embed.add_field(name='Signature', value=playerInfo.get('signature'), inline=False)
        embed.set_footer(text='UID: ' + uid)
        
        # Making list of characters from player's profile and adding to embed
        characterList = ""

        charID = playerInfo.get('showAvatarInfoList')[0].get('avatarId')
        charName = charDict.get(charID).get('name')
        charElement = charDict.get(charID).get('element')

        selectMenu = Select(placeholder="Choose a character!", options=[
            discord.SelectOption(label=charName, emoji=elementEmote(charElement))])

        for fav in range(len(playerInfo.get('showAvatarInfoList'))):
            charID = playerInfo.get('showAvatarInfoList')[fav].get('avatarId')
            charName = charDict.get(charID).get('name')
            charElement = charDict.get(charID).get('element')
            if fav != 0:
                selectMenu.append_option(discord.SelectOption(label=charName, emoji=elementEmote(charElement)))
            if fav == len(playerInfo.get('showAvatarInfoList')):
                characterList = f"{characterList}> {elementEmote(charElement)} {charName}"
            else:
                characterList = f"{characterList}> {elementEmote(charElement)} {charName}\n"
        embed.add_field(name='Characters', value=characterList)

        # Setting up menu drop down
        async def charDetails(interaction):
            charName = selectMenu.values[0]
            charkey = 0
            for key in list(charDict):
                if charDict.get(key).get('name') == charName:
                    charkey = key
            charElement = charDict.get(charkey).get('element')
            embedcolor = elementColor(charElement)
            profileAvatarIcon = charDict.get(charkey).get('icon')
            for x in range(len(data.get("playerInfo").get("showAvatarInfoList"))):
                if data.get("playerInfo").get("showAvatarInfoList")[x].get('avatarId') == charkey:
                    profileSkinId = data.get("playerInfo").get("showAvatarInfoList")[x].get('costumeId')
            profileSkinIcon = skinDict.get(profileSkinId)
            profileAvatarIcon = profileAvatarIcon if profileSkinIcon is None else profileSkinIcon

            # Finding the index of selected character in avatarInfoList
            index = 0
            for x in range(len(data.get("avatarInfoList"))):
                if charkey == data.get("avatarInfoList")[x].get('avatarId'):
                    index = x
            
            charInfo = data.get("avatarInfoList")[index]
            cons = len(charInfo.get('talentIdList')) if charInfo.get('talentIdList') is not None else 0

            # Another embed
            charEmbed = discord.Embed(title=f"{charName} C{cons}",
                description=f"> **Level:** {charInfo.get('propMap').get('4001').get('val')}\n"
                            f"> **Friendship:** {charInfo.get('fetterInfo').get('expLevel')}\n"
                            f"> **Weapon:** {charInfo.get('equipList')[-1].get('flat').get('icon')}\n"
                            f"> **Max HP:** {charInfo.get('fightPropMap').get('2000'):,.0f}\n"
                            f"> **Atk:** {charInfo.get('fightPropMap').get('2001'):,.0f}\n"
                            f"> **Def:** {charInfo.get('fightPropMap').get('2002'):,.0f}\n"
                            f"> **EM:** {charInfo.get('fightPropMap').get('28'):,.0f}\n"
                            f"> **CR:** {charInfo.get('fightPropMap').get('20')*100:.1f} %\n"
                            f"> **CD:** {charInfo.get('fightPropMap').get('22')*100:.1f} %\n"
                            f"> **ER:** {charInfo.get('fightPropMap').get('23')*100:.1f} %",
                color=embedcolor)
            charEmbed.set_thumbnail(url=f"https://enka.network/ui/UI_AvatarIcon_{profileAvatarIcon}.png")
            charEmbed.set_footer(text='UID: ' + uid)
            await interaction.response.send_message(embed=charEmbed, ephemeral=False)
        selectMenu.callback = charDetails
        view = View()
        view.add_item(selectMenu)
        
        await interaction.response.send_message(embed=embed, view=view) # Sending embed message
        print(f"Profile displayed for user {uid}") # Confirm completion on terminal

async def setup(bot):
    await bot.add_cog(Profile(bot))
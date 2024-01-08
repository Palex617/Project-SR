import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View
from PIL import Image, ImageDraw, ImageFont
import requests

class Profile(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Terminal display of command loaded
    @commands.Cog.listener()
    async def on_ready(self):
        print('Profile cog loaded.')
    
    @app_commands.command(name='profile', description='Enter UID')
    async def questions(self, interaction:discord.Interaction, uid:str):
        response = requests.get(f'https://enka.network/api/uid/{uid}')
        data = response.json()
        
        embedcolor = elementColor(charDict[data['playerInfo']['showAvatarInfoList'][0]['avatarId']]['element'])

        # Creating player info into an embed message
        embed = discord.Embed(title=data["playerInfo"]["nickname"], color=embedcolor)
        thumbnail = profilePic(data['playerInfo']['profilePicture'])
        file = discord.File(f"./assets/portrait/{thumbnail}.png", filename=f"{thumbnail}.png")
        embed.set_thumbnail(url=f'attachment://{thumbnail}.png')
        embed.add_field(name='AR', value=data["playerInfo"]["level"], inline=True)
        embed.add_field(name='WL', value=data["playerInfo"]["worldLevel"], inline=True)
        embed.add_field(name='Abyss', value=f"{data['playerInfo']['towerFloorIndex']}-{data['playerInfo']['towerLevelIndex']}", inline=True)
        embed.add_field(name='Signature', value=data["playerInfo"]["signature"], inline=False)
        embed.set_footer(text='UID: ' + uid)
    
        # Making list of characters from player's profile and adding to embed
        characterList = ""
        charName = charDictSilly[charDict[data['playerInfo']['showAvatarInfoList'][0]['avatarId']]['name']]
        charElement = charDict[data['playerInfo']['showAvatarInfoList'][0]['avatarId']]['element']

        selectMenu = Select(placeholder="Choose a character!", options=[
            discord.SelectOption(label=charName, emoji=elementEmote(charElement))])
        
        for char in range(len(data['playerInfo']['showAvatarInfoList'])):
            charID = int(data['playerInfo']['showAvatarInfoList'][char]['avatarId'])
            charName = charDictSilly[charDict[data['playerInfo']['showAvatarInfoList'][char]['avatarId']]['name']]
            charElement = charDict.get(charID).get('element')
            if char != 0:
                selectMenu.append_option(discord.SelectOption(label=charName, emoji=elementEmote(charElement)))
            if char == len(data['playerInfo']['showAvatarInfoList']):
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
                if charDictSilly.get(charDict.get(ID).get('name')) == charName:
                    charID = ID
            charElement = charDict.get(charID).get('element')
            embedcolor = elementColor(charElement)

            # Finding the index of selected character
            index = 0
            for x in range(len(data['playerInfo']['showAvatarInfoList'])):
                if charID == int(data['playerInfo']['showAvatarInfoList'][x]['avatarId']):
                    index = x
            
            # Finding number of cons of selected character
            if 'talentIdList' in data['avatarInfoList'][index]:
                cons = len(data["avatarInfoList"][index]["talentIdList"])
            else:
                cons = 0

            # Generating character card and saving file to directory
            characterCard(uid, index)

            # Another embed
            charEmbed = discord.Embed(title=f"{data['playerInfo']['nickname']}'s C{cons} {charName}", color=embedcolor)            
            file = discord.File("./showcase.png", filename="showcase.png")
            charEmbed.set_image(url='attachment://showcase.png')
            charEmbed.set_footer(text='UID: ' + uid)
            await interaction.response.send_message(embed=charEmbed, ephemeral=False, file=file)
        selectMenu.callback = charDetails
        view = View()
        view.add_item(selectMenu)
        
        # This gives error if user has a private profile. Weird behavior to have tbh
        await interaction.response.send_message(embed=embed, view=view, file=file) # Sending embed message
        print(f"Profile displayed for user {uid}") # Confirm completion on terminal

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
def characterCard(uid, index):
    response = requests.get(f'https://enka.network/api/uid/{uid}')
    data = response.json()

    avatarId = data["avatarInfoList"][index]["avatarId"]
    img = Image.open(f'./assets/namecards/{data["avatarInfoList"][index]["avatarId"]}.webp')
    img = img.convert("RGBA")
    imgalpha = Image.new('RGBA', img.size, (255, 255, 255, 0))
    splash = Image.open(f'./assets/splash art/{data["avatarInfoList"][index]["avatarId"]}.png')
    draw = ImageDraw.Draw(imgalpha)

    splash = splash.resize((570,570))
    img.paste(splash, (-107,-80), splash)

    draw.text((20,20), f'{charDictSilly[charDict[avatarId]["name"]]}', (255,255,255), font=ImageFont.truetype('./assets/font/zh-cn.ttf',18))
    draw.text((20,50), f'Lv. {data["avatarInfoList"][index]["propMap"]["4001"]["val"]}/{maxLvl[data["avatarInfoList"][index]["propMap"]["1002"]["val"]]}', (255,255,255), font=ImageFont.truetype('./assets/font/zh-cn.ttf',12))
    draw.text((20,70), f'Fr. {data["avatarInfoList"][index]["fetterInfo"]["expLevel"]}', (255,255,255), font=ImageFont.truetype('./assets/font/zh-cn.ttf',12))
    draw.text((20,374), f'{data["uid"]}', (255,255,255), font=ImageFont.truetype('./assets/font/zh-cn.ttf',12))
    
    # Weapon info
    weapon = Image.open(f'./assets/weapons/{data["avatarInfoList"][index]["equipList"][-1]["flat"]["icon"]}.png').convert("RGBA")
    weapon = weapon.resize((90,90))
    img.paste(weapon, (365,10), weapon)
    draw.text((462,20), f'{weapDict[data["avatarInfoList"][index]["equipList"][-1]["flat"]["icon"]]}', (255,255,255), font=ImageFont.truetype('./assets/font/zh-cn.ttf',15))
    
    # Opaque rectangle shapes
    draw.rounded_rectangle((461, 45, 521, 66), fill=(128,128,128,100), radius=3)
    draw.rounded_rectangle((528, 45, 601, 66), fill=(128,128,128,100), radius=3)
    draw.rounded_rectangle((461, 72, 485, 89), fill=(64,64,64,100), radius=3)
    draw.rounded_rectangle((496, 72, 572, 89), fill=(64,64,64,100), radius=3)
    
    # Weapon base atk icon
    iconatk = Image.open(f'./assets/icons/Atk.png')
    iconatk = iconatk.resize((18,18))
    imgalpha.paste(iconatk, (465,47), iconatk)
    
    # Weapon main stat icon
    iconWeaponMainStat = Image.open(f'{iconGet[data["avatarInfoList"][index]["equipList"][-1]["flat"]["weaponStats"][1]["appendPropId"]]}')
    iconWeaponMainStat = iconWeaponMainStat.resize((18,18))
    imgalpha.paste(iconWeaponMainStat, (533,47), iconWeaponMainStat)

    # Weapon stat text info
    draw.text((487,48), f'{data["avatarInfoList"][index]["equipList"][-1]["flat"]["weaponStats"][0]["statValue"]}', (255,255,255), font=ImageFont.truetype('./assets/font/zh-cn.ttf',14))
    draw.text((556,48), f'{data["avatarInfoList"][index]["equipList"][-1]["flat"]["weaponStats"][1]["statValue"]}', (255,255,255), font=ImageFont.truetype('./assets/font/zh-cn.ttf',14))
    refineId = "1" + str(data["avatarInfoList"][index]["equipList"][-1]["itemId"])
    draw.text((466,74), f'R{data["avatarInfoList"][index]["equipList"][-1]["weapon"]["affixMap"][refineId] + 1}', (234,212,172), font=ImageFont.truetype('./assets/font/zh-cn.ttf',12))
    draw.text((504,74), f'Lv. {data["avatarInfoList"][index]["equipList"][-1]["weapon"]["level"]}/{maxLvl[str(data["avatarInfoList"][index]["equipList"][-1]["weapon"]["promoteLevel"])]}', (255,255,255), font=ImageFont.truetype('./assets/font/zh-cn.ttf',12))
    
    # Character stat info
    def statValue(stat):
        if stat == 'HP':
            return f'{data["avatarInfoList"][index]["fightPropMap"]["2000"]:,.0f}'
        elif stat == 'ATK':
            return f'{data["avatarInfoList"][index]["fightPropMap"]["2001"]:,.0f}'
        elif stat == 'DEF':
            return f'{data["avatarInfoList"][index]["fightPropMap"]["2002"]:,.0f}'
        elif stat == 'Elemental Mastery':
            return f'{data["avatarInfoList"][index]["fightPropMap"]["28"]:,.0f}'
        elif stat == 'CRIT Rate':
            return f'{data["avatarInfoList"][index]["fightPropMap"]["20"]*100:.1f}%'
        elif stat == 'CRIT DMG':
            return f'{data["avatarInfoList"][index]["fightPropMap"]["22"]*100:.1f}%'
        elif stat == 'Energy Recharge':
            return f'{data["avatarInfoList"][index]["fightPropMap"]["23"]*100:.1f}%'
    i = 0
    for stat in ['HP', 'ATK', 'DEF', 'Elemental Mastery', 'CRIT Rate', 'CRIT DMG', 'Energy Recharge']:
        iconstat = Image.open(f'./assets/icons/{stat}.png')
        iconstat = iconstat.resize((16,16))
        img.paste(iconstat, (377,119+(i*30)), iconstat)
        draw.text((396,120+(i*30)), f'{stat}', (255,255,255), font=ImageFont.truetype('./assets/font/zh-cn.ttf',12))
        draw.text((580,120+(i*30)), statValue(stat), (255,255,255), font=ImageFont.truetype('./assets/font/zh-cn.ttf',12))
        i += 1
    
    element = charDict[avatarId]['element']
    elementDMG = 0
    physicalDMG = data["avatarInfoList"][index]["fightPropMap"]["30"]
    match (element): # Identifying what element our character is and saving their respective element dmg type
        case 'Pyro':
            elementDMG = data["avatarInfoList"][index]["fightPropMap"]["40"]
        case 'Electro':
            elementDMG = data["avatarInfoList"][index]["fightPropMap"]["41"]
        case 'Hydro':
            elementDMG = data["avatarInfoList"][index]["fightPropMap"]["42"]
        case 'Dendro':
            elementDMG = data["avatarInfoList"][index]["fightPropMap"]["43"]
        case 'Anemo':
            elementDMG = data["avatarInfoList"][index]["fightPropMap"]["44"]
        case 'Geo':
            elementDMG = data["avatarInfoList"][index]["fightPropMap"]["45"]
        case 'Cryo':
            elementDMG = data["avatarInfoList"][index]["fightPropMap"]["46"]
    
    if physicalDMG > 0:
        draw.text((396,330), f'Physical DMG Bonus', (255,255,255), font=ImageFont.truetype('./assets/font/zh-cn.ttf',12))
        draw.text((580,330), f'{physicalDMG*100:.1f}%', (255,255,255), font=ImageFont.truetype('./assets/font/zh-cn.ttf',12))
        iconstat = Image.open(f'./assets/icons/Physical.png')
        iconstat = iconstat.resize((16,16))
        img.paste(iconstat, (377,119+(i*30)), iconstat)
    else:
        draw.text((396,330), f'{element} DMG Bonus', (255,255,255), font=ImageFont.truetype('./assets/font/zh-cn.ttf',12))
        draw.text((580,330), f'{elementDMG*100:.1f}%', (255,255,255), font=ImageFont.truetype('./assets/font/zh-cn.ttf',12))
        iconstat = Image.open(f'./assets/icons/{element}.png')
        iconstat = iconstat.resize((16,16))
        img.paste(iconstat, (377,119+(i*30)), iconstat)

    # Artifact information
    for i in range(len(data["avatarInfoList"][index]["equipList"])-1):
        artifactcv = critvalue(data["avatarInfoList"][index]["equipList"][i]["flat"]["reliquarySubstats"])
        draw.rounded_rectangle((664, 10+(78*i), 845, 77+(78*i)), fill=(64,64,64,150), radius=3, outline=outlineColor(artifactcv), width=1)

        # BAD TRANSPARENCY MASK FIX: .convert("RGBA")
        artifact = Image.open(f'./assets/artifacts/{data["avatarInfoList"][index]["equipList"][i]["flat"]["icon"]}.png').convert("RGBA")
        artifact = artifact.resize((110,110))
        artifact = artifact.crop((25, 26, 180, 92))
        imgalpha.paste(artifact, (665,11+(78*i)), artifact)

        iconMainStat = Image.open(f'{iconGet[data["avatarInfoList"][index]["equipList"][i]["flat"]["reliquaryMainstat"]["mainPropId"]]}')
        iconMainStat = iconMainStat.resize((18,18))
        imgalpha.paste(iconMainStat, (744,20+(78*i)), iconMainStat)
        draw.text((763,20+(78*i)), f'{data["avatarInfoList"][index]["equipList"][0]["flat"]["reliquaryMainstat"]["statValue"]}', (255,255,255), font=ImageFont.truetype('./assets/font/zh-cn.ttf',15))
        draw.text((744,41+(78*i)), f'{artifactcv} cv', outlineColor(artifactcv), font=ImageFont.truetype('./assets/font/zh-cn.ttf',14))
        
    imgFinal = Image.alpha_composite(img, imgalpha)
    #imgFinal.show()
    imgFinal.save('showcase.png')
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
def critvalue(artifact):
    critValue = 0
    for line in range(len(artifact)):
        if artifact[line]['appendPropId'] == 'FIGHT_PROP_CRITICAL':
            critValue += 2*artifact[line]['statValue']
        elif artifact[line]['appendPropId'] == 'FIGHT_PROP_CRITICAL_HURT':
            critValue += artifact[line]['statValue']
    return round(critValue,1)
def outlineColor(artifactCV):
    if artifactCV < 15:
        return (140,140,140)
    elif artifactCV < 25:
        return (102,163,255)
    elif artifactCV < 35:
        return (194,102,255)
    elif artifactCV < 45:
        return (255,165,0)
    elif artifactCV < 50:
        return (255,217,0)
    else:
        return (0,255,255)  
def profilePic(pfp):
        # needs data['playerInfo']['profilePicture']
        if 'id' in pfp:
            return (profilePicture[pfp['id']])
        elif 'costumeId' in pfp:
            return (skinDict[pfp['costumeId']])
        else:
            return (charDict[pfp['avatarId']]['icon'])

charDict = {
    10000002:{'name':'Kamisato Ayaka','element':'Cryo','icon':'portrait_ayaka'},
    10000003:{'name':'Jean','element':'Anemo','icon':'portrait_jean'},
    10000005:{'name':'Traveler','element':'Multi','icon':'portrait_aether'},
    10000006:{'name':'Lisa','element':'Electro','icon':'portrait_lisa'},
    10000007:{'name':'Traveler','element':'Multi','icon':'portrait_lumine'},
    10000014:{'name':'Barbara','element':'Hydro','icon':'portrait_barbara'},
    10000015:{'name':'Kaeya','element':'Cryo','icon':'portrait_kaeya'},
    10000016:{'name':'Diluc','element':'Pyro','icon':'portrait_diluc'},
    10000020:{'name':'Razor','element':'Electro','icon':'portrait_razor'},
    10000021:{'name':'Amber','element':'Pyro','icon':'portrait_amber'},
    10000022:{'name':'Venti','element':'Anemo','icon':'portrait_venti'},
    10000023:{'name':'Xiangling','element':'Pyro','icon':'portrait_xiangling'},
    10000024:{'name':'Beidou','element':'Electro','icon':'portrait_beidou'},
    10000025:{'name':'Xingqiu','element':'Hydro','icon':'portrait_xingqiu'},
    10000026:{'name':'Xiao','element':'Anemo','icon':'portrait_xiao'},
    10000027:{'name':'Ningguang','element':'Geo','icon':'portrait_ningguang'},
    10000029:{'name':'Klee','element':'Pyro','icon':'portrait_klee'},
    10000030:{'name':'Zhongli','element':'Geo','icon':'portrait_zhongli'},
    10000031:{'name':'Fischl','element':'Electro','icon':'portrait_fischl'},
    10000032:{'name':'Bennett','element':'Pyro','icon':'portrait_bennett'},
    10000033:{'name':'Tartaglia','element':'Hydro','icon':'portrait_tartaglia'},
    10000034:{'name':'Noelle','element':'Geo','icon':'portrait_noelle'},
    10000035:{'name':'Qiqi','element':'Cryo','icon':'portrait_qiqi'},
    10000036:{'name':'Chongyun','element':'Cryo','icon':'portrait_chongyun'},
    10000037:{'name':'Ganyu','element':'Cryo','icon':'portrait_ganyu'},
    10000038:{'name':'Albedo','element':'Geo','icon':'portrait_albedo'},
    10000039:{'name':'Diona','element':'Cryo','icon':'portrait_diona'},
    10000041:{'name':'Mona','element':'Hydro','icon':'portrait_mona'},
    10000042:{'name':'Keqing','element':'Electro','icon':'portrait_keqing'},
    10000043:{'name':'Sucrose','element':'Anemo','icon':'portrait_sucrose'},
    10000044:{'name':'Xinyan','element':'Pyro','icon':'portrait_xinyan'},
    10000045:{'name':'Rosaria','element':'Cryo','icon':'portrait_rosaria'},
    10000046:{'name':'Hu Tao','element':'Pyro','icon':'portrait_hutao'},
    10000047:{'name':'Kaedehara Kazuha','element':'Anemo','icon':'portrait_kazuha'},
    10000048:{'name':'Yanfei','element':'Pyro','icon':'portrait_yanfei'},
    10000049:{'name':'Yoimiya','element':'Pyro','icon':'portrait_yoimiya'},
    10000050:{'name':'Thoma','element':'Pyro','icon':'portrait_thoma'},
    10000051:{'name':'Eula','element':'Cryo','icon':'portrait_eula'},
    10000052:{'name':'Raiden Shogun','element':'Electro','icon':'portrait_raiden'},
    10000053:{'name':'Sayu','element':'Anemo','icon':'portrait_sayu'},
    10000054:{'name':'Sangonomiya Kokomi','element':'Hydro','icon':'portrait_kokomi'},
    10000055:{'name':'Gorou','element':'Geo','icon':'portrait_gorou'},
    10000056:{'name':'Sara','element':'Electro','icon':'portrait_sara'},
    10000057:{'name':'Arataki Itto','element':'Geo','icon':'portrait_itto'},
    10000058:{'name':'Yae Miko','element':'Electro','icon':'portrait_yae'},
    10000059:{'name':'Shikanoin Heizou','element':'Anemo','icon':'portrait_heizou'},
    10000060:{'name':'Yelan','element':'Hydro','icon':'portrait_yelan'},
    10000061:{'name':'Kirara','element':'Dendro','icon':'portrait_kirara'},
    10000062:{'name':'Aloy','element':'Cryo','icon':'portrait_aloy'},
    10000063:{'name':'Shenhe','element':'Cryo','icon':'portrait_shenhe'},
    10000064:{'name':'Yun Jin','element':'Geo','icon':'portrait_yunjin'},
    10000065:{'name':'Kuki Shinobu','element':'Electro','icon':'portrait_kuki'},
    10000066:{'name':'Kamisato Ayato','element':'Hydro','icon':'portrait_ayato'},
    10000067:{'name':'Collei','element':'Dendro','icon':'portrait_collei'},
    10000068:{'name':'Dori','element':'Electro','icon':'portrait_dori'},
    10000069:{'name':'Tighnari','element':'Dendro','icon':'portrait_tighnari'},
    10000070:{'name':'Nilou','element':'Hydro','icon':'portrait_nilou'},
    10000071:{'name':'Cyno','element':'Electro','icon':'portrait_cyno'},
    10000072:{'name':'Candace','element':'Hydro','icon':'portrait_candace'},
    10000073:{'name':'Nahida','element':'Dendro','icon':'portrait_nahida'},
    10000074:{'name':'Layla','element':'Cryo','icon':'portrait_layla'},
    10000075:{'name':'Wanderer','element':'Anemo','icon':'portrait_wanderer'},
    10000076:{'name':'Faruzan','element':'Anemo','icon':'portrait_faruzan'},
    10000077:{'name':'Yaoyao','element':'Dendro','icon':'portrait_yaoyao'},
    10000078:{'name':'Alhaitham','element':'Dendro','icon':'portrait_alhaitham'},
    10000079:{'name':'Deyha','element':'Pyro','icon':'portrait_deyha'},
    10000080:{'name':'Mika','element':'Cryo','icon':'portrait_mika'},
    10000081:{'name':'Kaveh','element':'Dendro','icon':'portrait_kaveh'},
    10000082:{'name':'Baizhu','element':'Dendro','icon':'portrait_baizhu'},
    10000083:{'name':'Lynette','element':'Anemo','icon':'portrait_lynette'},
    10000084:{'name':'Lyney','element':'Pyro','icon':'portrait_lyney'},
    10000085:{'name':'Freminet','element':'Cryo','icon':'portrait_freminet'},
    10000086:{'name':'Wriothesley','element':'Cryo','icon':'portrait_wriothesley'},
    10000087:{'name':'Neuvillette','element':'Hydro','icon':'portrait_neuvillette'},
    10000088:{'name':'Charlotte','element':'Cryo','icon':'portrait_charloette'},
    10000089:{'name':'Furina','element':'Hydro','icon':'portrait_furina'},
    10000090:{'name':'Chevreuse','element':'Pyro','icon':'portrait_chevreuse'},
    10000091:{'name':'Navia','element':'Geo','icon':'portrait_navia'}
}
charDictSilly = {
    'Kamisato Ayaka':'Ayaya',
    'Jean':'Jen',
    'Traveler':'Loom',
    'Lisa':'Purple Librarian',
    'Traveler':'Loom',
    'Barbara':'Babs',
    'Kaeya':'Ice Bridge',
    'Diluc':'Batman',
    'Razor':'Wolfboy',
    'Amber':'Ambur',
    'Venti':'Barsibato',
    'Xiangling':'Cooking Girl',
    'Beidou':'Baedou',
    'Xingqiu':'Waterboy',
    'Xiao':'Pogoman',
    'Ningguang':'Richlady',
    'Klee':'Terror Tot',
    'Zhongli':'John Lee',
    'Fischl':'Purple Chicken',
    'Bennett':'Benedict',
    'Tartaglia':'Taglietelle',
    'Noelle':'Battle Maid',
    'Qiqi':'Dead Kid',
    'Chongyun':'Brainfreeze',
    'Ganyu':'Goat',
    'Albedo':'Susbedo',
    'Diona':'Diano',
    'Mona':'Puddle',
    'Keqing':'Kequeen',
    'Sucrose':'Sugar',
    'Xinyan':'Rocker Chick',
    'Rosaria':'Weird Nun',
    'Hu Tao':'Who?',
    'Kaedehara Kazuha':'Kazoo',
    'Yanfei':'Lawyer',
    'Yoimiya':'Pewpew',
    'Thoma':'Male Waifu',
    'Eula':'Vengeance',
    'Raiden Shogun':'Raisin',
    'Sayu':'Sayunara',
    'Sangonomiya Kokomi':'Kokofish',
    'Gorou':'Grr',
    'Sara':'Simp',
    'Arataki Itto':'Bullchucker',
    'Yae Miko':'Yay',
    'Shikanoin Heizou':'One Punch',
    'Yelan':'Lady Sonic',
    'Aloy':'Junkmail',
    'Shenhe':'Cool Auntie',
    'Yun Jin':'Opera',
    'Kuki Shinobu':'Cookie',
    'Kamisato Ayato':'Bobbaman',
    'Collei':'Colliflowa',
    'Dori':'Door',
    'Tighnari':'Big Ears',
    'Nilou':'Niloo',
    'Cyno':'Yugino',
    'Candace':'Candeez',
    'Nahida':'Nihido',
    'Layla':'Lala',
    'Wanderer':'Scaradook',
    'Faruzan':'Teach',
    'Yaoyao':'Bell Head',
    'Alhaitham':'Muscle Nerd',
    'Deyha':'6-Pack Cat',
    'Mika':'Bird Boy',
    'Kaveh':'Kevin',
    'Baizhu':'Dr Snek',
    'Kirara':'Box Cat',
    'Lyney':'Magical Grr',
    'Lynette':'Deadpan Catgirl',
    'Freminet':'Scuba',
    'Wriothesley':'Ice Punchy Wolfman',
    'Neuvillette':'Judge Hydropump',
    'Furina':'Cutting Board',
    'Charlotte':'Lawyer Clone',
    'Navia':'Crybaby',
    'Chevreuse':'Chevreuse'
}
profilePicture = {
    1: "portrait_aether",
	2: "portrait_lumine",
	100: "portrait_amber",
	101: "portrait_ambercostumewic",
	200: "portrait_kaeya",
	201: "portrait_kaeyacostumedancer",
	300: "portrait_lisa",
	301: "portrait_lisacostumestudentin",
	400: "portrait_barbara",
	401: "portrait_barbaracostumesummertime",
	500: "portrait_razor",
	600: "portrait_xiangling",
	700: "portrait_beidou",
	800: "portrait_xingqiu",
	900: "portrait_ningguang",
	901: "portrait_ningguangcostumefloral",
	1000: "portrait_fischl",
	1001: "portrait_fischlcostumehighness",
	1100: "portrait_bennett",
	1200: "portrait_noelle",
	1300: "portrait_chongyun",
	1400: "portrait_sucrose",
	1500: "portrait_jean",
	1501: "portrait_jeancostumewic",
	1502: "portrait_jeancostumesea",
	1600: "portrait_diluc",
	1601: "portrait_diluccostumeflamme",
	1700: "portrait_qiqi",
	1800: "portrait_mona",
	1801: "portrait_monacostumewic",
	1900: "portrait_keqing",
	1901: "portrait_keqingcostumefeather",
	2000: "portrait_venti",
	2100: "portrait_klee",
	2101: "portrait_kleecostumewitch",
	2200: "portrait_diona",
	2300: "portrait_tartaglia",
	2400: "portrait_xinyan",
	2500: "portrait_zhongli",
	2600: "portrait_albedo",
	2700: "portrait_ganyu",
	2800: "portrait_xiao",
	2900: "portrait_hutao",
	3000: "portrait_rosaria",
	3001: "portrait_rosariacostumewic",
	3100: "portrait_yanfei",
	3200: "portrait_eula",
	3300: "portrait_kazuha",
	3400: "portrait_ayaka",
	3401: "portrait_ayakacostumefruhling",
	3500: "portrait_sayu",
	3600: "portrait_yoimiya",
	3700: "portrait_aloy",
	3800: "portrait_sara",
	3900: "portrait_raiden",
	4000: "portrait_kokomi",
	4100: "portrait_thoma",
	4200: "portrait_gorou",
	4300: "portrait_itto",
	4400: "portrait_yunjin",
	4500: "portrait_shenhe",
	4600: "portrait_yae",
	4700: "portrait_ayato",
	4800: "portrait_yelan",
	4900: "portrait_kuki",
	5000: "portrait_heizou",
	5100: "portrait_collei",
	5200: "portrait_tighnari",
	5300: "portrait_dori",
	5400: "portrait_candace",
	5500: "portrait_cyno",
	5600: "portrait_nilou",
	5700: "portrait_nahida",
	5800: "portrait_layla",
	5900: "portrait_faruzan",
	6000: "portrait_wanderer",
	6100: "portrait_yaoyao",
	6200: "portrait_alhaitham",
	6300: "portrait_dehya",
	6400: "portrait_mika",
	6500: "portrait_kaveh",
	6600: "portrait_baizhu",
	6700: "portrait_kirara",
	6800: "portrait_lynette",
	6900: "portrait_lyney",
	7000: "portrait_freminet",
	7100: "portrait_neuvillette",
	7200: "portrait_wriothesley",
	7300: "portrait_charlotte",
	7400: "portrait_furina",
	7500: "portrait_navia",
	7600: "portrait_chevreuse",
	99999: "portrait_ambor"
}
weapDict = {
    'UI_EquipIcon_Sword_Blunt':'Dull Blade', # sword
    'UI_EquipIcon_Sword_Silver':'Silver Sword',
    'UI_EquipIcon_Sword_Steel':'Cool Steel',
    'UI_EquipIcon_Sword_Dawn':'Harbinger of Dawn',
    'UI_EquipIcon_Sword_Traveler':'Traveler\'s Handy Sword',
    'UI_EquipIcon_Sword_Darker':'Dark Iron Sword',
    'UI_EquipIcon_Sword_Sashimi':'Fillet Blade',
    'UI_EquipIcon_Sword_Mitsurugi':'Skyrider Sword',
    'UI_EquipIcon_Sword_Zephyrus':'Favonius Sword',
    'UI_EquipIcon_Sword_Troupe':'The Flute',
    'UI_EquipIcon_Sword_Fossil':'Sacrificial Sword',
    'UI_EquipIcon_Sword_Theocrat':'Royal Longsword',
    'UI_EquipIcon_Sword_Rockkiller':'Lion\'s Roar',
    'UI_EquipIcon_Sword_Proto':'Prototype Rancour',
    'UI_EquipIcon_Sword_Exotic':'Iron Sting',
    'UI_EquipIcon_Sword_Blackrock':'Blackcliff Longsword',
    'UI_EquipIcon_Sword_Bloodstained':'The Black Sword',
    'UI_EquipIcon_Sword_Outlaw':'The Alley Flash',
    'UI_EquipIcon_Sword_Psalmus':'Sword of Descension',
    'UI_EquipIcon_Sword_Magnum':'Festering Desire',
    'UI_EquipIcon_Sword_Bakufu':'Amenoma Kageuchi',
    'UI_EquipIcon_Sword_Opus':'Cinnabar Spindle',
    'UI_EquipIcon_Sword_Youtou':'Kagotsurube Isshin',
    'UI_EquipIcon_Sword_Arakalari':'Sapwood Blade',
    'UI_EquipIcon_Sword_Pleroma':'Xiphos\' Moonlight',
    'UI_EquipIcon_Sword_Boreas':'Wolf-Fang',
    'UI_EquipIcon_Sword_Vorpal':'Finale of the Deep',
    'UI_EquipIcon_Sword_Machination':'Flueve Cendre Ferryman',
    'UI_EquipIcon_Sword_Mechanic':'The Dockhand\'s Assistant',
    'UI_EquipIcon_Sword_Purewill':'Sword of Narzissenkruez',
    'UI_EquipIcon_Sword_Kasabouzu':'Toukabou Shigure',
    'UI_EquipIcon_Sword_Falcon':'Aquila Favonia',
    'UI_EquipIcon_Sword_Dvalin':'Skyward Blade',
    'UI_EquipIcon_Sword_Widsith':'Freedom-Sworn',
    'UI_EquipIcon_Sword_Kunwu':'Summit Shaper',
    'UI_EquipIcon_Sword_Morax':'Primordial Jade Cutter',
    'UI_EquipIcon_Sword_Narukami':'Mistsplitter Reforged',
    'UI_EquipIcon_Sword_Amenoma':'Haran Geppaku Futsu',
    'UI_EquipIcon_Sword_Deshret':'Key of Khaj-Nisut',
    'UI_EquipIcon_Sword_Ayus':'Light of Foliar Incision',
    'UI_EquipIcon_Sword_Regalis':'Spendor of Tranquil Waters',
    'UI_EquipIcon_Pole_Gewalt':'Beginner\'s Protector', # polearm
    'UI_EquipIcon_Pole_Rod':'Iron Point',
    'UI_EquipIcon_Pole_Ruby':'White Tassel',
    'UI_EquipIcon_Pole_Halberd':'Halberd',
    'UI_EquipIcon_Pole_Noire':'Black Tassel',
    'UI_EquipIcon_Pole_Stardust':'Dragon\'s Bane',
    'UI_EquipIcon_Pole_Proto':'Prototype Starglitter',
    'UI_EquipIcon_Pole_Exotic':'Crescent Pike',
    'UI_EquipIcon_Pole_Blackrock':'Blackcliff Pole',
    'UI_EquipIcon_Pole_Gladiator':'Deathmatch',
    'UI_EquipIcon_Pole_Lapis':'Lithic Spear',
    'UI_EquipIcon_Pole_Zephyrus':'Favonius Lance',
    'UI_EquipIcon_Pole_Theocrat':'Royal Spear',
    'UI_EquipIcon_Pole_Everfrost':'Dragonspine Spear',
    'UI_EquipIcon_Pole_Bakufu':'Kitain Cross Spear',
    'UI_EquipIcon_Pole_Mori':'The Catch',
    'UI_EquipIcon_Pole_Maria':'Wavebreaker\'s Fin',
    'UI_EquipIcon_Pole_Arakalari':'Moonpiercer',
    'UI_EquipIcon_Pole_Windvane':'Missive Windspear',
    'UI_EquipIcon_Pole_Shanty':'Ballad of the Fjords',
    'UI_EquipIcon_Pole_Vorpal':'Rightful Reward',
    'UI_EquipIcon_Pole_Mechanic':'Prospector\'s Drill',
    'UI_EquipIcon_Pole_Homa':'Staff of Homa',
    'UI_EquipIcon_Pole_Dvalin':'Skyward Spine',
    'UI_EquipIcon_Pole_Kunwu':'Vortex Vanquisher',
    'UI_EquipIcon_Pole_Morax':'Primordial Jade Winged-Spear',
    'UI_EquipIcon_Pole_Santika':'Calamity Queller',
    'UI_EquipIcon_Pole_Narukami':'Engulfing Lightning',
    'UI_EquipIcon_Pole_Deshret':'Staff of the Scarlet Sands',
    'UI_EquipIcon_Catalyst_Apprentice':'Apprentice\'s Notes', # catalyst
    'UI_EquipIcon_Catalyst_Pocket':'Pocket Grimoire',
    'UI_EquipIcon_Catalyst_Intro':'Magic Guide',
    'UI_EquipIcon_Catalyst_Pulpfic':'Thrilling Tales of Dragon Slayers',
    'UI_EquipIcon_Catalyst_Lightnov':'Otherworldly Story',
    'UI_EquipIcon_Catalyst_Jade':'Emerald Orb',
    'UI_EquipIcon_Catalyst_Phoney':'Twin Nephrite',
    'UI_EquipIcon_Catalyst_Zephyrus':'Favonius Codex',
    'UI_EquipIcon_Catalyst_Troupe':'The Widsith',
    'UI_EquipIcon_Catalyst_Fossil':'Sacrificial Fragments',
    'UI_EquipIcon_Catalyst_Theocrat':'Royal Grimoire',
    'UI_EquipIcon_Catalyst_Resurrection':'Solar Pearl',
    'UI_EquipIcon_Catalyst_Proto':'Prototype Amber',
    'UI_EquipIcon_Catalyst_Exotic':'Mappa Mare',
    'UI_EquipIcon_Catalyst_Blackrock':'Blackcliff Agate',
    'UI_EquipIcon_Catalyst_Truelens':'Eye of Perception',
    'UI_EquipIcon_Catalyst_Outlaw':'Wine and Song',
    'UI_EquipIcon_Catalyst_Everfrost':'Frostbearer',
    'UI_EquipIcon_Catalyst_Ludiharpastum':'Dodoco Tales',
    'UI_EquipIcon_Catalyst_Bakufu':'Hakushin Ring',
    'UI_EquipIcon_Catalyst_Jyanome':'Oathsworn Eye',
    'UI_EquipIcon_Catalyst_Pleroma':'Wandering Evenstar',
    'UI_EquipIcon_Catalyst_Arakalari':'Fruit of Fulfillment',
    'UI_EquipIcon_Catalyst_Yue':'Sacrificial Jade',
    'UI_EquipIcon_Catalyst_Vorpal':'Flowing Purity',
    'UI_EquipIcon_Catalyst_DandelionPoem':'Ballad of the Boundless Blue',
    'UI_EquipIcon_Catalyst_Dvalin':'Skyward Atlas',
    'UI_EquipIcon_Catalyst_Fourwinds':'Lost Prayer',
    'UI_EquipIcon_Catalyst_Kunwu':'Memory of Dust',
    'UI_EquipIcon_Catalyst_Morax':'Jadefall\'s Splendor',
    'UI_EquipIcon_Catalyst_Kaleido':'Everlasting Moonglow',
    'UI_EquipIcon_Catalyst_Narukami':'Kagura\'s Verity',
    'UI_EquipIcon_Catalyst_Ayus':'A Thousand Floating Dreams',
    'UI_EquipIcon_Catalyst_Alaya':'Tulaytullah\'s Rememberance',
    'UI_EquipIcon_Catalyst_Wheatley':'Cashflow Supervision',
    'UI_EquipIcon_Catalyst_Iudex':'Tome of the Eternal Flow',
    'UI_EquipIcon_Bow_Hunters':'Hunter\'s Bow', # bow
    'UI_EquipIcon_Bow_Old':'Seasoned Hunter\'s Bow',
    'UI_EquipIcon_Bow_Crowfeather':'Raven Bow',
    'UI_EquipIcon_Bow_Arjuna':'Sharpshooter\'s Oath',
    'UI_EquipIcon_Bow_Curve':'Recurve Bow',
    'UI_EquipIcon_Bow_Sling':'Slingshot',
    'UI_EquipIcon_Bow_Msg':'Messenger',
    'UI_EquipIcon_Bow_Zephyrus':'Favonius Warbow',
    'UI_EquipIcon_Bow_Troupe':'The Stringless',
    'UI_EquipIcon_Bow_Fossil':'Sacrificial Bow',
    'UI_EquipIcon_Bow_Theocrat':'Royal Bow',
    'UI_EquipIcon_Bow_Recluse':'Rust',
    'UI_EquipIcon_Bow_Proto':'Prototype Crescent',
    'UI_EquipIcon_Bow_Exotic':'Compound Bow',
    'UI_EquipIcon_Bow_Blackrock':'Blackcliff Warbow',
    'UI_EquipIcon_Bow_Viridescent':'The Viridescent Hunt',
    'UI_EquipIcon_Bow_Outlaw':'Alley Hunter',
    'UI_EquipIcon_Bow_Fallensun':'Fading Twilight',
    'UI_EquipIcon_Bow_Nachtblind':'Mitternachts Walts',
    'UI_EquipIcon_Bow_Fleurfair':'Windblume Ode',
    'UI_EquipIcon_Bow_Bakufu':'Hamayumi',
    'UI_EquipIcon_Bow_Predator':'Predator',
    'UI_EquipIcon_Bow_Maria':'Mouun\'s Moon',
    'UI_EquipIcon_Bow_Arakalari':'King\'s Squire',
    'UI_EquipIcon_Bow_Fin':'End of the Line',
    'UI_EquipIcon_Bow_Ibis':'Ibis Piercer',
    'UI_EquipIcon_Bow_Gurabad':'Scion of the Blazing Sun',
    'UI_EquipIcon_Bow_Vorpal':'Song of Stillness',
    'UI_EquipIcon_Bow_Mechanic':'Range Gauge',
    'UI_EquipIcon_Bow_Dvalin':'Skyward Harp',
    'UI_EquipIcon_Bow_Amos':'Amos\' Bow',
    'UI_EquipIcon_Bow_Widsith':'Elegy for the End',
    'UI_EquipIcon_Bow_Worldbane':'Polar Star',
    'UI_EquipIcon_Bow_Kirin':'Aqua Simulacra',
    'UI_EquipIcon_Bow_Narukami':'Thundering Pulse',
    'UI_EquipIcon_Bow_Ayus':'Hunter\'s Path',
    'UI_EquipIcon_Bow_Pledge':'The First Great Magic',
    'UI_EquipIcon_Claymore_Aniki':'Waster Greatsword', # claymore
    'UI_EquipIcon_Claymore_Oyaji':'Old Merc\'s Pal',
    'UI_EquipIcon_Claymore_Glaive':'Ferrous Shadow',
    'UI_EquipIcon_Claymore_Siegfry':'Bloodtainted Greatsword',
    'UI_EquipIcon_Claymore_Tin':'White Iron Greatsword',
    'UI_EquipIcon_Claymore_Reasoning':'Debate Club',
    'UI_EquipIcon_Claymore_Mitsurugi':'Skyrider Greatsword',
    'UI_EquipIcon_Claymore_Zephyrus':'Favonius Greatsword',
    'UI_EquipIcon_Claymore_Troupe':'The Bell',
    'UI_EquipIcon_Claymore_Fossil':'Sacrificial Greatsword',
    'UI_EquipIcon_Claymore_Theocrat':'Royal Greatsword',
    'UI_EquipIcon_Claymore_Perdue':'Rainslasher',
    'UI_EquipIcon_Claymore_Proto':'Prototype Archaic',
    'UI_EquipIcon_Claymore_Exotic':'Whiteblind',
    'UI_EquipIcon_Claymore_Blackrock':'Blackcliff Slasher',
    'UI_EquipIcon_Claymore_Kione':'Serpent Spine',
    'UI_EquipIcon_Claymore_Lapis':'Lithic Blade',
    'UI_EquipIcon_Claymore_Dragonfell':'Snow-Tombed Starsilver',
    'UI_EquipIcon_Claymore_MillenniaTuna':'Luxurious Sea-Lord',
    'UI_EquipIcon_Claymore_Bakufu':'Katsuragikiri Nagamasa',
    'UI_EquipIcon_Claymore_Pleroma':'Makhaira Aquamarine',
    'UI_EquipIcon_Claymore_Maria':'Akuoumaru',
    'UI_EquipIcon_Claymore_Arakalari':'Forest Regalia',
    'UI_EquipIcon_Claymore_Fleurfair':'Mailed Flower',
    'UI_EquipIcon_Claymore_BeastTamer':'Talking Stick',
    'UI_EquipIcon_Claymore_Vorpal':'Tidal Shadow',
    'UI_EquipIcon_Claymore_Champion':'\"Ultimate Overload\'s Mega Magic Sword\"',
    'UI_EquipIcon_Claymore_Mechanic':'Portable Power Saw',
    'UI_EquipIcon_Claymore_Dvalin':'Skyward Pride',
    'UI_EquipIcon_Claymore_Wolfmound':'Wolf\'s Gravestone',
    'UI_EquipIcon_Claymore_Widsith':'Song of Broken Pines',
    'UI_EquipIcon_Claymore_Kunwu':'The Unforged',
    'UI_EquipIcon_Claymore_Itadorimaru':'Redhorn Stonethresher',
    'UI_EquipIcon_Claymore_Deshret':'Beacon of the Reed Sea',
    'UI_EquipIcon_Claymore_GoldenVerdict':'Verdict'
}
iconGet = {
    'FIGHT_PROP_ATTACK_PERCENT':'./assets/icons/ATK Percent.png',
    'FIGHT_PROP_ATTACK':'./assets/icons/ATK.png',
    'FIGHT_PROP_CRITICAL_HURT':'./assets/icons/CRIT DMG.png',
    'FIGHT_PROP_CRITICAL':'./assets/icons/CRIT Rate.png',
    'FIGHT_PROP_DEFENSE':'./assets/icons/DEF.png',
    'FIGHT_PROP_DEFENSE_PERCENT':'./assets/icons/DEF Percent.png',
    'FIGHT_PROP_ELEMENT_MASTERY':'./assets/icons/Elemental Mastery.png',
    'FIGHT_PROP_CHARGE_EFFICIENCY':'./assets/icons/Energy Recharge.png',
    'FIGHT_PROP_HP':'./assets/icons/HP.png',
    'FIGHT_PROP_HP_PERCENT':'./assets/icons/HP Percent.png',
    'FIGHT_PROP_WIND_ADD_HURT':'./assets/icons/Anemo.png',
    'FIGHT_PROP_ICE_ADD_HURT':'./assets/icons/Cryo.png',
    'FIGHT_PROP_GRASS_ADD_HURT':'./assets/icons/Dendro.png',
    'FIGHT_PROP_ELEC_ADD_HURT':'./assets/icons/Electro.png',
    'FIGHT_PROP_ROCK_ADD_HURT':'./assets/icons/Geo.png',
    'FIGHT_PROP_WATER_ADD_HURT':'./assets/icons/Hydro.png',
    'FIGHT_PROP_FIRE_ADD_HURT':'./assets/icons/Pyro.png',
    'FIGHT_PROP_PHYSICAL_ADD_HURT':'./assets/icons/Physical.png',
    'FIGHT_PROP_HEAL_ADD':'./assets/icons/Healing.png'
}
maxLvl = {
        '0': '20',
        '1': '40',
        '2': '50',
        '3': '60',
        '4': '70',
        '5': '80',
        '6': '90'
}
skinDict = {
    200301:'portrait_jeancostumesea',
    200302:'portrait_jeancostumewic',
    201401:'portrait_barbaracostumesummertime',
    201601:'portrait_diluccostumeflamme',
    202101:'portrait_ambercostumewic',
    202701:'portrait_ningguangcostumefloral',
    203101:'portrait_fischlcostumehighness',
    204101:'portrait_monacostumewic',
    204201:'portrait_keqingcostumefeather',
    204501:'portrait_rosariacostumewic',
    200201:'portrait_ayakacostumefruhling',
    200601:'portrait_lisacostumestudentin',
    202901:'portrait_kleecostumewitch',
    201501:'portrait_kaeyacostumedancer'
}

async def setup(bot):
    await bot.add_cog(Profile(bot))
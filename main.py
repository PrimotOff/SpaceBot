import discord
import io
import keep_alive
import requests
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
discordintents = discord.Intents(messages=True, guilds=True)
from io import BytesIO
import random
import datetime
import asyncio
import wikipedia
import random
import os
import dateutil.parser
from dotenv import load_dotenv
from discord import Spotify
import sqlite3

client = commands.Bot(command_prefix='!', intents=discord.Intents.all())

connection = sqlite3.connect('server.db')
cursor = connection.cursor()

token = os.environ.get("DISCORD_BOT_SECRET")

@client.remove_command('help')



@client.event
async def on_ready():
    guilds = await client.fetch_guilds(limit = None).flatten()
    await client.change_presence(activity=discord.Activity(application_id=778958437631131690, type=discord.ActivityType.playing, name=f'за {len(guilds)} серверами.', state='http://spacebotapp.ru/', details=f'Type !help to view commands', assets={'large_image': 'avatar', 'large_image_text': 'SpaceBot'}))
    print("Bot connected")
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        serverid INT,
        name TEXT,
        id INT,
        cash BIGINT,
        rep INT,
        bank INT
        )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS shop (
        role_id INT,
        id INT,
        cost BIGINT
    )""")
    connection.commit()
    print("Table +")
    
#@client.event
#async def on_message(message):
#    if cursor.execute(f"SELECT id FROM users WHERE id = {ctx.author.id} AND serverid = {ctx.author.guild.id}").fetchone() is None:
#        cursor.execute(f"INSERT INTO users VALUES ({ctx.author.guild.id}, '{ctx.author}', {ctx.author.id}, {0}, {0}, {0})")
#        connection.commit()
#    else:
#        pass

@client.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name = 'verify')
    await member.add_roles(role)
	#channel = client.get_channel(name = "welcome")
    channel=discord.utils.get(member.guild.channels, name="welcome")
    url = str(member.avatar_url)[:-10]
    url = requests.get(url,stream = True)
    avatar = Image.open(io.BytesIO(url.content))
    welcome = Image.open('./assets/hi.png')
    welcome = welcome.convert('RGBA')
    avatar = avatar.convert('RGBA')
    avatar = avatar.resize((500,500))
    mask = Image.new('L',(1500,1500),0)
    draw = ImageDraw.Draw(mask)
    idraw = ImageDraw.Draw(welcome)
    name = member.name
    tag = member.discriminator
    at = member.created_at
    headline = ImageFont.truetype('./assets/font.ttf', size=70)
    headline2 = ImageFont.truetype('./assets/font.ttf', size=70)
    idraw.text((900, 750), f'{name}#{tag}',anchor="ms", font=headline, fill='#FFFFFF')
    idraw.text((900, 950), f'Создан {at}' [:-15],anchor="ms", font=headline2, fill='#FFFFFF')
    draw.ellipse((0,0) + (1500,1500),fill = 255)
    mask = mask.resize((500,500))
    avatar.putalpha(mask)
    welcome = welcome.resize((1800,1100))
    welcome.paste(avatar,(650,50),avatar)
    _buffer = io.BytesIO()
    welcome.save(_buffer,"png")
    _buffer.seek(0)
    await channel.send(file = discord.File(fp = _buffer,filename = f'{member.name}welcome.png'))
    await channel.send(f"{member.mention} добро пожаловать на сервер {member.guild.name}!")
    await member.send(file = discord.File(filename = f'{member.name}welcome.png'))
    await member.send(f"{member.mention} добро пожаловать на сервер {member.guild.name}!")
	

@client.command(aliases=['c', 'с', 'клеар', 'очистить'])
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=2):
	await ctx.channel.purge(limit=amount)

	emb = discord.Embed(title='clear', color=discord.Colour.green(), timestamp = ctx.message.created_at)
	emb.set_footer(text = f'{client.user.name} © 2021 | Все права защищены', icon_url = client.user.avatar_url)
	emb.add_field(name = 'Удалено сообщений:',value=f'__{amount}__')

	await ctx.send(embed=emb)

@client.command()
@commands.has_permissions(kick_members=True)
async def mute(ctx, member:discord.Member, duration, *, reason=None):
    if member == None:
        await ctx.send(f"{ctx.author.mention} укажите ```пользователь```")
    else:
        unit = duration[-1]
        print(f'{unit}')
        if unit == 'с':
            time = int(duration[:-1])
            longunit = 'секунд'
        elif unit == 'м':
            time = int(duration[:-1]) * 60
            longunit = 'минут'
        elif unit == 'ч':
            time = int(duration[:-1]) * 60 * 60
            longunit = 'часов'
        else:
            await ctx.send('Неправильно! Пиши `c`, `м`, `ч`')
            return
        emb = discord.Embed(title='Mute', color=discord.Colour.green(), timestamp =     ctx.message.created_at)
        emb.set_footer(text = f'{client.user.name} © 2021 | Все права защищены',    icon_url = client.user.avatar_url)
        emb.add_field(name='**модератор**', value= f'{ctx.author.mention}')
        emb.add_field(name='**замьчен**', value= f'{member.mention}')
        emb.add_field(name='**причина**', value= f'{reason}')
        emb.add_field(name='**время**', value= f'{duration}')
	
        progress = await ctx.send(embed=emb), await member.send(embed=emb)
        try:
            for channel in ctx.guild.text_channels:
                await channel.set_permissions(member,   overwrite=discord.PermissionOverwrite(send_messages = False),     reason=reason)

            for channel in ctx.guild.voice_channels:
                await channel.set_permissions(member,   overwrite=discord.PermissionOverwrite(speak=False), reason=reason)
        except:
            success = False
        else:
            success = True

        await ctx.send(f'{member} замучен на {duration}')
        await asyncio.sleep(time)
        try:
            for channel in ctx.guild.channels:
                 await channel.set_permissions(member, overwrite=None, reason=reason)
        except:
            pass

@client.command(aliases=['k', 'к', 'кик'])
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member = None, *, reason="хз какой"):
	if member == None:
		emb3 = discord.Embed(title='kick', color=discord.Colour.red())
		emb3.set_author(name=client.user.name, icon_url=client.user.avatar_url)
		emb3.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
		emb3.add_field(
		    name='наказание',
		    value=f'{ctx.author.mention} обязательно укажите пользователся!')
		await ctx.send(embed=emb3)
	else:
		server = ctx.guild.name
		emb = discord.Embed(title='kick', color=discord.Colour.green(), timestamp = ctx.message.created_at)
		emb.set_author(name=client.user.name, icon_url=client.user.avatar_url)
		emb.set_footer(text = f'{client.user.name} © 2021 | Все права защищены', icon_url = client.user.avatar_url)
		emb.add_field(name='**модератор**', value= f'{ctx.author.mention}')
		emb.add_field(name='**кикнут**', value= f'{member.mention}')
		emb.add_field(name='**причина**', value= f'{reason}')
		await ctx.send(embed=emb)
		await member.send(embed=emb)
		emb2 = discord.Embed(title='kick', color=discord.Colour.green(), timestamp = ctx.message.created_at)
		emb2.set_author(name=client.user.name, icon_url=client.user.avatar_url)
		emb2.set_footer(text = f'{client.user.name} © 2021 | Все права защищены', icon_url = client.user.avatar_url)
		emb2.add_field(name='**модератор**', value= f'{ctx.author.mention}')
		emb2.add_field(name='**кикнут**', value= f'{member.mention}')
		emb2.add_field(name='**причина**', value= f'{reason}')
		await member.kick(reason=reason)

@client.command()
@commands.has_permissions(kick_members=True)
async def ban(ctx, member:discord.Member, duration, *, reason=None):
    if member == None:
        await ctx.send(f"{ctx.author.mention} укажите ```пользователь```")
    else:
        unit = duration[-1]
        print(f'{unit}')
        if unit == 'с':
            time = int(duration[:-1])
            longunit = 'секунд'
        elif unit == 'м':
            time = int(duration[:-1]) * 60
            longunit = 'минут'
        elif unit == 'ч':
            time = int(duration[:-1]) * 60 * 60
            longunit = 'часов'
        else:
            await ctx.send('Неправильно! Пиши `c`, `м`, `ч`')
            return
        emb = discord.Embed(title='Mute', color=discord.Colour.green(), timestamp =     ctx.message.created_at)
        emb.set_footer(text = f'{client.user.name} © 2021 | Все права защищены',    icon_url = client.user.avatar_url)
        emb.add_field(name='**модератор**', value= f'{ctx.author.mention}')
        emb.add_field(name='**забанен**', value= f'{member}')
        emb.add_field(name='**причина**', value= f'{reason}')
        emb.add_field(name='**время**', value= f'{duration}')
	
        progress = await ctx.send(embed=emb), await member.send(embed=emb)
        try:
            for channel in ctx.guild.text_channels:
                await member.ban( reason = reason )

            for channel in ctx.guild.voice_channels:
                await channel.set_permissions(member,   overwrite=discord.PermissionOverwrite(speak=False), reason=reason)
        except:
            success = False
        else:
            success = True

        await ctx.send(f'{member} забанен на {duration}')
        await asyncio.sleep(time)
        banned_users = await ctx.guild.bans()
        for ban_entry in banned_users:
            user = ban_entry.user
            await ctx.guild.unban( user )

        #try:
        #    for channel in ctx.guild.channels:
        #         await channel.set_permissions(member, overwrite=None, #reason=reason)
        #except:
        #    pass




@client.command()
async def newyear(ctx):
	await ctx.channel.purge(limit=1)
	verify_role = ctx.guild.get_role(780476291895263293)
	await ctx.author.add_roles(verify_role)
	server = ctx.guild.name
	emb = discord.Embed(title='2021', color=discord.Colour.green(), timestamp = ctx.message.created_at)
	emb.set_author(name=client.user.name, icon_url=client.user.avatar_url)
	emb.add_field(
	    name='2021',
	    value=
	    f' {ctx.author.mention}, ты успешно получил роль на сервере {server} '
	)
	await ctx.author.send(embed=emb)


@client.command(aliases=['sert', 'dolb','dolboeb', 'diplom'])
async def sertificat(ctx, member: discord.Member):
	img = Image.open('./assets/ser.png')
	idraw = ImageDraw.Draw(img)
	name = member.name
	tag = member.discriminator
	msg = f'{name}'
    #W, H = (170,350 )
	headline = ImageFont.truetype('./assets/font.ttf', size=50)
	idraw.text((325, 380), f'{name}',anchor="ms", font=headline, fill='#6B613E')
    #w, h = draw.textsize(msg)
    #idraw.text(((W-w)/2, 350), msg, fill = '#6B613E')

	img.save('serf.png')
	await ctx.send(file=discord.File(fp='serf.png'))


@client.command(aliases=['svad', 'svadba', 'sex', 'svidetelstvo'])
async def brak(ctx, member: discord.Member):
	img = Image.open('./assets/svad.png')
	idraw = ImageDraw.Draw(img)
	name = member.name
	name2 = ctx.author.name
	tag = member.discriminator
	headline = ImageFont.truetype('./assets/font.ttf', size=20)
	idraw.text((105, 112), f'{name2}', font=headline, fill='#463C30')
	idraw.text((100, 170), f'{name}', font=headline, fill='#463C30')

	img.save('svad2.png')
	await ctx.send(file=discord.File(fp='svad2.png'))


@client.command(aliases=['userinfo', 'uinfo'])
async def user(ctx, member: discord.Member = None):
	if member == None:
		member = ctx.author
	if member.nick == None:
		nick = member.name
	else:
		nick = member.nick

	emb = discord.Embed(
	    title=f'**Информация о {member.name}**',
	    description=f'''
Никнейм на сервере: {nick}

**Аватар:** [[нажми]({member.avatar_url})]
**Тег:** {member.discriminator}
**Всего ролей:** {len(member.roles)}
**Гл.Роль:** {member.top_role.name}
    
**Дата создания аккаунта:** {str(member.created_at)[:16]}
**Дата входа на сервер:** {str(member.joined_at)[:16]}
''', color = member.top_role.color , timestamp = ctx.message.created_at)
	emb.set_thumbnail(url=member.avatar_url)

	await ctx.send(embed=emb)


@client.event
async def on_guild_join(guild):
	guilds = await client.fetch_guilds(limit = None).flatten()
	await client.change_presence( activity= discord.Activity(name=f'за {len(guilds)} серверами.', type= discord.ActivityType.watching))
	me = client.get_user(636588932603183136)
	emb = discord.Embed(
	    title=f'Уведомление',
	    description='Бот пришел на новый сервер.',
	    color=0x00de68)  # Цвет - зеленый
	channel = guild.system_channel
	link = await channel.create_invite()
	emb.add_field(name=guild.name, value=f'Ссылка: {link}')
	emb.set_author(name=me, icon_url=me.avatar_url)
	emb.set_footer(
	    text=f'{client.user.name} © 2021 | Все права защищены',
	    icon_url=client.user.avatar_url)
	await me.send(embed=emb)





def strfdelta(tdelta, fmt):
	d = {"days": tdelta.days}
	d["hours"], rem = divmod(tdelta.seconds, 3600)
	d["minutes"], d["seconds"] = divmod(rem, 60)
	return fmt.format(**d)


    

@client.command(pass_context=True)
async def invite(ctx, amount=1):
	await ctx.channel.purge(limit=1)
	author = ctx.message.author
	amount = amount
	emb = discord.Embed(
	    title='invite',
	    description='📲 пригласи меня на свой сервер нажав по кнопке invite',
	    colour=discord.Color.green(),
	    url=
	    'https://discord.com/oauth2/authorize?client_id=778958437631131690&scope=bot&permissions=8'
	)
	emb.set_author(name=client.user.name)
	emb.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
	emb.set_image(
	    url=
	    'https://media1.tenor.com/images/9501c8fc880fb1e14055798f23d47f73/tenor.gif?itemid=16563786'
	)
	await ctx.author.send(embed=emb)

@client.command(aliases=['сервер'])
async def server(ctx):
	allvoice = len(ctx.guild.voice_channels)
	alltext = len(ctx.guild.text_channels)
	members = ctx.guild.members
	allroles = len(ctx.guild.roles)
	bots = len([m for m in members if m.bot])

	emb = discord.Embed(title=f"{ctx.guild.name}", color = discord.Color.green())
	emb.add_field(name='**Владелец:**', value= ctx.guild.owner)
	emb.add_field(name='**Регион:**', value= ctx.guild.region)	
	emb.add_field(name='**Описание:**', value= ctx.guild.description)
	emb.add_field(name='**Nitro-буст:**', value= ctx.guild.premium_subscription_count)
	emb.add_field(name='**Участники:**', value= ctx.guild.member_count)
	emb.add_field(name='**Боты:**', value= f'{bots}')
	emb.add_field(name='**Создан:**', value= f'{ctx.guild.created_at}'[:-10])
	emb.add_field(name='**Голосовые:**', value= f'{allvoice}')
	emb.add_field(name='**Текстовые:**', value= f'{alltext}')
	emb.add_field(name='**Роли:**', value= f'{allroles}')

	emb.set_thumbnail(url=ctx.guild.icon_url)

	await ctx.send(embed =emb)




@client.command(aliases = ['anime','аниме'])
async def user_anime(ctx):
    anime = [
    'https://static2.aniimg.com/upload/20170606/712/F/5/O/F5OGEF.jpg',
    'https://get.wallhere.com/photo/illustration-anime-anime-girls-short-hair-cartoon-black-hair-sweater-mouth-mangaka-41663.jpg',
    'https://static.zerochan.net/Kuroyukihime.full.1028240.jpg',
    'https://static.zerochan.net/IA.full.1212336.jpg',
    'https://wallpapercave.com/wp/wp2579738.jpg',
    'https://images.wallpaperscraft.ru/image/anime_devushka_lico_glaza_23057_1920x1200.jpg',
    'https://get.wallhere.com/photo/illustration-blonde-long-hair-anime-anime-girls-looking-at-viewer-cartoon-school-uniform-mangaka-49934.jpg',
    'http://pm1.narvii.com/6933/109db960f03a808a2d04d4f78f290fa19a9fb56dr1-1920-1200v2_uhq.jpg',
    'https://i.ucrazy.ru/files/i/2011.8.11/1313061791_anime_anime_sport_girl_018649_.jpg',
    'http://pm1.narvii.com/7065/3c4b5db0614269a1a6ae858ebfe0706ee7602bfbr1-1440-900v2_uhq.jpg',
    'https://proprikol.ru/wp-content/uploads/2019/11/kartinki-anime-s-ushkami-10.jpg',
    'https://get.wallhere.com/photo/illustration-long-hair-anime-anime-girls-clouds-blue-school-uniform-visual-novel-schoolgirl-If-My-Heart-Had-Wings-Habane-Kotori-computer-wallpaper-mangaka-143320.jpg',
    'https://wallpapercave.com/wp/wp3238040.jpg',
    'http://pm1.narvii.com/6881/7ad4347d226019de248098c5a2d65ace8cc4c494r1-1920-1080v2_uhq.jpg',
    'https://million-wallpapers.ru/wallpapers/3/69/390987900899292/denpa-onna-chtoby-seishun-otoko.jpg',
    'https://wallup.net/wp-content/uploads/2018/09/26/215906-anime-Vocaloid-Hatsune_Miku.jpg',
    'https://i.artfile.ru/1920x1080_1464584_[www.ArtFile.ru].jpg',
    'https://static.zerochan.net/Gurenka.full.1179328.jpg',
    'http://pm1.narvii.com/7117/429293446f7b6681ee4d5a2a9474969fed7282dar1-2048-1152v2_uhq.jpg',
    'https://i.ucrazy.ru/files/i/2011.8.11/1313061866_anime_bride_013359_.jpg',
    'https://img1.goodfon.ru/original/1920x1403/6/96/art-awakawayui-hatsune-miku.jpg',
    'http://pm1.narvii.com/7132/d06bb8b9ff95e99d0f12c35b8eaebc3aae6f6e1ar1-1920-1440v2_uhq.jpg',
    'https://get.wallhere.com/photo/shoufukucho-anime-girl-look-wind-1001035.jpg',
    'https://get.wallhere.com/photo/illustration-blonde-night-anime-Moon-blue-girl-sweet-screenshot-computer-wallpaper-fictional-character-725975.jpg',
    'https://i.ucrazy.ru/files/i/2011.8.11/1313061783_anime_anime_013328_.jpg'
    ]
    images = random.choice(anime)
    emb = discord.Embed(title = f'**anime**', colour = discord.Color.green())
    emb.set_image(url = f'{images}')
    emb.set_footer(text = f'{client.user.name} © 2021 | Все права защищены', icon_url = client.user.avatar_url)

    await ctx.send(embed = emb)

@client.command()
async def hands(ctx, member: discord.Member = None):
    if member == ctx.author:
        return await ctx.send(embed = discord.Embed(description = 'Ты не можешь взять за руку самого себя!'))
 
    if member == None:
        return await ctx.send(embed = discord.Embed(description = 'Обязательно укажи пользователя!'))
 
    hands = ['https://cdn.discordapp.com/attachments/746337035660427315/746343049323610272/8f70714a8fc965fdcae4d7d11bc4c683.gif','https://cdn.discordapp.com/attachments/746337035660427315/746343071402295346/6a99cf456a620157081d791a5f221b709facb9f5_hq.gif','https://cdn.discordapp.com/attachments/746337035660427315/746343086527086743/4d595b493c634263506f6e3babdd0bbe.gif','https://cdn.discordapp.com/attachments/746337035660427315/746343109385781298/64722f8fe88db6c1178fbae5ff6cd06e.gif','https://cdn.discordapp.com/attachments/746337035660427315/746343217842356275/A9kxW4y.gif']
 
    embed1 = discord.Embed(description = f'{ctx.author.mention} взял за ручку {member.mention}')
    embed1.set_image(url=random.choice(hands))
    await ctx.send(embed = embed1)

@client.command()
async def ping(ctx):
    ping = client.latency
    ping_emoji = "🟩🔳🔳🔳🔳"
    
    ping_list = [
        {"ping": 0.10000000000000000, "emoji": "🟧🟩🔳🔳🔳"},
        {"ping": 0.15000000000000000, "emoji": "🟥🟧🟩🔳🔳"},
        {"ping": 0.20000000000000000, "emoji": "🟥🟥🟧🟩🔳"},
        {"ping": 0.25000000000000000, "emoji": "🟥🟥🟥🟧🟩"},
        {"ping": 0.30000000000000000, "emoji": "🟥🟥🟥🟥🟧"},
        {"ping": 0.35000000000000000, "emoji": "🟥🟥🟥🟥🟥"}]
    
    for ping_one in ping_list:
        if ping > ping_one["ping"]:
            ping_emoji = ping_one["emoji"]
            break

    message = await ctx.send("Пожалуйста, подождите. . .")
    await message.edit(content = f"Понг! {ping_emoji} `{ping * 1000:.0f}ms` :ping_pong:")
	
Kiss1 = ('https://i.gifer.com/2VNx.gif')
Kiss2 = ('https://i.gifer.com/2uEt.gif')
Kiss3 = ('https://i.gifer.com/2lte.gif')
Kiss4 = ('https://i.gifer.com/8Sbz.gif')
Kiss5 = ('https://i.gifer.com/PCUi.gif')
Kiss6 = ('https://i.gifer.com/i0I.gif')
Kiss7 = ('https://i.gifer.com/3a1n.gif')
Kiss8 = ('https://i.gifer.com/C3GK.gif')
Kiss9 = ('https://i.gifer.com/8Uc1.gif')
Kiss10 = ('https://i.gifer.com/3kMa.gif')
Kiss11 = ('https://i.gifer.com/2OsR.gif')
Kiss12 = ('https://cdn.discordapp.com/attachments/700754286291714080/738430039749689344/anime-kiss-m.gif')
Kiss13 = ('https://i.gifer.com/XJis.gif')
Kiss14 = ('https://cdn.weeb.sh/images/Skc42pdv-.gif')
Kiss15 = ('https://cdn.weeb.sh/images/rJoL2pdvb.gif')
Kiss16 = ('https://cdn.weeb.sh/images/HJlWhpdw-.gif')
Kiss17 = ('https://cdn.weeb.sh/images/SyY0j6Ov-.gif')
Kiss18 = ('https://cdn.weeb.sh/images/rypMnpuvW.gif')
Kiss19 = ('https://cdn.weeb.sh/images/SkQIn6Ovb.gif')
Kiss20 = ('https://cdn.weeb.sh/images/r1VWnTuPW.gif')
Kiss21 = ('https://cdn.weeb.sh/images/ry-r3TuD-.gif')
Kiss22 = ('https://cdn.weeb.sh/images/BJv0o6uDZ.gif')
Kiss23 = ('https://cdn.weeb.sh/images/Bkuk26uvb.gif')
Kiss24 = ('https://cdn.weeb.sh/images/Sksk4l51z.gif')
Kiss25 = ('')
Kiss26 = ('https://cdn.weeb.sh/images/SJrBZrMBz.gif')
Kiss27 = ('https://cdn.weeb.sh/images/Skv72TuPW.gif')
Kiss28 = ('https://cdn.weeb.sh/images/B1yv36_PZ.gif')
Kiss29 = ('https://cdn.weeb.sh/images/Sylj0s6dv-.jpeg')
Kiss30 = ('https://cdn.weeb.sh/images/Hkt-nTOwW.gif')
Kiss31 = ('https://cdn.weeb.sh/images/BkLQnT_PZ.gif')
Kiss32 = ('https://cdn.weeb.sh/images/B1NwJg9Jz.gif')
Kiss33 = ('https://cdn.weeb.sh/images/r10UnpOPZ.gif')
Kiss34 = ('https://cdn.weeb.sh/images/rJrCj6_w-.gif')
Kiss35 = ('https://cdn.weeb.sh/images/Hy-oQl91z.gif')
KissRANDOM = [Kiss1,Kiss2,Kiss3,Kiss4,Kiss5,Kiss6,Kiss7,Kiss8,Kiss9,Kiss10,Kiss11,Kiss12,Kiss13,Kiss14,Kiss15,Kiss16,Kiss17,Kiss18,Kiss19,Kiss20,Kiss21,Kiss22,Kiss23,Kiss24,Kiss26,Kiss27,Kiss28,Kiss29,Kiss30,Kiss31,Kiss32,Kiss33,Kiss34,Kiss35]

@client.command(aliases =['Kiss', 'kiss'])
async def __kiss(ctx, member : discord.Member = None):
    await ctx.message.delete()
    author = (ctx.author.id)
    Kiss = random.choice(KissRANDOM)
    print(f'Команду Kiss использовал пользователь {ctx.author.name}')
    embed = discord.Embed(title = f'{ctx.author} поцеловал {member}', timestamp = ctx.message.created_at)
    embed.set_image( url = Kiss)
    await ctx.send(embed=embed)

@client.command()
async def shot( ctx, member: discord.Member ):
    await ctx.channel.purge( limit = 1 )

    embed = discord.Embed(title = 'Выстрел', description = 'Вы сможете в кого-то выстрелить.', colour = discord.Color.red(), timestamp = ctx.message.created_at)

    embed.add_field( name = '**Доставание дробовика**', value = f"{ctx.author.mention} достаёт дробовик...", inline = False )

    await asyncio.sleep( 3 )
    embed.add_field( name = '**Направление дробовика**', value = f"{ctx.author.mention} направляет дробовик на {member.mention}...", inline = False )

    await asyncio.sleep( 2 )
    embed.add_field( name = '**Стрельба**', value = f"{ctx.author.mention} стреляет в {member.mention}...", inline = False )

    embed.set_image(url='https://media.discordapp.net/attachments/690222948283580435/701494203607416943/tenor_3.gif')

    await asyncio.sleep( 2 )
    embed.add_field( name = '**Кровь**', value = f"{member.mention} истекает кровью...", inline = False )

    await ctx.send( embed = embed )

@client.command()
async def avatar(ctx, member: discord.Member = None):
    if member == None:
        member = ctx.author

    await ctx.message.delete()

    user = ctx.message.author if not member else member

    embed = discord.Embed(title = f'Аватар пользователя {member}', color = 0xFF000, timestamp = ctx.message.created_at)

    embed.set_image(url = user.avatar_url_as(format = None, size = 4096))
    embed.set_author(icon_url = 'https://www.flaticon.com/premium-icon/icons/svg/2919/2919600.svg', name = 'Участник | Аватар')
    embed.set_footer(text = f'{client.user.name} © 2021 | Все права защищены', icon_url = client.user.avatar_url)

    await ctx.send(embed = embed)

@client.command()
async def wiki(ctx, *, query: str):

    msg = await ctx.send("Пожалуйста, подождите. . .")
    sea = requests.get(
        ('https://ru.wikipedia.org//w/api.php?action=query'
         '&format=json&list=search&utf8=1&srsearch={}&srlimit=5&srprop='
        ).format(query)).json()['query']

    if sea['searchinfo']['totalhits'] == 0:
        await ctx.send(f'По запросу **"{query}"** ничего не найдено :confused:')
    else:
        for x in range(len(sea['search'])):
            article = sea['search'][x]['title']
            req = requests.get('https://ru.wikipedia.org//w/api.php?action=query'
                               '&utf8=1&redirects&format=json&prop=info|images'
                               '&inprop=url&titles={}'.format(article)).json()['query']['pages']
            if str(list(req)[0]) != "-1":
                break
        article = req[list(req)[0]]['title']
        arturl = req[list(req)[0]]['fullurl']
        artdesc = requests.get('https://ru.wikipedia.org/api/rest_v1/page/summary/' + article).json()['extract']
        embed = discord.Embed(title = article, url = arturl, description = artdesc, color = 0x00ffff, timestamp = ctx.message.created_at)
        embed.set_author(name = 'Google | Википедия', url = 'https://en.wikipedia.org/', icon_url = 'https://upload.wikimedia.org/wikipedia/commons/6/63/Wikipedia-logo.png')
        embed.set_footer(text = f'{client.user.name} © 2021 | Все права защищены', icon_url = client.user.avatar_url)

        await ctx.send(embed = embed)

Hit1 = ('https://i.gifer.com/DjuN.gif')
Hit2 = ('https://i.gifer.com/4msN.gif')
Hit3 = ('https://i.gifer.com/9SOw.gif')
Hit4 = ('https://i.gifer.com/9Ky6.gif')
Hit5 = ('https://i.gifer.com/79cT.gif')
Hit6 = ('https://i.gifer.com/9Ky8.gif')
Hit7 = ('https://i.gifer.com/9KyA.gif')

HitRANDOM = [Hit1,Hit2,Hit3,Hit4,Hit5,Hit6,Hit7]

@client.command(aliases =['hit', 'Hit'])
async def __hit(ctx, member : discord.Member = None):
    await ctx.message.delete()
    author = (ctx.author.id)
    Kiss = random.choice(HitRANDOM)
    print(f'Команду Kiss использовал пользователь {ctx.author.name}')
    embed = discord.Embed(title = f'{ctx.author} ударил {member}', timestamp = ctx.message.created_at)
    embed.set_image( url = Kiss)
    embed.set_footer(text = f'{client.user.name} © 2021 | Все права защищены', icon_url = client.user.avatar_url)
    await ctx.send(embed=embed)

	
@client.command()
async def trash(ctx,member:discord.Member = None):
    if member == None:
        member = ctx.author
    url = str(member.avatar_url)[:-10]
    url = requests.get(url,stream = True)
    avatar = Image.open(io.BytesIO(url.content))
    trash = Image.open('./assets/trash.png')
    trash = trash.convert('RGBA')
    avatar = avatar.convert('RGBA')
    avatar = avatar.resize((500,500))
    mask = Image.new('L',(1500,1500),0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0,0) + (1500,1500),fill = 255)
    mask = mask.resize((500,500))
    avatar.putalpha(mask)
    trash = trash.resize((1000,1000))
    trash.paste(avatar,(155,280,655,780),avatar)
    _buffer = io.BytesIO()
    trash.save(_buffer,"png")
    _buffer.seek(0)
    await ctx.send(file = discord.File(fp = _buffer,filename = f'{member.name}trash.png'))
	
@client.command()
async def rv(ctx, *, text: str):

    t_rev = text[::-1].replace("@", "@\u200B").replace("&", "&\u200B")
    await ctx.send(f"{t_rev}")
	
@client.command()
async def hug(ctx, user: discord.Member): # b'\xfc'
    await ctx.message.delete()
    r = requests.get("https://nekos.life/api/v2/img/hug")
    res = r.json()
    em = discord.Embed(description=user.mention)
    em.set_image(url=res['url'])
    em.set_footer(text = f'{client.user.name} © 2021 | Все права защищены', icon_url = client.user.avatar_url)
    await ctx.send(embed=em)
	
@client.command(aliases=['автор'])
async def author(ctx):
	emb = discord.Embed( color=discord.Colour.blue(), timestamp = ctx.message.created_at)
	emb.set_author(name=client.user.name, icon_url=client.user.avatar_url)
	emb.set_footer(text = f'{client.user.name} © 2021 | Все права защищены', icon_url = client.user.avatar_url)
	emb.add_field( name = '**автор**', value = f"Primot" )
	emb.add_field( name = '**Discord**', value = f"Даник#7128" )

	await ctx.send(embed=emb)
	
@client.command()
async def say(ctx, channel : discord.TextChannel, *, message):
    channel = channel
    await channel.send(message)
	
@client.command()
async def welcome(ctx,member:discord.Member = None):
    if member == None:
        member = ctx.author
    url = str(member.avatar_url)[:-10]
    url = requests.get(url,stream = True)
    avatar = Image.open(io.BytesIO(url.content))
    welcome = Image.open('./assets/hi.png')
    welcome = welcome.convert('RGBA')
    avatar = avatar.convert('RGBA')
    avatar = avatar.resize((500,500))
    mask = Image.new('L',(1500,1500),0)
    draw = ImageDraw.Draw(mask)
    idraw = ImageDraw.Draw(welcome)
    name = member.name
    tag = member.discriminator
    at = member.created_at
    headline = ImageFont.truetype('./assets/font.ttf', size=70)
    headline2 = ImageFont.truetype('./assets/font.ttf', size=70)
    idraw.text((900, 750), f'{name}#{tag}',anchor="ms", font=headline, fill='#FFFFFF')
    idraw.text((900, 950), f'Создан {at}' [:-15],anchor="ms", font=headline2, fill='#FFFFFF')
    draw.ellipse((0,0) + (1500,1500),fill = 255)
    mask = mask.resize((500,500))
    avatar.putalpha(mask)
    welcome = welcome.resize((1800,1100))
    welcome.paste(avatar,(650,50),avatar)
    _buffer = io.BytesIO()
    welcome.save(_buffer,"png")
    _buffer.seek(0)
    await ctx.send(file = discord.File(fp = _buffer,filename = f'{member.name}welcome.png'))
	       
@client.command(aliases = ['spot'])
async def spotify(ctx,member:discord.Member = None):
    if member == None:
        member = ctx.author
    spot = next((activity for activity in member.activities if isinstance(activity, discord.Spotify)), None)
    if not spot:
        return await ctx.send(f"{member.mention}, не слушает Spotify :mute:")
    avatar = Image.open(requests.get(url = spot.album_cover_url, stream=True).raw).convert('RGBA')
    spotify = Image.open('./assets/Spotify.PNG')
    spotify = spotify.convert('RGBA')
    avatar = avatar.convert('RGBA')
    avatar = avatar.resize((450,450))
    mask = Image.new('L',(1500,1500),0)
    draw = ImageDraw.Draw(mask)
    idraw = ImageDraw.Draw(spotify)
    name = member.name
    tag = member.discriminator
    at = member.created_at
    headline = ImageFont.truetype("./assets/font.ttf", size=90)
    headline2 = ImageFont.truetype('./assets/font.ttf', size=60)
    idraw.text((570, 50), f'Песня', font=headline2, fill='#FFFFFF')
    idraw.text((570, 110), f'{spot.title}', font=headline, fill='#FFFFFF')
    idraw.text((570, 210), f'Альбом', font=headline2, fill='#FFFFFF')
    idraw.text((570, 270), f'{spot.album}', font=headline, fill='#FFFFFF')
    idraw.text((570, 370), f'Автор:', font=headline2, fill='#A7A7A7')
    idraw.text((770, 370), f'{spot.artist}', font=headline2, fill='#FFFFFF')
    idraw.text((570, 470), f"{spot.created_at}" [:-15], font=headline2, fill='#FFFFFF')
    draw.ellipse((0,0) + (1500,1500),fill = 255)
    mask = mask.resize((500,500))
    #avatar.putalpha(mask)
    spotify = spotify.resize((1920,640))
    spotify.paste(avatar,(50,50),avatar)
    _buffer = io.BytesIO()
    spotify.save(_buffer,"png")
    _buffer.seek(0)
    await ctx.send(file = discord.File(fp = _buffer,filename = f'{member.name}spotify.png'))	



@client.command()
async def help(ctx, arg = None):
    if arg == None:
        emb = discord.Embed( title = f':arrow_backward:Команды:arrow_forward:', colour = discord.Color.green(), timestamp = ctx.message.created_at, url='http://spacebotapp.ru/')
        emb.add_field(name = f":ledger:!help info",value=f"Информация")
        emb.add_field(name = f":u7121:!help anime",value=f"Аниме")
        emb.add_field(name = f":headphones:!help music",value=f"Музыка")
        emb.add_field(name = f":hammer_pick:!help moder",value=f"Модерация")
        emb.add_field(name = f":partying_face:!help fun",value=f"Веселье")
        emb.add_field(name = f":shopping_cart:!help shop",value=f"Магазин[Beta]")
        emb.set_footer(text = f'{client.user.name} © 2021 | Все права защищены', icon_url = client.user.avatar_url)
        await ctx.send( embed = emb )
    else:
        if arg == 'info':
            emb = discord.Embed( title = f':ledger:Информация:ledger:', colour = discord.Color.green(), timestamp = ctx.message.created_at, url='http://spacebotapp.ru/')
            emb.add_field(name = ":bust_in_silhouette:```!user {пользователь, *}```",value=f"узнать информацию о пользователе")
            emb.add_field(name = ":window:```!avatar {пользователь, *}```",value=f"получить аватар пользователя")
            emb.add_field(name = ":satellite:```!invite```",value=f"пригласить бота на сервер")
            emb.add_field(name = ":desktop:```!server```",value=f"узнать информацию про сервер")
            emb.add_field(name = ":speech_left:```!ping```",value=f"узнать пинг бота")
            emb.add_field(name = ":detective:```!author```",value=f"узнать об авторе бота")
            emb.add_field(name = ":scroll:```!wiki [текст]```",value=f"узнать информацию о слове через википедию")
            emb.set_footer(text = f'{client.user.name} © 2021 | Все права защищены', icon_url = client.user.avatar_url)
            await ctx.send( embed = emb )
        else:
            if arg == 'anime':
                emb = discord.Embed( title = f':u7121:Аниме:u7121:', colour = discord.Color.green(), timestamp = ctx.message.created_at, url='http://spacebotapp.ru/')
                emb.add_field(name = ":hot_face:!anime",value=f"получить рандом картинку из аниме")
                emb.set_footer(text = f'{client.user.name} © 2021 | Все права защищены', icon_url = client.user.avatar_url)
                await ctx.send( embed = emb )
            else:
                if arg == 'music':
                    emb = discord.Embed( title = f':headphones:Музыка:headphones:', colour = discord.Color.green(), timestamp = ctx.message.created_at, url='http://spacebotapp.ru/')
                    emb.add_field(name = ":green_circle:```!spotify {пользователь, *}```",value=f"узнать, что слушает пользователь через Spotify")
                    emb.set_footer(text = f'{client.user.name} © 2021 | Все права защищены', icon_url = client.user.avatar_url)
                    await ctx.send( embed = emb )
                else:
                    if arg == 'moder':
                        emb = discord.Embed( title = f':hammer_pick:Модерация:hammer_pick:', colour = discord.Color.green(), timestamp = ctx.message.created_at, url='http://spacebotapp.ru/')
                        emb.add_field(name = ":broom:```!clear [число]```",value=f"очистить чат")
                        emb.add_field(name = ":wrench:```!kick {пользователь} [причина]```",value=f"кикнуть пользователя")
                        emb.add_field(name = ":zipper_mouth:```!mute {пользователь} [время] [причина]```",value=f"замьютить пользователя")
                        emb.add_field(name = ":hammer:```!ban {пользователь} [время] [причина]```",value=f"забанить пользователя")
                        emb.set_footer(text = f'{client.user.name} © 2021 | Все права защищены', icon_url = client.user.avatar_url)
                        await ctx.send( embed = emb )
                    else:
                        if arg == 'fun':
                            emb = discord.Embed( title = f':partying_face:Веселье:partying_face:', colour = discord.Color.green(), timestamp = ctx.message.created_at, url='http://spacebotapp.ru/')
                            emb.add_field(name = ":page_facing_up:```!sert {пользователь}```",value=f"подарить сертификат пользователю")
                            emb.add_field(name = ":couple_with_heart_woman_man:```!brak {пользователь}```",value=f"жениться на пользователе")
                            emb.add_field(name = ":couple:```!hands {пользователь}```",value=f"взяться за руку пользователю")
                            emb.add_field(name = ":kissing_smiling_eyes:```!kiss {пользователь}```",value=f"поцеловать пользователя")
                            emb.add_field(name = ":gun:```!shot {пользователь}```",value=f"выстрелить в пользователя")
                            emb.add_field(name = ":punch:```!hit {пользователь}```",value=f"ударить пользователя")
                            emb.add_field(name = ":people_hugging:```!hug {пользователь}```",value=f"обнять пользователя")
                            emb.add_field(name = ":wastebasket:```!trash {пользователь, *}```",value=f"выкинуть пользователя")
                            emb.add_field(name = ":recycle:```!rv [текст]```",value=f"перевернуть текст")
                            emb.add_field(name = ":robot:```!say {канал} [текст]```",value=f"отправить текст от лица бота")
                            emb.set_footer(text = f'{client.user.name} © 2021 | Все права защищены', icon_url = client.user.avatar_url)
                            await ctx.send( embed = emb )
                        else:
                            if arg == 'shop':
                                emb = discord.Embed( title = f':partying_face:Магазин[Beta]:partying_face:', colour = discord.Color.green(), timestamp = ctx.message.created_at, url='http://spacebotapp.ru/')
                                emb.add_field(name = f":dollar:```!balance```",value=f"Узнать свой баланс")
                                emb.add_field(name = f":bank:```!dep [число]```",value=f"перевести деньги в банк")
                                emb.add_field(name = f":credit_card:```!with [число]```",value=f"перевести деньги на баланс")
                                emb.add_field(name = f":construction_worker:```!work```",value=f"заработать деньги от 10$ до 100$, раз в 60 мин")
                                emb.add_field(name = f":money_mouth:```!casino [число]```",value=f"поиграть в казино, раз в 10 мин")
                                emb.add_field(name = ":shopping_bags:```!shop```",value=f"посмотреть что в магазине")
                                emb.add_field(name = ":heavy_plus_sign:```!addrole {роль} [число]```",value=f"добавить роль в магазин")
                                emb.add_field(name = ":heavy_minus_sign:```!delrole {роль}```",value=f"убрать роль из магазина")
                                emb.add_field(name = ":coin:```!buy {роль}```",value=f"купить роль из магазина")
                                emb.add_field(name = ":coin:```!sell {продать}```",value=f"купить роль из магазина")
                                emb.set_footer(text = f'{client.user.name} © 2021 | Все права защищены', icon_url = client.user.avatar_url)
                                await ctx.send( embed = emb )

@client.command()
async def dep(ctx, amount: int = None):
    if amount > cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]:
        await ctx.send(f"**{ctx.author.mention}**, у вас недостаточно средств!")
    else:
        cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(amount, ctx.author.id))
        cursor.execute("UPDATE users SET bank = bank + {} WHERE id = {}".format(amount, ctx.author.id))
        connection.commit()
        emb = discord.Embed( title = 'Dep', colour = discord.Color.green(), timestamp = ctx.message.created_at )
        emb.add_field(name='**Пользователь:**', value= f'{ctx.author.mention}')
        emb.add_field(name='**Перевёл в банк:**', value= f'{amount}$')
        emb.set_footer(text = f'{client.user.name} © 2021 | Все права защищены', icon_url = client.user.avatar_url)
        emb.set_thumbnail(url=ctx.author.avatar_url)

        await ctx.send( embed = emb )

@client.command(aliases = ['with'])
async def __with(ctx, amount: int = None):

    if amount > cursor.execute("SELECT bank FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]:
        await ctx.send(f"**{ctx.author.mention}**, у вас недостаточно средств!")
    else:
        cursor.execute("UPDATE users SET bank = bank - {} WHERE id = {}".format(amount, ctx.author.id))
        cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(amount, ctx.author.id))
        connection.commit()
        emb = discord.Embed( title = f'With'[:-5], colour = discord.Color.green(), timestamp = ctx.message.created_at )
        emb.add_field(name='**Пользователь:**', value= f'{ctx.author.mention}')
        emb.add_field(name='**Перевёл на баланс:**', value= f'{amount}:money_with_wings:')
        emb.set_footer(text = f'{client.user.name} © 2021 | Все права защищены', icon_url = client.user.avatar_url)
        emb.set_thumbnail(url=ctx.author.avatar_url)
        

        await ctx.send( embed = emb )

@client.command(aliases = ['bal', 'cash', 'money'])
async def balance(ctx,member:discord.Member = None):
    if member == None:
        member = ctx.author
    if cursor.execute(f"SELECT id FROM users WHERE id = {member.id} AND serverid = {member.guild.id}").fetchone() is None:
       cursor.execute(f"INSERT INTO users VALUES ({member.guild.id}, '{member}', {member.id}, {0}, {0}, {0})")
       connection.commit() 
    else:
        pass
    emb = discord.Embed(title='balance', color=discord.Colour.green(), timestamp = ctx.message.created_at)
    emb.set_author(name=client.user.name, icon_url=client.user.avatar_url)
    emb.set_footer(text = f'{client.user.name} © 2021 | Все права защищены', icon_url = client.user.avatar_url)
    emb.add_field(name='**Пользователь**', value= f'{member.mention}')
    emb.add_field(name='**Баланс**', value= f'{cursor.execute("SELECT cash FROM users WHERE id = {} AND serverid = {}".format(member.id, ctx.guild.id)).fetchone()[0]}')
    await ctx.send(embed=emb)

@client.command(aliases = ['work'])
@commands.cooldown(1, 3600, commands.BucketType.user) # 3600 это через скок сек ползоыватель сможет выполнить команду снова
async def timely(ctx):
    value = random.randint(10, 100) #рандом число например: от 10 до 100
    cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {} and serverid = {}".format(value, ctx.author.id, ctx.author.guild.id))
    connection.commit()
    emb = discord.Embed( title = 'Work', colour = discord.Color.green(), timestamp = ctx.message.created_at )
    emb.set_footer(text = f'{client.user.name} © 2021 | Все права защищены', icon_url = client.user.avatar_url)
    emb.add_field(name='**Пользователь:**', value= f'{ctx.author.mention}')
    emb.add_field(name='**Сумма:**', value= f'{value}$')
    emb.set_thumbnail(url=ctx.author.avatar_url)
    await ctx.send( embed = emb )
    await asyncio.sleep(12*60)
    

@timely.error
async def work_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        lol = error.retry_after / 60
        msg = '```Попробуй снова через {:.0f} минут```'.format(lol)

        await ctx.send(msg)
    else:
        raise error

@client.command()
@commands.cooldown(1, 600, commands.BucketType.user)
async def casino(ctx, amount: int = None):
    if amount == None:
        await ctx.send(f"{ctx.author.mention} укажите ```сумма```")
    else:
        if amount > cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]:
            await ctx.send( f"{ctx.author.mention} у вас недостаточно средств!" )
        else:
            value1 = random.randint(1, 2)
            if value1 == 1:
                cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(amount, ctx.author.id))
                emb = discord.Embed( title = f'Казино', colour = discord.Color.red(), timestamp = ctx.message.created_at )
                emb.set_footer(text = f'{client.user.name} © 2021 | Все права защищены', icon_url = client.user.avatar_url)
                emb.add_field(name='**Проиграл:**', value= f'{amount}:money_with_wings:')
                emb.add_field(name='**Твой баланс:**', value= f"{cursor.execute('SELECT cash FROM users WHERE id = {}'.format(ctx.author.id)).fetchone()[0]}:money_with_wings:")
                emb.set_thumbnail(url=ctx.author.avatar_url)
                await ctx.send( embed = emb )
            else:
                if value1 == 2:
                    value2 = random.randint(1, 3)
                    if value2 == 1:
                        cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(amount, ctx.author.id))
                        emb = discord.Embed( title = f'Казино', colour = discord.Color.green(), timestamp = ctx.message.created_at )
                        emb.set_footer(text = f'{client.user.name} © 2021 | Все права защищены', icon_url = client.user.avatar_url)
                        emb.add_field(name='**Выйграл:**', value= f'{amount}:money_with_wings:')
                        emb.add_field(name='**Твой баланс:**', value= f"{cursor.execute('SELECT cash FROM users WHERE id = {}'.format(ctx.author.id)).fetchone()[0]}:money_with_wings:")
                        emb.set_thumbnail(url=ctx.author.avatar_url)
                        await ctx.send( embed = emb )
                    else:
                        if value2 == 2:
                            cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(amount*2, ctx.author.id))
                            emb = discord.Embed( title = f'Казино', colour = discord.Color.green(), timestamp = ctx.message.created_at )
                            emb.set_footer(text = f'{client.user.name} © 2021 | Все права защищены', icon_url = client.user.avatar_url)
                            emb.add_field(name='**Выйграл:**', value= f'{amount*2} X2:money_with_wings:')
                            emb.add_field(name='**Твой баланс:**', value= f"{cursor.execute('SELECT cash FROM users WHERE id = {}'.format(ctx.author.id)).fetchone()[0]}:money_with_wings:")
                            emb.set_thumbnail(url=ctx.author.avatar_url)
                            await ctx.send( embed = emb )
                        else:
                            if value2 == 3:
                                cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(amount, ctx.author.id))
                                emb = discord.Embed( title = f'Казино', colour = discord.Color.green(), timestamp = ctx.message.created_at )
                                emb.set_footer(text = f'{client.user.name} © 2021 | Все права защищены', icon_url = client.user.avatar_url)
                                emb.add_field(name='**Выйграл:**', value= f'{amount}:money_with_wings:')
                                emb.add_field(name='**Твой баланс:**', value= f"{cursor.execute('SELECT cash FROM users WHERE id = {}'.format(ctx.author.id)).fetchone()[0]}:money_with_wings:")
                                emb.set_thumbnail(url=ctx.author.avatar_url)
                                await ctx.send( embed = emb )

@casino.error
async def casino_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        lol = error.retry_after / 60
        msg = '```Попробуй снова через {:.0f} минут```'.format(lol)

        await ctx.send(msg)
    else:
        raise error

@client.command(aliases = ['add-role'])
@commands.has_permissions(administrator = True)
async def addrole(ctx, role: discord.Role = None, cost: int = None):
    if role is None:
        await ctx.send(f"**{ctx.author.mention}**, укажите ```роль```")
    else:
        if cost is None:
            await ctx.send(f"**{ctx.author.mention}**, укажите ```стоимость```")
        elif cost < 1:
            await ctx.send(f"**{ctx.author.mention}** укажите ```стоимость > 0```")
        else:
            cursor.execute("INSERT INTO shop VALUES ({}, {}, {})".format(role.id, ctx.guild.id, cost))
            connection.commit()
            emb = discord.Embed( title = f'Addrole', colour = discord.Color.green(), timestamp = ctx.message.created_at )
            emb.add_field(name='**Добавил:**', value= f'{ctx.author.mention}')
            emb.add_field(name='**Роль:**', value= f'{role}')
            emb.add_field(name='**Цена:**', value= f"{cost}$")
            emb.set_thumbnail(url=ctx.author.avatar_url)
            emb.set_footer(text = f'{client.user.name} © 2021 | Все права защищены', icon_url = client.user.avatar_url)
            await ctx.send( embed = emb )

@client.command(aliases = ['shop'])
async def sh(ctx):
    embed = discord.Embed(title = ':green_square:МАГАЗИН РОЛЕЙ:green_square: ', colour = discord.Colour.green(), timestamp = ctx.message.created_at )

    for row in cursor.execute("SELECT role_id, cost FROM shop WHERE id = {}".format(ctx.guild.id)):
        if ctx.guild.get_role(row[0]) != None:
            embed.add_field(
                name = f"Цена: {row[1]}$",
                value = f"Роль: {ctx.guild.get_role(row[0]).mention}",
                inline = False
                )
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.set_footer(text = f'{client.user.name} © 2021 | Все права защищены', icon_url = client.user.avatar_url)
        else:
            pass

    await ctx.send(embed = embed)

@client.command(aliases = ['delrole', 'delete-role', 'del-role'])
@commands.has_permissions(administrator = True)
async def deleterole(ctx, role: discord.Role = None):
    if role is None:
        await ctx.send(f"**{ctx.author.mention}**, укажите ```роль```")
    else:
        cursor.execute("DELETE FROM shop WHERE role_id = {}".format(role.id))
        connection.commit()
        emb = discord.Embed( title = f'Delrole'[:-5], colour = discord.Color.red(), timestamp = ctx.message.created_at )
        emb.set_footer(text = f'{client.user.name} © 2021 | Все права защищены', icon_url = client.user.avatar_url)
        emb.add_field(name='**Убрал**', value= f'{ctx.author.mention}')
        emb.add_field(name='**Роль:**', value= f'{role}')
        emb.set_thumbnail(url=ctx.author.avatar_url)

        await ctx.send( embed = emb )

@client.command(aliases = ['buy-role'])
async def buy(ctx, role: discord.Role = None):
    if role is None:
        await ctx.send(f"**{ctx.author}**, укажите ```роль```")
    else:
        if role in ctx.author.roles:
            await ctx.send(f"**{ctx.author.mention}**, у вас уже есть такая роль!")
        elif cursor.execute("SELECT cost FROM shop WHERE role_id = {}".format(role.id)).fetchone()[0] > cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]:
            await ctx.send(f"**{ctx.author.mention}**, у вас недостаточно средств!")
        else:
            await ctx.author.add_roles(role)
            cursor.execute("UPDATE users SET cash = cash - {0} WHERE id = {1}".format(cursor.execute("SELECT cost FROM shop WHERE role_id = {}".format(role.id)).fetchone()[0], ctx.author.id))
            connection.commit()
            emb = discord.Embed( title = f'Buy', colour = discord.Color.green(), timestamp = ctx.message.created_at )
            emb.set_footer(text = f'{client.user.name} © 2021 | Все права защищены', icon_url = client.user.avatar_url)
            emb.add_field(name='**Купил**', value= f'{ctx.author.mention}')
            emb.add_field(name='**Роль:**', value= f'{role}')
            emb.set_thumbnail(url=ctx.author.avatar_url)
            await ctx.send( embed = emb )

@client.command(aliases = ['sell-role'])
async def sell(ctx, role: discord.Role = None):
    if role is None:
        await ctx.send(f'**{ctx.author}**, введите роль, которую хотите продать!')
    else:
        if role not in ctx.author.roles:
            await ctx.send(f'**{ctx.author}**, у вас нету данной роли, для того что бы её продавать!')
        else:
            cursor.execute("UPDATE users SET cash = cash + {0} WHERE id = {1}".format(cursor.execute("SELECT cost FROM shop WHERE role_id = {}".format(role.id)).fetchone()[0], ctx.author.id))
            connection.commit()
            await ctx.author.remove_roles(role)
            emb = discord.Embed( title = f'Sell', colour = discord.Color.green(), timestamp = ctx.message.created_at )
            emb.set_footer(text = f'{client.user.name} © 2021 | Все права защищены', icon_url = client.user.avatar_url)
            emb.add_field(name='**Продал:**', value= f'{ctx.author.mention}')
            emb.add_field(name='**Роль:**', value= f'{role}')
            emb.set_thumbnail(url=ctx.author.avatar_url)
            await ctx.send( embed = emb )

keep_alive.keep_alive()
client.run(token)

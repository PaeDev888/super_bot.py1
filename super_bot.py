import os
import discord
from discord.ext import commands
from discord import get

from myserver import server_on  

# --- ❗ การตั้งค่าที่จำเป็น ❗ ---

# 1. ตั้งค่า Intents (สิทธิ์ที่บอทต้องการ)
# ต้องแน่ใจว่าได้เปิด SERVER MEMBERS INTENT และ MESSAGE CONTENT INTENT ใน Discord Developer Portal
intents = discord.Intents.default()
intents.members = True          # สำหรับ join, leave, userinfo, moderation
intents.message_content = True  # สำหรับ commands
intents.reactions = True        # สำหรับ reaction roles
intents.guilds = True           # สำหรับ on_guild_join (เผื่ออนาคต)

# 2. สร้างอ็อบเจกต์บอท
bot = commands.Bot(command_prefix='/.', intents=discord.Intents.all()) 

# 3. ID ช่องสำหรับต้อนรับและลา (ปรับค่าเหล่านี้!)
WELCOME_CHANNEL_ID = 1431207767422533742
GOODBYE_CHANNEL_ID = 1431209788079079484

# 4. การตั้งค่า Reaction Roles (ปรับค่าเหล่านี้!)
# ❗ ต้องใช้ ID "ข้อความ" จริง
REACTION_MESSAGE_ID = 1431547767406334022
ROLE_MAP = {
    '👍': 1420646878441115790, # อิโมจิ : ID บทบาท
    # เพิ่มคู่ อิโมจิ : ID บทบาท ได้ตามต้องการ
    # '⭐': 1375791546930167809,
}


# --- จบส่วนการตั้งค่า ---


# 0. อีเวนต์พื้นฐาน
@bot.event
async def on_ready():
    """เมื่อบอทออนไลน์"""
    print(f'{bot.user.name} ออนไลน์และพร้อมใช้งาน!')
    print('------')
    await bot.change_presence(activity=discord.Game(name="!help | Bot อเนกประสงค์"))


# 1. หมวด: ข้อมูล/ยูทิลิตี้ (Info/Utility)

@bot.command(name='ping')
async def ping(ctx):
    """แสดงค่า Latency ของบอท"""
    latency = round(bot.latency * 1000)
    await ctx.send(f"Pong! 🏓 Latency: **{latency}ms**")

@bot.command(name='serverinfo')
async def serverinfo(ctx):
    """แสดงข้อมูลโดยรวมของเซิร์ฟเวอร์"""
    guild = ctx.guild
    embed = discord.Embed(
        title=f"ข้อมูลเซิร์ฟเวอร์: {guild.name}",
        description="รายละเอียดโดยรวมของเซิร์ฟเวอร์นี้",
        color=discord.Color.blue()
    )
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    embed.add_field(name="เจ้าของเซิร์ฟเวอร์", value=guild.owner.mention, inline=True)
    embed.add_field(name="สมาชิกทั้งหมด", value=guild.member_count, inline=True)
    embed.add_field(name="สร้างเมื่อ", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="ID เซิร์ฟเวอร์", value=guild.id, inline=False)
    
    await ctx.send(embed=embed)

# โค้ด userinfo เดิม
@bot.command(name='userinfo')
async def userinfo(ctx, member: discord.Member = None):
    """แสดงข้อมูลของสมาชิก (!userinfo @member)"""
    if member is None:
        member = ctx.author  
    
    embed = discord.Embed(
        title=f"ข้อมูลของ {member.name}",
        description=f"ข้อมูลสมาชิก",
        color=member.color if member.color != discord.Color.default() else discord.Color.greyple()
    )
    
    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)
    
    embed.add_field(name="ID ผู้ใช้", value=member.id, inline=False)
    embed.add_field(name="เข้าร่วม Discord เมื่อ", value=member.created_at.strftime("%d/%m/%Y %H:%M:%S"), inline=True)
    if member.joined_at:
        embed.add_field(name="เข้าร่วมเซิร์ฟเวอร์เมื่อ", value=member.joined_at.strftime("%d/%m/%Y %H:%M:%S"), inline=True)
    
    roles = [role.mention for role in member.roles[1:]]
    embed.add_field(name=f"บทบาท ({len(roles)})", value=" ".join(reversed(roles)) if roles else "ไม่มี", inline=False)
    
    await ctx.send(embed=embed)


# 2. หมวด: การจัดการ (Moderation)

@bot.command(name='kick')
@commands.has_permissions(kick_members=True) # ตรวจสอบสิทธิ์เตะ
async def kick(ctx, member: discord.Member, *, reason="ไม่มีเหตุผล"):
    """เตะสมาชิกออกจากเซิร์ฟเวอร์ (!kick @member [เหตุผล])"""
    try:
        await member.kick(reason=reason)
        await ctx.send(f"✅ เตะ **{member.display_name}** เรียบร้อยแล้ว. เหตุผล: **{reason}**")
    except discord.Forbidden:
        await ctx.send("❌ บอทไม่มีสิทธิ์เตะสมาชิกคนนี้ (อาจเป็นเพราะบทบาทบอทอยู่ต่ำกว่า)")
    except commands.errors.MissingPermissions:
        await ctx.send("❌ คุณไม่มีสิทธิ์ `kick_members` ในการใช้คำสั่งนี้")

@bot.command(name='ban')
@commands.has_permissions(ban_members=True) # ตรวจสอบสิทธิ์แบน
async def ban(ctx, member: discord.Member, *, reason="ไม่มีเหตุผล"):
    """แบนสมาชิกออกจากเซิร์ฟเวอร์ (!ban @member [เหตุผล])"""
    try:
        await member.ban(reason=reason)
        await ctx.send(f"🔨 แบน **{member.display_name}** เรียบร้อยแล้ว. เหตุผล: **{reason}**")
    except discord.Forbidden:
        await ctx.send("❌ บอทไม่มีสิทธิ์แบนสมาชิกคนนี้")
    except commands.errors.MissingPermissions:
        await ctx.send("❌ คุณไม่มีสิทธิ์ `ban_members` ในการใช้คำสั่งนี้")

# 3. หมวด: ปฏิสัมพันธ์ (Interaction) - Join/Leave
@bot.event
async def on_member_join(member):
    """เมื่อมีสมาชิกใหม่เข้ามา (ใช้ Intent: members)"""
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        embed = discord.Embed(title="สมาชิกใหม่!", description=f"ยินดีต้อนรับ {member.mention} เข้าสู่เซิร์ฟเวอร์! 👋", color=discord.Color.green())
        if member.avatar: embed.set_thumbnail(url=member.avatar.url)
        await channel.send(embed=embed)

@bot.event
async def on_member_leave(member):
    """เมื่อมีสมาชิกออกจากเซิร์ฟเวอร์ (ใช้ Intent: members)"""
    channel = bot.get_channel(GOODBYE_CHANNEL_ID)
    if channel:
        embed = discord.Embed(title="ลาก่อน...", description=f"{member.name} ({member.mention}) ได้ออกจากเซิร์ฟเวอร์ไปแล้ว 😢", color=discord.Color.red())
        if member.avatar: embed.set_thumbnail(url=member.avatar.url)
        await channel.send(embed=embed)


# 4. หมวด: ปฏิสัมพันธ์ (Interaction) - Reaction Roles (ใช้ Intent: reactions)
@bot.event
async def on_raw_reaction_add(payload):
    """เมื่อมีการเพิ่ม Reaction (ให้บทบาท)"""
    if payload.message_id != REACTION_MESSAGE_ID or payload.user_id == bot.user.id:
        return
    emoji_key = str(payload.emoji)
    if emoji_key not in ROLE_MAP:
        return
        
    guild = bot.get_guild(payload.guild_id)
    if not guild: return

    role = guild.get_role(ROLE_MAP[emoji_key])
    member = payload.member
    if not role or not member: return

    try:
        await member.add_roles(role, reason="Reaction Role")
        print(f"ให้บทบาท {role.name} กับ {member.name}")
    except discord.Forbidden:
        print(f"ไม่มีสิทธิ์ให้บทบาท {role.name} (ตรวจสอบ Hierarchy)")

@bot.event
async def on_raw_reaction_remove(payload):
    """เมื่อมีการลบ Reaction ออก (ลบบทบาท)"""
    if payload.message_id != REACTION_MESSAGE_ID or payload.user_id == bot.user.id:
        return
    emoji_key = str(payload.emoji)
    if emoji_key not in ROLE_MAP:
        return

    guild = bot.get_guild(payload.guild_id)
    if not guild: return

    role = guild.get_role(ROLE_MAP[emoji_key])
    member = guild.get_member(payload.user_id)
    if not role or not member: return

    try:
        await member.remove_roles(role, reason="Reaction Role Removed")
        print(f"ลบบทบาท {role.name} จาก {member.name}")
    except discord.Forbidden:
        print(f"ไม่มีสิทธิ์ลบบทบาท {role.name} (ตรวจสอบ Hierarchy)")


# 5. หมวด: กิจกรรม/ความสนุก (Fun)
@bot.command(name='hello')
async def hello(ctx):
    """ทักทายง่ายๆ"""
    await ctx.send(f"สวัสดีครับคุณ {ctx.author.display_name}! มีอะไรให้ช่วยไหมครับ?")

@bot.command(name='dice')
async def dice(ctx):
    """ทอยลูกเต๋า 1-6"""
    import random
    result = random.randint(1, 6)
    await ctx.send(f"🎲 คุณทอยลูกเต๋าได้หมายเลข **{result}**")

# 6. การจัดการข้อผิดพลาด (Error Handling)
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ คุณใส่ข้อมูลไม่ครบถ้วน กรุณาตรวจสอบการใช้งานคำสั่ง (ดูที่ `!help [คำสั่ง]`)")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ คุณไม่มีสิทธิ์เพียงพอในการใช้คำสั่งนี้")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("❌ บอทไม่มีสิทธิ์เพียงพอในการทำงานนี้ (กรุณาให้สิทธิ์บอท `kick_members` หรือ `ban_members`)")
    elif isinstance(error, commands.CommandNotFound):
        # ไม่ต้องตอบกลับเพื่อไม่ให้รบกวนการแชท
        pass
    else:
        print(f"เกิดข้อผิดพลาดที่ไม่คาดคิด: {error}")
        # await ctx.send(f"❌ เกิดข้อผิดพลาดที่ไม่คาดคิด: {error}") # เปิดบรรทัดนี้เพื่อ debug

server_on()

# รันบอท
try:
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))
except discord.LoginFailure:
    print("เกิดข้อผิดพลาด: Token ไม่ถูกต้อง หรือไม่ได้เปิด Intents ใน Developer Portal")
except Exception as e:
    print(f"เกิดข้อผิดพลาดในการรันบอท: {e}")
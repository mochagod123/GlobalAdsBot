import discord
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient
import time
import json
import asyncio

async_db = AsyncIOMotorClient("mongodb://localhost:27017")["AdsBot"]

COOLDOWN_TIMEGC = 10
cooldown = {}

bot = commands.Bot(command_prefix="ad!", help_command=None, intents=discord.Intents.all())

@bot.event
async def on_ready():
    await bot.tree.sync()

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    
    if not message.content:
        return
    
    db_ads = async_db["Global"]
    try:
        dbfind_ads = await db_ads.find_one({"Channel": message.channel.id}, {"_id": False})
    except:
        pass
    if dbfind_ads is None:
        await bot.process_commands(message)
        return

    current_time = time.time()
    last_message_time = cooldown.get(message.guild.id, 0)
    if current_time - last_message_time < COOLDOWN_TIMEGC:
        return
    cooldown[message.guild.id] = current_time

    async for channel in db_ads.find():
        if channel["Channel"] == message.channel.id:
            continue
        if message.guild.icon:
            icon = message.guild.icon.url
        else:
            icon = None
        if message.author.avatar:
            avatar = message.author.avatar.url
        else:
            avatar = message.author.default_avatar.url
        await bot.get_channel(channel["Channel"]).send(embed=discord.Embed(title=f"{message.author.name}/{message.author.id}", description=message.content, color=discord.Color.purple()).set_footer(text=message.guild.name, icon_url=icon).set_thumbnail(url=avatar))
        await asyncio.sleep(2)

@bot.hybrid_command(name="join", with_app_command=True, description="グローバル宣伝に参加します。")
@commands.cooldown(2, 10)
async def join_adglobal(ctx: commands.Context):
    await async_db["Global"].replace_one(
        {"Channel": ctx.channel.id, "Guild": ctx.guild.id}, 
        {"Channel": ctx.channel.id, "Guild": ctx.guild.id}, 
        upsert=True
        )
    await ctx.reply("参加しました！", ephemeral=True)

@bot.hybrid_command(name="leave", with_app_command=True, description="グローバル宣伝から脱退します。")
@commands.cooldown(2, 10)
async def leave_adglobal(ctx: commands.Context):
    await async_db["Global"].delete_one(
        {"Channel": ctx.channel.id, "Guild": ctx.guild.id}, 
    )
    await ctx.reply("脱退しました！", ephemeral=True)

@bot.hybrid_command(name="rule", with_app_command=True, description="グローバル宣伝のルールを取得します。")
@commands.cooldown(2, 10)
async def rule_adglobal(ctx: commands.Context):
    await ctx.reply(embed=discord.Embed(title="グローバル宣伝のルール", color=discord.Color.purple(), description="""
ルール
・エロ鯖を貼らない。
・ショップ鯖を貼らない。
・荒らし関連の鯖を貼らない。
・運営が禁止したものを貼らない。
・自分が貼ったら、ほかの人が貼るまで貼らない。
・スパムをしない。
以上です。
"""))

bot.run("Token")

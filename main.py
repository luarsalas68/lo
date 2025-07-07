import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()
prefix = ">"
bot_token = os.getenv("DISCORD_TOKEN")

# Comma-separated allowed user ids in .env: "123456789012345678,987654321098765432"
allowed_users = os.getenv("ALLOWED_USER_IDS", "")
if allowed_users.strip():
    allowed_users = [int(uid.strip()) for uid in allowed_users.split(",") if uid.strip()]
else:
    allowed_users = []

bot = commands.Bot(command_prefix=lambda _, msg: prefix, self_bot=True)
annoy_target = None
annoy_interval = 5
self_react_emoji = None
self_react_enabled = False

def is_allowed():
    async def predicate(ctx):
        if not allowed_users or ctx.author.id in allowed_users:
            return True
        else:
            await ctx.send("you can't use this command")
            return False
    return commands.check(predicate)

@bot.command()
@is_allowed()
async def prefix(ctx, new_prefix: str):
    global prefix
    prefix = new_prefix
    await ctx.send(f"Prefix changed to `{prefix}`")

@bot.command()
@is_allowed()
async def massban(ctx, delay: int = 1000):
    for member in ctx.guild.members:
        try:
            await ctx.guild.ban(member)
            await asyncio.sleep(delay / 1000)
        except Exception:
            continue
    await ctx.send("Massban completed.")

@bot.command()
@is_allowed()
async def masskick(ctx, delay: int = 1000):
    for member in ctx.guild.members:
        try:
            await ctx.guild.kick(member)
            await asyncio.sleep(delay / 1000)
        except Exception:
            continue
    await ctx.send("Masskick completed.")

@bot.command()
@is_allowed()
async def annoy(ctx, user_id: int):
    global annoy_target
    annoy_target = user_id
    await ctx.send(f"Annoying user {user_id}")

@bot.command()
@is_allowed()
async def astop(ctx):
    global annoy_target
    annoy_target = None
    await ctx.send("Stopped annoying.")

@bot.command()
@is_allowed()
async def ainterval(ctx, milliseconds: int):
    global annoy_interval
    annoy_interval = milliseconds // 1000
    await ctx.send(f"Message delete interval set to {annoy_interval}s.")

@bot.command()
@is_allowed()
async def ahelp(ctx):
    helpmsg = (
        "```diff\n"
        "+ Třôℓℓßôж™ v2.4 +\n"
        "=====================================\n"
        "+ >prefix <new_prefix> - Change the command prefix for the bot +\n"
        "+ >massban <delay> - Start a mass ban with a specified delay in milliseconds +\n"
        "+ >masskick <delay> - Start a mass kick with a specified delay in milliseconds +\n"
        "+ >annoy <user_id> - Set a target user ID to annoy by replying to their messages +\n"
        "+ >astop - Stop annoying the target user +\n"
        "+ >ainterval <milliseconds> - Set how long command outputs stay before being deleted +\n"
        "+ >ahelp - Display this help message +\n"
        "+ >aspam <message> <count> <delay> - Spam a message multiple times with a specified delay +\n"
        "+ >apurge <milliseconds> <amount> - Purge messages sent by selfbot +\n"
        "+ >whois <user_id> - Display detailed information about a user +\n"
        "+ >quickcage <@user> - Quickcage a user's mom by sending an image and message +\n"
        "+ >sreact <emoji> - Sets an emoji to automatically react to your own messages. +\n"
        "+ >rstop - Disables the self-reaction feature. +\n"
        "=====================================\n"
        "```"
    )
    await ctx.send(helpmsg)

@bot.command()
@is_allowed()
async def aspam(ctx, *, args):
    try:
        msg, count, delay = args.rsplit(' ', 2)
        count = int(count)
        delay = float(delay) / 1000
    except:
        await ctx.send("Usage: >aspam <message> <count> <delay>")
        return
    for _ in range(count):
        m = await ctx.send(msg)
        await asyncio.sleep(delay)
        try:
            await m.delete()
        except:
            pass

@bot.command()
@is_allowed()
async def apurge(ctx, milliseconds: int, amount: int):
    deleted = 0
    async for message in ctx.channel.history(limit=100):
        if message.author.id == bot.user.id and deleted < amount:
            try:
                await message.delete(delay=milliseconds / 1000)
                deleted += 1
            except:
                continue
    await ctx.send(f"Purged {deleted} messages.")

@bot.command()
@is_allowed()
async def whois(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    embed = discord.Embed(title="User Info", description=f"ID: {user.id}")
    embed.add_field(name="Name", value=str(user))
    if user.avatar:
        embed.set_thumbnail(url=user.avatar.url)
    await ctx.send(embed=embed)

@bot.command()
@is_allowed()
async def quickcage(ctx, user: discord.User):
    await ctx.send("Caging your mom...")  # Customize message
    await ctx.send("https://i.imgur.com/yourcageimage.jpg")  # Replace with your image URL

@bot.command()
@is_allowed()
async def sreact(ctx, emoji: str):
    global self_react_emoji, self_react_enabled
    self_react_emoji = emoji
    self_react_enabled = True
    await ctx.send(f"Self-reaction enabled with {emoji}")

@bot.command()
@is_allowed()
async def rstop(ctx):
    global self_react_enabled
    self_react_enabled = False
    await ctx.send("Self-reaction disabled.")

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    # Annoy
    if annoy_target and message.author.id == annoy_target:
        m = await message.channel.send(f"{message.author.mention} 🤡")
        await asyncio.sleep(annoy_interval)
        await m.delete()
    # Self reaction
    if self_react_enabled and message.author.id == bot.user.id and self_react_emoji:
        try:
            await message.add_reaction(self_react_emoji)
        except:
            pass

if __name__ == "__main__":
    bot.run(bot_token, bot=False)
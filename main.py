import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

# Carga el token desde .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=">", self_bot=True, intents=intents)

# Variables globales
react_enabled = False
react_emoji = None
react_channel_id = None
react_task = None
stop_spam = False
stop_react = False
repeat_task = None
repeat_message = None
repeat_delay = 0

@bot.event
async def on_ready():
    print(f"✅ Selfbot conectado como {bot.user}")

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if react_enabled and not stop_react and message.channel.id == react_channel_id and message.author != bot.user:
        try:
            await message.add_reaction(react_emoji)
        except Exception as e:
            print(f"Error al reaccionar: {e}")

@bot.command(name='s')
async def say(ctx, *, message):
    try:
        await ctx.send(message)
        await ctx.message.delete()
    except Exception as e:
        print(f"Error en >s: {e}")

@bot.command(name='sm')
async def spam(ctx, cantidad: int, tiempo: float, *, mensaje="Mensaje"):
    global stop_spam
    stop_spam = False
    try:
        for _ in range(cantidad):
            if stop_spam:
                break
            await ctx.send(mensaje)
            await asyncio.sleep(tiempo)
    except Exception as e:
        print(f"Error en >sm: {e}")

@bot.command(name='stop')
async def stop(ctx):
    global stop_spam, stop_react, repeat_task
    stop_spam = True
    stop_react = True
    if repeat_task is not None:
        repeat_task.cancel()
        repeat_task = None
    try:
        await ctx.send("⛔ Spam y reacciones detenidas.")
    except:
        pass

@bot.command(name='purge')
async def purge(ctx, cantidad: int):
    try:
        await ctx.message.delete()
        messages = await ctx.channel.purge(limit=cantidad + 1, check=lambda m: m.author == bot.user)
        print(f"🧹 Se eliminaron {len(messages)} mensajes del selfbot.")
    except Exception as e:
        print(f"Error en >purge: {e}")

@bot.command(name='repeat')
async def repeat(ctx, delay: float, *, message=None):
    global repeat_task, repeat_message, repeat_delay
    try:
        if message is None:
            async for msg in ctx.channel.history(limit=10):
                if msg.author == ctx.author and not msg.content.startswith(">repeat"):
                    repeat_message = msg.content
                    break
        else:
            repeat_message = message
        repeat_delay = delay
        if repeat_task is not None:
            repeat_task.cancel()
        repeat_task = asyncio.create_task(repeat_message_task(ctx.channel.id))
        await ctx.send(f"🔁 Repetición iniciada cada {repeat_delay} segundos: `{repeat_message}`")
    except Exception as e:
        print(f"Error en >repeat: {e}")

async def repeat_message_task(channel_id):
    channel = bot.get_channel(channel_id)
    while True:
        try:
            await channel.send(repeat_message)
            await asyncio.sleep(repeat_delay)
        except Exception as e:
            print(f"Error en repeat loop: {e}")
            break

@bot.command(name='areact')
async def areact(ctx, canal_id: int, duracion, emoji):
    global react_enabled, react_emoji, react_channel_id, react_task, stop_react
    react_enabled = True
    react_emoji = emoji
    react_channel_id = canal_id
    stop_react = False

    try:
        await ctx.message.add_reaction('👌')
        print(f"🔁 Reacción automática activada en canal {canal_id} con {emoji}")
    except:
        pass

    if react_task is not None:
        react_task.cancel()
        react_task = None

    if duracion.lower() != "inf":
        try:
            segundos = int(duracion)
            react_task = asyncio.create_task(react_auto(segundos))
        except ValueError:
            await ctx.send("❌ Duración inválida. Usa un número entero o 'inf'.")

async def react_auto(duration):
    await asyncio.sleep(duration)
    global react_enabled
    react_enabled = False
    print("⏱ Reacción automática detenida por tiempo.")

@bot.command(name='cmds')
async def cmds(ctx):
    embed = discord.Embed(title="📜 Selfbot Commands", color=0x00ff00)
    embed.add_field(name=">s <mensaje>", value="Envía un mensaje y lo elimina.", inline=False)
    embed.add_field(name=">sm <cantidad> <tiempo> <mensaje?>", value="Spamea mensajes con intervalo.", inline=False)
    embed.add_field(name=">purge <número>", value="Elimina tus últimos mensajes.", inline=False)
    embed.add_field(name=">repeat <delay> <mensaje?>", value="Repite un mensaje cada X segundos.", inline=False)
    embed.add_field(name=">stop", value="Detiene spam y repeticiones.", inline=False)
    embed.add_field(name=">areact <canal_id> <duración> <emoji>", value="Reacciona automáticamente a mensajes en un canal.", inline=False)
    await ctx.send(embed=embed)

bot.run(TOKEN)

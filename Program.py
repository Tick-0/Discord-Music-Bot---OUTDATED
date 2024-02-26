#Import dependencies
import discord
import asyncio
import os
import random
import ffmpeg

from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from discord import TextChannel

from youtube_dl import YoutubeDL

from random import shuffle

#setting up global variables
global PAUSE
PAUSE = False

global QUEUE
QUEUE = []
MTQ = []

global LOOP
LOOP = False

#preparing discord api and YDL
client = commands.Bot(command_prefix=".")  

players = {}


#is ready?
@client.event  
async def on_ready():
    print("Bot online")
    


# makes bot join users voice channel
@client.command()
async def join(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
 
#kicks bot from voice channel
@client.command()
async def kick(ctx):
    global check
    check = False
    PAUSE = False
    QUEUE.clear()
    client = ctx.guild.voice_client
    if client.is_connected():
        await client.disconnect()
    else:
        await ctx.send("Bot is not currently connected to a channel.")
        
#Turns on Queue Loop
@client.command()
async def loop(ctx):
    global LOOP
    if LOOP == False:
        LOOP = True
    else:
        LOOP = False

# play sound from youtube video
@client.command()
async def play(ctx, url):
        global check
        asyncio.create_task(queue_loop(ctx,url))
        global QUEUE
        global MTQ
        if QUEUE != MTQ:
            await ctx.send("Song added to Queue")
            QUEUE.append(str(url))        
        else:
            await ctx.send("Bot is now playing")
            QUEUE.append(str(url))
            
#main song playing function            
async def queue_loop(ctx,url):
    global YDL_SETTINGS
    YDL_SETTINGS = {"format": "bestaudio", "noplaylist": "True"}
    FFMPEG_SETTINGS = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", "options": "-vn"}
    voice = get(client.voice_clients, guild=ctx.guild)
    global QUEUE
    global PAUSE
    global check
    global MTQ
    check = True 
    while check == True:   
        await asyncio.sleep(1)
        if PAUSE == False and not voice.is_playing(): 
            if QUEUE != MTQ:                                              
                with YoutubeDL(YDL_SETTINGS) as ydl:
                    PLAY_NOW = QUEUE.pop(0)
                    info = ydl.extract_info(PLAY_NOW, download=False)
                    if LOOP == True:
                        QUEUE.append(PLAY_NOW)
                URL = info["url"]
                voice.play(FFmpegPCMAudio(URL, **FFMPEG_SETTINGS))
                voice.is_playing()
                
        
                

#shuffle the queue
@client.command()
async def shuffle(ctx):
    global QUEUE
    random.shuffle(QUEUE)
    await ctx.send("Queue has been shuffled")
    
#display Queue
@client.command()
async def queue(ctx):
    global QUEUE
    q = []
    for i in range(len(QUEUE)):
        with YoutubeDL(YDL_SETTINGS) as ydl:
            info = ydl.extract_info(QUEUE[i], download=False)
            await ctx.send(str(info["title"]))
            

# Pause song
@client.command()
async def pause(ctx):
    global PAUSE
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        PAUSE = True
        voice.pause()
        await ctx.send("Bot has been paused")


# resume song
@client.command()
async def resume(ctx):
    global PAUSE
    voice = get(client.voice_clients, guild=ctx.guild)
    if not voice.is_playing():
        voice.resume()
        PAUSE = False
        await ctx.send("Bot is resuming")


# command to stop voice
@client.command()
async def skip(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.stop()
        await ctx.send("Skipped")
    if not voice.is_playing():
        await ctx.send("No Song Playing")


# clears QUEUE
@client.command()
async def clear(ctx):
    global QUEUE
    QUEUE.clear()
    await ctx.send("Queue has been cleared.")

#checks bot latency
@client.command()
async def ping(ctx):
    await ctx.send(f"Pong! ~~{round(client.latency * 1000)}ms~~")
    print (f"{ctx.message.author} used Ping")


#executes main
client.run("Bot Token Here")

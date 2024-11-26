import discord
import os
from dotenv import load_dotenv
import random
from discord.ext import commands

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Bot(intents=intents)  # Use discord.Bot directly
Bot = commands.Bot(command_prefix='/', intents=intents)

gif_list = {
    "hug": [ "https://media.giphy.com/media/yziFo5qYAOgY8/giphy.gif?cid=790b7611zdcjdrswkeb6a0cihk6sa9cwjgbw2w49kvbpipg4&ep=v1_gifs_search&rid=giphy.gif&ct=g",
            "https://media.giphy.com/media/ZQN9jsRWp1M76/giphy.gif?cid=790b7611zdcjdrswkeb6a0cihk6sa9cwjgbw2w49kvbpipg4&ep=v1_gifs_search&rid=giphy.gif&ct=g"

    ],
    "pat": ["https://media.giphy.com/media/Z7x24IHBcmV7W/giphy.gif?cid=ecf05e47lntsqr4sbboxyjpkaxqgv8lp94oqurjdd4jrgcgw&ep=v1_gifs_related&rid=giphy.gif&ct=g",
            "https://media.giphy.com/media/SSPW60F2Uul8OyRvQ0/giphy.gif?cid=ecf05e475aed1apcxfc4our9wpobyyo84645mwurfi3xssti&ep=v1_gifs_related&rid=giphy.gif&ct=g"

    ]
}

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.content.startswith('Hello LeevBot'):
        await message.channel.send('Hello!')
    
    if message.content.startswith('LeevBot, What is the best fruit ever?'):
        await message.channel.send('Bananas fr')

    if message.content.startswith('Meow'):
        await message.channel.send('Meow')

# Define a slash command
@bot.command(description="Sends the bot's latency.")
async def ping(ctx):  # A slash command will be created with the name "ping"
    await ctx.respond(f"Pong! Latency is {bot.latency}")

@bot.command(description="Sends a hug gif.")
async def hug(ctx):
    if "hug" in gif_list:
        gif = random.choice(gif_list["hug"])
        await ctx.send(gif)
    else:
        await ctx.send("No hugs found 😔")

@bot.command(description="Sends a pat gif.")
async def pat(ctx):
    if "pat" in gif_list:
        gif = random.choice(gif_list["pat"])
        await ctx.send(gif)
    else:
        await ctx.send("No pats found 😔")

bot.run(os.getenv('TOKEN'))
import asyncio
from io import BytesIO
import threading
import aiohttp
import discord
import os
import random
from dotenv import load_dotenv
from discord.ext import commands
from discord import option
from itertools import cycle
import json

load_dotenv()
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(intents=intents) 

CHANNEL_ID = 1281444467584532514

user_gender = {}

@bot.event
async def on_ready():
    await bot.sync_commands()
    print(f'We have logged in as {bot.user}')
    await bot.get_channel(CHANNEL_ID).send("🤖 Bot is waking up!")


def load_gifs():
    # with open("gifs.json","r") as file:
    # with open("some_out.json","r") as file:
    with open(os.getenv('GIF_FILE'),"r") as file:
        return json.load(file)
    
gif_data = load_gifs()

def load_user_data():
    if os.path.exists("user_data.json"):
        with open ("user_data.json", "r") as file:
            return json.load(file)
    return {}

user_gender = load_user_data()

def save_user_data():
    with open("user_data.json", "w") as file:
        json.dump(user_gender, file, indent=4)
    

@bot.command(description="Registers your gender so you get more customized gifs")
async def register(ctx, gender):
    """Allows users to register their gender as 'male' or 'female'."""
    gender = gender.lower()
    if gender not in ['male', 'female']:
        await ctx.respond("Invalid gender! Please choose 'male' or 'female'. I don't accept walmart bags. Please input your biological gender.")
        return
    user_gender[str(ctx.author.id)] = gender
    save_user_data()

    await ctx.respond(f"{ctx.author.mention}, your gender has been set to **{gender}**.")


@bot.command(description="Send a hug, kiss, pat, or highfive.")
@option('action', description='Choose what to do', choices = gif_data.keys())
async def action(ctx, action: str, user: discord.Member):
    """Sends a GIF based on the action and gender combination."""
    action = action.lower()
    valid_actions = gif_data.keys()

    if action not in valid_actions:
        await ctx.respond(f"Invalid action! Choose from: {', '.join(valid_actions)}.")
        return

    # Get sender and recipient gender
    sender_gender = user_gender.get(str(ctx.author.id))
    recipient_gender = user_gender.get(str(user.id))

    if not sender_gender:
        await ctx.respond(f"{ctx.author.mention}, please register your gender using `/register male` or `/register female`.")
        return
    if not recipient_gender:
        await ctx.respond(f"{user.mention} has not registered their gender yet. Make them do it!!\n Selecting random one for now")
        possible_genders = [gender_pair.split('_')[1]
                            for gender_pair in gif_data[action].keys() 
                            if gender_pair.startswith(sender_gender)]
        recipient_gender = random.choice(possible_genders)
    
    gif_category = f"{sender_gender}_{recipient_gender}"

    # Fetch a random GIF asynchronously based on the action
    if gif_category in gif_data[action]:
        gif_url = random.choice(gif_data[action][gif_category])
        embed = discord.Embed(
            description=f"{ctx.author.mention} gives a {action} to {user.mention}! 💖",
            color=discord.Color.random(),
        )
        embed.set_image(url=gif_url)
        print(f"Replying to {ctx.author.mention}-> {action} -> {user.mention} with {gif_url}")
        await ctx.respond(embed=embed)
        # await ctx.respond(gif_url)
        # await ctx.respond(content=gif_url, embed=embed)
        # embed_video = discord.EmbedMedia(url=gif_url)
        # await ctx.respond(embed_video)
        # embed_field = discord.EmbedField('Some name',gif_url,True)
        # await ctx.respond(embed_field)
        # embed.add_field(embed_field)
        # await ctx.respond(embed=embed)
    else:
        await ctx.respond("Sorry, I couldn't find a suitable GIF. 😔")

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

# Basic ping command to check latency
@bot.command(description="Sends the bot's latency.")
async def ping(ctx):
    await ctx.respond(f"Pong! Latency is {bot.latency}")

# Run the bot with the token from .env
# bot.run(os.getenv('TOKEN'))
async def run_bot():
    try:
        print("🤖 Bot is waking up!")
        print("To shut down, type 'q' and press Enter\n")
        await bot.start(os.getenv('TOKEN'))
    except Exception as e:
        print(f"An error occurred: {e}")

async def main():
    # Create tasks for bot and input monitoring
    bot_task = asyncio.create_task(run_bot())

    # Input monitoring loop
    while True:
        user_input = await asyncio.get_event_loop().run_in_executor(None, input)
        
        if user_input.lower() == 'q':
            print("\n🌙 Shutting down bot...")
            
            await bot.get_channel(CHANNEL_ID).send("I am going for a nap...")
            # Cancel the bot task
            bot_task.cancel()
            
            # Close the bot connection
            await bot.close()
            
            # Break the monitoring loop
            break

    print("Bot has been shut down.")

if __name__ == '__main__':
    asyncio.run(main())
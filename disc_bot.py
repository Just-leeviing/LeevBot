import asyncio
import threading
import discord
import os
import random
import time
from dotenv import load_dotenv
from discord.ext import commands
import aiohttp
from itertools import cycle

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Bot(intents=intents)  # Use discord.Bot directly

CHANNEL_ID = 1281444467584532514
# Dictionary to store user gender registrations
user_gender = {}

# Cache for storing fetched GIFs and managing shuffle cycles
gif_cache = {}

@bot.event
async def on_ready():
    await bot.sync_commands()
    print(f'We have logged in as {bot.user}')
    await bot.get_channel(CHANNEL_ID).send("🤖 Bot is waking up!")

# Function to fetch a random GIF from Giphy asynchronously
async def fetch_gif(action):
    current_time = time.time()

    # Check if the action has a valid cached result within the last 10 minutes
    if action in gif_cache and current_time - gif_cache[action]['timestamp'] < 600:
        return next(gif_cache[action]['gif_cycle'])

    # Otherwise, fetch new GIFs from the Giphy API
    url = "https://api.giphy.com/v1/gifs/search"
    params = {
        "api_key": os.getenv('GIPHY_API_KEY'),
        "q": action,
        "limit": 20,  # Fetch up to 20 GIFs
        "rating": "pg-13"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                if data['data']:
                    gifs = [gif['images']['original']['url'] for gif in data['data']]
                    random.shuffle(gifs)  # Shuffle GIFs to avoid repetition
                    gif_cache[action] = {'gif_cycle': cycle(gifs), 'timestamp': current_time}
                    return next(gif_cache[action]['gif_cycle'])

    return None


@bot.command()
async def register(ctx, gender):
    """Allows users to register their gender as 'male' or 'female'."""
    gender = gender.lower()
    if gender not in ['male', 'female']:
        await ctx.respond("Invalid gender! Please choose 'male' or 'female'. I don't accept walmart bags. Please input your biological gender.")
        return
    user_gender[ctx.author.id] = gender
    await ctx.respond(f"{ctx.author.mention}, your gender has been set to **{gender}**.")


@bot.command(description="Send a hug, kiss, pat, or highfive.")
async def action(ctx, action: str, user: discord.Member):
    """Sends a GIF based on the action and gender combination."""
    action = action.lower()
    valid_actions = ["hug", "kiss", "pat", "highfive"]

    if action not in valid_actions:
        await ctx.respond(f"Invalid action! Choose from: {', '.join(valid_actions)}.")
        return

    # Get sender and recipient gender
    sender_gender = user_gender.get(ctx.author.id)
    recipient_gender = user_gender.get(user.id)

    if not sender_gender:
        await ctx.respond(f"{ctx.author.mention}, please register your gender using `/register male` or `/register female`.")
        return
    if not recipient_gender:
        await ctx.respond(f"{user.mention} has not registered their gender yet.")
        return

    # Fetch a random GIF asynchronously based on the action
    gif_url = await fetch_gif(action)
    if gif_url:
        embed = discord.Embed(
            description=f"{ctx.author.mention} gives a {action} to {user.mention}! 💖",
            color=discord.Color.random()
        )
        embed.set_image(url=gif_url)
        await ctx.respond(embed=embed)
    else:
        await ctx.respond("Sorry, I couldn't find a suitable GIF. 😔")

# Event listener for simple message responses (optional)
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
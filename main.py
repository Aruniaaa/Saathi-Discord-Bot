import discord
from discord.ext import commands
import random
import asyncio
import logging
from dotenv import load_dotenv
import os
try:
 from bad_words import bad_words
except ImportError:
    bad_words = []
import re
import numpy as np
from discord import app_commands
active_games = {}
from datetime import datetime, timedelta
import economy


# ₊˚ ‿︵‿︵‿︵୨୧ · · ♡ · · ୨୧‿︵‿︵‿︵ ˚₊


load_dotenv()
token = os.getenv("DISCORD_BOT_TOKEN")
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.all()
intents.message_content = True  
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)
tree = bot.tree

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")


#₊˚ ‿︵‿︵‿︵୨୧ · · ♡ · · ୨୧‿︵‿︵‿︵ ˚₊


@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name='general')
    if channel:
        await channel.send(f"Welcome to the server, {member.mention}! 🎉")
    try:
        await member.send(f"Hey {member.name}! Welcome to the server, have fun, make new friends, and follow the rules!💗")
    except discord.Forbidden:
        print(f"Could not send a welcome message to {member.name}. They might have DMs disabled.")


# ₊˚ ‿︵‿︵‿︵୨୧ · · ♡ · · ୨୧‿︵‿︵‿︵ ˚₊


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Handle bad words filtering
    msg_content = message.content.lower()
    for word in bad_words:
        pattern = r'\b' + re.escape(word) + r'\b'
        if re.search(pattern, msg_content):
            await message.delete()
            await message.channel.send(f"🚫 {message.author.mention} please avoid using bad language and let's keep this clean!")
            return  

    # Handle active games logic
    user_id = message.author.id
    if user_id in active_games:
        guess = message.content.upper().split()
        code = active_games[user_id]["code"]
        counter = active_games[user_id]["counter"]

        if len(guess) != len(code):
            await message.channel.send("❌ You guessed more or fewer letters than needed. Please guess exactly 4 letters, separated by spaces.")
            return

        correct_positions = 0
        incorrect_positions = 0

        for i in range(len(code)):
            if guess[i] == code[i]:
                correct_positions += 1
            elif guess[i] in code:
                incorrect_positions += 1

        if correct_positions == len(code):
            await message.channel.send(f"✅ You guessed the code! `{code}`\nIt took you **{counter}** attempts. Good job!")
            del active_games[user_id]
        else:
            await message.channel.send(f"🎯 Correct positions: `{correct_positions}` | Wrong positions but correct letter: `{incorrect_positions}`")
            active_games[user_id]["counter"] += 1

    await bot.process_commands(message)

@bot.event
async def on_member_remove(member):
    channel = discord.utils.get(member.guild.text_channels, name='general')
    if channel:
        await channel.send(f"{member.name} has left the server.")
    await member.send(f"We are sad to see you go, {member.name} Hope you enjoyed your stay 👋")

# ₊˚ ‿︵‿︵‿︵୨୧ · · ♡ · · ୨୧‿︵‿︵‿︵ ˚₊

@bot.event
async def on_command_error(ctx, error):
            if isinstance(error, commands.MissingRequiredArgument):
                await ctx.send("⚠️ You missed a required argument. Please check the command usage.")
            elif isinstance(error, commands.MissingRole):
                await ctx.send("⛔ You don't have the required role to use this command.")
            elif isinstance(error, commands.CommandNotFound):
                await ctx.send("❓ This command does not exist. Use `!help` to see the available commands.")
            elif isinstance(error, commands.BadArgument):
                await ctx.send("❌ Invalid argument provided. Please check the command usage.")
            elif isinstance(error, commands.CommandInvokeError):
                await ctx.send("⚙️ An error occurred while executing the command. Please try again later.")
            elif isinstance(error, asyncio.TimeoutError):
                await ctx.send("⏳ You took too long to respond. Please try again.")
            else:
                await ctx.send("🚨 An unexpected error occurred. Please contact the admin.")
            logging.error(f"Error in command {ctx.command}: {error}")


# ₊˚ ‿︵‿︵‿︵୨୧ · · ♡ · · ୨୧‿︵‿︵‿︵ ˚₊


@tree.command(name="help", description="Don't know how to use Saathi? This command will help! 💫")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📖 Saathi Command Guide",
        description="Here's everything you can do with your cosmic buddy! 🌌\nUse `/command_name` to activate each one.",
        color= 0xB39EB5
    )

    # 🌟 Social & Fun Commands
    embed.add_field(name="🧩 General & Games", value="""
`/hello` - Say hello to Saathi 👋  
`/rps` - Play rock, paper, scissors with the bot 🪨📃✂️  
`/flames` - Compatibility check 💞  
`/lovecalc` - Love percentage calc 💖  
`/dice_roll` - Roll a dice 🎲  
`/math` - Solve a math question 🧠  
`/makepoll` - Create a poll 📊  
`/numberguess` - Guess the number game ❓  
`/codegame` - Crack the secret code! 🔐  
`/movierecc` - Get 3 movie recs 🍿  
""", inline=False)

    # 💰 Economy Commands
    embed.add_field(name="💸 Economy & StarDust", value="""
`/balance` - See your StarDust balance ✨  
`/daily` - Claim your daily reward 🎁  
`/work` - Work a job and earn StarDust 💼  
`/beg` - Shamelessly beg the universe 🙏  
`/give` - Share StarDust with others 🌠  
`/shop` - Browse the galactic shop 🛍️  
`/buy` - Purchase an item from the shop 🪙  
""", inline=False)

    # 🪐 Exploration Commands
    embed.add_field(name="🚀 Explore & Discover", value="""
`/explore` - Venture through space and find goodies 🌌  
`/deep_space` - Go on a risky, far-out mission, high reward, high risk! 💀✨  
""", inline=False)

    # 🐾 Pet & Profile System
    embed.add_field(name="🪄 Pets, Titles & Profiles", value="""
`/inventory` - View all your collected items 🎒  
`/equip_pet` - Equip a pet to show off 🐾  
`/equip_title` - Equip a cool title 🏷️  
`/profile` - View your cosmic profile card 🌠  
`/feed` - Feed your favorite pet 🍪  
""", inline=False)

    # Help command itself
    embed.add_field(name="🆘 Help & Info", value="""
`/help` - Show this guide 📖  
""", inline=False)

    embed.set_footer(text=f"Use your commands wisely {interaction.author.mention} 💗")
    embed.set_thumbnail(url="https://i.pinimg.com/originals/d9/e1/41/d9e141c49b6e9e98b973b5b85ceac1c0.gif")
    await interaction.response.send_message(embed=embed)



# ₊˚ ‿︵‿︵‿︵୨୧ · · ♡ · · ୨୧‿︵‿︵‿︵ ˚₊



@tree.command(name='hello', description="Say hi to Saathi!🎀")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f'Hey {interaction.author.mention}!🎀')



# ₊˚ ‿︵‿︵‿︵୨୧ · · ♡ · · ୨୧‿︵‿︵‿︵ ˚₊



# rock paper scissors
@tree.command(name="rps", description="Play a game of rock, paper, scissors with the bot! 🪨📄✂️")
async def rps(interaction: discord.Interaction, user_choice: str):
    options = ['rock', 'paper', 'scissors']
    user_choice = user_choice.lower()

    
    if user_choice not in options:
        await interaction.response.send_message("Invalid choice! Please choose 'rock', 'paper', or 'scissors'.")
        return

    bot_choice = random.choice(options)  # Bot chooses randomly
    await interaction.response.send_message(f'You chose {user_choice} and I chose {bot_choice}.')

    # Game logic
    if user_choice == bot_choice:
        await interaction.followup.send("It's a draw! 🤝")
    elif (user_choice == 'rock' and bot_choice == 'scissors') or \
         (user_choice == 'paper' and bot_choice == 'rock') or \
         (user_choice == 'scissors' and bot_choice == 'paper'):
        await interaction.followup.send("You win! 🎉")
    else:
        await interaction.followup.send("You lose! 😭")


# ₊˚ ‿︵‿︵‿︵୨୧ · · ♡ · · ୨୧‿︵‿︵‿︵ ˚₊



@tree.command(name="flames", description="Check your FLAMES compatibility! 🔥")
@app_commands.describe(your_name="Your name", their_name="Your crush's name")
async def flames(interaction: discord.Interaction, your_name: str, their_name: str):
    await interaction.response.defer()

    your_name_list = list(your_name.lower())
    their_name_list = list(their_name.lower())

    for char in your_name[:]:
        if char in their_name_list:
            your_name_list.remove(char)
            their_name_list.remove(char)

    count = len(your_name_list) + len(their_name_list)
    flames = ['f', 'l', 'a', 'm', 'e', 's']
    index = 0

    while len(flames) > 1:
        index = (index + count - 1) % len(flames)
        flames.pop(index)

    result = flames[0]

    meanings = {
        'f': "friendship 🤝",
        'l': "love ❤️",
        'a': "attraction 💘",
        'm': "marriage 💍",
        'e': "enemies 💢",
        's': "siblings 🍜"
    }

    await interaction.followup.send(f"You two got '{result.upper()}' which means {meanings[result]}")

      

# ₊˚ ‿︵‿︵‿︵୨୧ · · ♡ · · ୨୧‿︵‿︵‿︵ ˚₊

@tree.command(name="lovecalc", description="Test your compatibility by entering your and your crush's name! 💞")
@app_commands.describe(
    your_name="Please enter your name",
    their_name="Please enter your crush's name"
)
async def love_calc(interaction: discord.Interaction, your_name: str, their_name: str):

    your_name = your_name.lower()
    their_name = their_name.lower()

    lst = []
    your_name_list = list(your_name)
    their_name_list = list(their_name)

    for i in your_name_list[:]:
        if i in their_name_list:
            your_name_list.remove(i)
            their_name_list.remove(i)
            lst.append(2)

    for _ in your_name_list:
        lst.append(1)
    for _ in their_name_list:
        lst.append(1)

    def reduce_list(lst):
        while len(lst) > 2:
            new = []
            left = 0
            right = len(lst) - 1
            while left < right:
                new.append(lst[left] + lst[right])
                left += 1
                right -= 1
            if left == right:
                new.append(lst[left])
            lst = new
        return lst

    result = reduce_list(lst)

    # Construct a proper two-digit percentage
    if len(result) == 1:
        percentage = result[0] % 100
    else:
        percentage = int(f"{result[0]:01}{result[1]:01}") % 100

    await interaction.response.send_message(
        f"❤️ Your love compatibility is **{percentage}%** ❤️"
    )



# ₊˚ ‿︵‿︵‿︵୨୧ · · ♡ · · ୨୧‿︵‿︵‿︵ ˚₊


@tree.command(name="dice_roll", description="Roll a dice interactively!")
@app_commands.describe(cmd="Roll the dice (Y/N?)")
async def dice_roll(interaction: discord.Interaction, cmd: str):
    await interaction.response.defer()

    while True:
        try:
            cmd = cmd.lower()

            if cmd in ['y', 'yes']:
                num1 = random.randint(1, 6)
                await interaction.followup.send(f"The number you rolled is {num1} 🎲")
                break
            elif cmd in ['n', 'no']:
                await interaction.followup.send("Thanks for playing!")
                break
            else:
                await interaction.followup.send("Please enter a valid command! (y/n)")
                break
        except asyncio.TimeoutError:
            await interaction.followup.send("You took too long to respond!")
            break


# ₊˚ ‿︵‿︵‿︵୨୧ · · ♡ · · ୨୧‿︵‿︵‿︵ ˚₊


@tree.command(name="math", description="Answer a random math question! 🧮")
@app_commands.describe(max_range="Maximum number for the question")
async def math(interaction: discord.Interaction, max_range: int):
    await interaction.response.defer()

    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel

    operations = ["+", "-", "/", "*"]
    num1 = random.randint(1, max_range)
    num2 = random.randint(1, max_range)
    operation = random.choice(operations)

    if operation == "+":
        correct_answer = num1 + num2
    elif operation == "-":
        correct_answer = num1 - num2
    elif operation == "/":
        correct_answer = round(num1 / num2, 2)
    elif operation == "*":
        correct_answer = num1 * num2

    await interaction.followup.send(f"{num1} {operation} {num2} = ?")

    try:
        msg = await bot.wait_for("message", check=check, timeout=30)
        answer = float(msg.content)
        if round(answer, 2) == round(correct_answer, 2):
            await interaction.followup.send(f"Correct! 🏆")
        else:
            await interaction.followup.send(f"Incorrect ❌ — the correct answer is {correct_answer}")
    except asyncio.TimeoutError:
        await interaction.followup.send("⏰ You took too long to respond!")




# ₊˚ ‿︵‿︵‿︵୨୧ · · ♡ · · ୨୧‿︵‿︵‿︵ ˚₊



@tree.command(name="makepoll", description="Make a yes/no poll!")
@app_commands.describe(
    question="What is your question? (Please ensure it can be answered with a yes/no)"
)
async def makepoll(interaction: discord.Interaction, question: str):
    embed = discord.Embed(
        title="📊 Poll",
        description=question,
        color=discord.Color.blurple()
    )
    embed.set_footer(text="React with 👍 for Yes or 👎 for No.")
    
    await interaction.response.send_message(embed=embed)
    poll_message = await interaction.original_response()
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("👎")

    
# ₊˚ ‿︵‿︵‿︵୨୧ · · ♡ · · ୨୧‿︵‿︵‿︵ ˚₊


@tree.command(name="numberguess", description="Play a number guessing game!")
@app_commands.describe(min_ran="Minimum number", max_ran="Maximum number")
async def numberguess(interaction: discord.Interaction, min_ran: int, max_ran: int):
    await interaction.response.send_message(
        f"🎲 Let's play a number guessing game between **{min_ran}** and **{max_ran}**!\nType your guesses below. Type `quit` to stop.", ephemeral=True
    )

    target = random.randint(min_ran, max_ran)
    counter = 0

    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel

    while True:
        try:
            msg = await bot.wait_for("message", check=check, timeout=60)

            if msg.content.lower() == "quit":
                await interaction.followup.send(f"Goodbye! 👋 The number was **{target}**.", ephemeral=True)
                break

            guess = int(msg.content)
            counter += 1

            if guess == target:
                await interaction.followup.send(f"🎉 You guessed it in {counter} attempts! The number was **{target}**.", ephemeral=True)
                break
            elif guess > target:
                await interaction.followup.send("⬆️ Too high!", ephemeral=True)
            else:
                await interaction.followup.send("⬇️ Too low!", ephemeral=True)
        except asyncio.TimeoutError:
            await interaction.followup.send("⏰ You took too long! Game over.", ephemeral=True)
            break
        except ValueError:
            await interaction.followup.send("⚠️ Please enter a valid number.", ephemeral=True)
        except asyncio.TimeoutError:
            await interaction.followup.send("⏰ You took too long! Game over.", ephemeral=True)
            break

# ₊˚ ‿︵‿︵‿︵୨୧ · · ♡ · · ୨୧‿︵‿︵‿︵ ˚₊



@tree.command(name="codegame", description="Play a game where you guess the secret code!")
async def codegame(interaction: discord.Interaction):
    user_id = interaction.user.id

    possibilities = ['R', 'B', 'G', 'Y', 'O', 'V', 'W']
    code = [random.choice(possibilities) for _ in range(4)]
    hint_possibilities = list(set(code))

    while len(hint_possibilities) < 5:
        ran = random.choice(possibilities)
        if ran not in hint_possibilities:
            hint_possibilities.append(ran)
            break

    random.shuffle(hint_possibilities)
    hint_str = " ".join(hint_possibilities)

    active_games[user_id] = {
        "code": code,
        "counter": 1
    }

    await interaction.response.send_message(f"🎯 Game started! Some of the letters from these hints are in the code:\n`{hint_str}`\nThe code has **{len(code)}** letters. Letters can repeat.\n\nType your guess like this: `R G B Y` (separated by spaces). I’ll wait for your messages!")


# ₊˚ ‿︵‿︵‿︵୨୧ · · ♡ · · ୨୧‿︵‿︵‿︵ ˚₊
     


@tree.command(name="movierecc", description="Get movie recommendations based on your mood!")
@app_commands.describe(
    action_like="On a scale of 10, how much do you like action?",
    romance_like="On a scale of 10, how much do you like romance?",
    category="H - Hollywood\nB - Bollywood\nM - Mixed"
)
async def movierecc(interaction: discord.Interaction, action_like: float, romance_like: float, category: str):

    category = category.lower()
    if category not in ['h', 'b', 'm']:
        await interaction.response.send_message("⚠️ Invalid category! Please choose 'H' for Hollywood, 'B' for Bollywood, or 'M' for Mixed.")
        return
    if not (0 <= action_like <= 10):
        await interaction.response.send_message("⚠️ Please provide a valid score for action (0-10).")
        return
    if not (0 <= romance_like <= 10):
        await interaction.response.send_message("⚠️ Please provide a valid score for romance (0-10).")
        return

 


    await interaction.response.send_message("⚠️ Please note that the recommendations provided by this bot may not be 100% accurate. Enjoy responsibly!")
    async def recommend_movies(action_like, romance_like, movies_dict):
        user = np.array([action_like, romance_like])
        dot_products = []
        new_movie_vectors = []
        dic = {}

        for vec in movies_dict.keys():
            vec_np = np.array(vec)
            new_movie_vectors.append(vec_np)
            dot_products.append(np.dot(vec_np, user))

        for i in range(len(dot_products)):
            dic[dot_products[i]] = new_movie_vectors[i]

        sorted_keys = sorted(dic.keys())
        top3 = [dic[sorted_keys[-i]] for i in range(1, 4)]

        await interaction.followup.send(f"""Film recommendations based on your choices:
1. {movies_dict.get(tuple(top3[0]))}
2. {movies_dict.get(tuple(top3[1]))}
3. {movies_dict.get(tuple(top3[2]))}
Enjoy watching!🍿💗""")



    if category == 'h':
        from movies import hollywood_movies
        await recommend_movies(action_like, romance_like, hollywood_movies)
    elif category == 'b':
        from movies import bollywood_movies
        await recommend_movies(action_like, romance_like, bollywood_movies)
    elif category == 'm':
        from movies import mixed_movies
        await recommend_movies(action_like, romance_like, mixed_movies)
    else:
        await interaction.followup.send("Please enter a valid category and try again!!🌟")

# ₊˚ ‿︵‿︵‿︵୨୧ · · ♡ · · ୨୧‿︵‿︵‿︵ ˚₊
     



"""

ECONOMY SECTION !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!



"""


cooldowns = {
    "work": {},
    "daily": {},
    "beg" : {}
}

@bot.tree.command(name="balance", description="Check your StarDust balance.")
async def balance(interaction: discord.Interaction):
    await interaction.response.defer()  
    await economy.ensure_user(interaction.user.id)
    bal = await economy.get_balance(interaction.user.id)
    await interaction.followup.send(f"🌟 {interaction.user.mention}, you have **{bal} StarDust**!")



@bot.tree.command(name="beg", description="Beg for some StarDust.")
async def beg(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)  # private beg moment lol

    user_id = interaction.user.id
    now = datetime.now()
    await economy.ensure_user(user_id)

    last_time = cooldowns["beg"].get(user_id)
    if last_time and now - last_time < timedelta(minutes=10):
        remaining = timedelta(minutes=10) - (now - last_time)
        mins, secs = divmod(remaining.total_seconds(), 60)
        return await interaction.followup.send(
            f"⏳ You have some dignity left, you can't beg now. Try again in {int(mins)}m {int(secs)}s."
        )

    amount = random.randint(1, 30)
    await economy.add_balance(user_id, amount)
    cooldowns["beg"][user_id] = now
    await interaction.followup.send(f"🥺 You begged and someone gave you **{amount} StarDust**!")



@bot.tree.command(name="work", description="Work to earn StarDust.")
async def work(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    user_id = interaction.user.id
    now = datetime.now()

    last_time = cooldowns["work"].get(user_id)
    if last_time and now - last_time < timedelta(minutes=5):
        remaining = timedelta(minutes=5) - (now - last_time)
        mins, secs = divmod(remaining.total_seconds(), 60)
        return await interaction.followup.send(
            f"⏳ Chilllllllll, you’re tired. Try again in {int(mins)}m {int(secs)}s."
        )

    amount = random.randint(50, 150)
    await economy.add_balance(user_id, amount)
    cooldowns["work"][user_id] = now
    await interaction.followup.send(f"☄️ You worked hard and earned **{amount} StarDust**!")



@bot.tree.command(name="daily", description="Claim your daily StarDust.")
async def daily(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    user_id = interaction.user.id
    now = datetime.now()

    last_time = cooldowns["daily"].get(user_id)
    if last_time and now - last_time < timedelta(hours=24):
        remaining = timedelta(hours=24) - (now - last_time)
        hours, remainder = divmod(remaining.total_seconds(), 3600)
        mins, _ = divmod(remainder, 60)
        return await interaction.followup.send(
            f"🕒 You already claimed your daily. Try again in {int(hours)}h {int(mins)}m."
        )

    amount = random.randint(100, 300)
    await economy.add_balance(user_id, amount)
    cooldowns["daily"][user_id] = now
    await interaction.followup.send(f"💫 You claimed your daily reward of **{amount} StarDust**!")



@bot.tree.command(name="give", description="Give StarDust to another user.")
@app_commands.describe(member="The user to give StarDust to", amount="Amount of StarDust to give")
async def give(interaction: discord.Interaction, member: discord.Member, amount: int):
    await interaction.response.defer()

    if amount <= 0:
        return await interaction.followup.send("❌ Amount must be positive.", ephemeral=True)

    from_id = interaction.user.id
    to_id = member.id

    if from_id == to_id:
        return await interaction.followup.send("❌ You can’t give StarDust to yourself.", ephemeral=True)

    success = await economy.transfer_balance(from_id, to_id, amount)
    if success:
        await interaction.followup.send(f"💸 You gave **{amount} StarDust** to {member.mention}!")
    else:
        await interaction.followup.send("🚫 You aren't that rich bro.", ephemeral=True)





async def load_cogs():
    await bot.load_extension("explore")  
    await bot.load_extension("shop_buy_etc")
async def main():
    await economy.setup()
    await load_cogs()
    await bot.start(token)


asyncio.run(main())

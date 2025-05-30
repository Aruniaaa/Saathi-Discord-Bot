#  Saathi - Your All-in-One Space-Themed Discord Bot 

Saathi is an aesthetic, space-themed multipurpose Discord bot designed for fun, moderation, games, and an in-server economy. It has unique commands, collectible pets, Stardust currency, and an auto detection system that removes and warns the user for upto 320 abuse/profanity/cuss words! 

---

## ✨ Features

### 🌠 General Commands

* `/hello` – Get a friendly greeting
* `/help` – Displays all available commands and guides
* `/dice_roll` – Roll a random dice
* `/math` – Solve a math question

### ❤️ Fun & Games

* `/rps` – Play Rock, Paper, Scissors
* `/flames` – Check your FLAMES compatibility 
* `/lovecalc` – Find your love score 
* `/numberguess` – Guess a number between 1-10
* `/codegame` – Try to guess the secret code 

### 🎬 Entertainment

* `/movierecc` – Get movie recommendations based on your vibe
* `/makepoll` – Create Yes/No polls

### 💰 Economy System

* `/balance` – View your current Stardust
* `/work`, `/beg`, `/daily` – Earn Stardust in different ways
* `/give` – Send Stardust to other users
* `/shop` – Explore the galactic shop (Pets, Titles, Food, Lootboxes, etc.)
* `/buy` – Purchase an item from the shop
* `/inventory` – View your personal inventory
* `/feed` – Feed your pets space snacks
* `/explore` – Find exotic exoplanets and pets
* `/explore_far` – Risky but rewarding space exploration

### 🪐 Customization

* `/equip_pet` – Equip your favorite pet 
* `/equip_title` – Equip a title to showcase in your profile 🏷
* `/profile` – View your aesthetic space-themed profile card 

---

## 🔧 Tech Stack

* **Python 3.10+**
* **discord.py** (with app\_commands)
* **aiosqlite** for asynchronous database handling
* **python-dotenv** for managing secrets
* **NumPy** for logic-based games

---

## 📂 Project Structure

```
saathi/
├── main.py               # Main bot runner
├── economy.py            # Economy logic and database management
├── explore.py            # Explore and deep-space pet discovery logic
├── movies.py             # Movie recommendation command
├── shop_buy_etc.py       # Shop, buy, inventory, and equip logic
├── badwords.txt          # Word list used for moderation filtering
├── badwords.py           # Chat moderation using word list
├── requirements.txt      # Python dependencies
└── .env                  # Create this before running and store your token
```

---

## ✅ Requirements

In your `requirements.txt`:

```
discord.py
python-dotenv
numpy
aiosqlite
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/saathi-bot.git
cd saathi-bot
```

### 2. Set up your `.env`

```
DISCORD_TOKEN=your_discord_bot_token
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the bot

```bash
python bot.py
```

---

## 🌟 Contributions

PRs are welcome! If you want to contribute commands, themes, or features, feel free to fork, go creative, go wild!<3 

---

## 📜 License

This project is licensed under the MIT License.

---


Made by,
> — Arunia

import discord
from discord.ext import commands
from discord import app_commands
import random
import economy
import aiosqlite


async def get_equipped(user_id, table, name_col, extra_col=None):
    query = f"SELECT {name_col}" + (f", {extra_col}" if extra_col else "") + f" FROM {table} WHERE user_id = ? AND equipped = 1"
    async with aiosqlite.connect("saathi_economy.db") as db:
        async with db.execute(query, (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result if result else None
        

async def get_rarest_item(user_id):
    rarity_order = {
        "Common": 1,
        "Uncommon": 2,
        "Rare": 3,
        "Epic": 4,
        "Legendary": 5
    }

    rarest_pet = None
    highest = 0

    async with aiosqlite.connect("saathi_economy.db") as db:
        async with db.execute("SELECT pet_name, rarity FROM user_pets WHERE user_id = ?", (user_id,)) as cursor:
            pets = await cursor.fetchall()
            for name, rarity in pets:
                if rarity_order.get(rarity, 0) > highest:
                    highest = rarity_order[rarity]
                    rarest_pet = f"{name.title()} (*{rarity}*)"

       

    return rarest_pet  

shop_data = {
            "pets": {
                "common": 750,
                "uncommon": 1500,
                "rare": 3275,
                "epic": 7800
            },
            "titles": {
                "Galactic Explorer": 750,
                "Nebula Knight": 1500,
                "Void Warden": 3000,
                "Vacuum Wanderer": 5000,
                "Star Seeker": 7500,
                "Light Fast": 10000,
                "✨ Stardust Royalty ✨": 6000
            },
            "food": {
                "Space Biscuit": 200,
                "Quantum Crunchies": 500,
                "Nebula Cookie": 650,
                "Exoplanet Rolls": 700,
                "Methyle Mocktail": 850,
                "Asteroid Cereal": 900
            },
            "lootboxes": {
                "Basic Crate": 1500,
                "Cosmic Chest": 3500,
                "Legendary Box": 7000
            },
            "nametags": {
                "Name Tag": 1000
            }
        }


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shop_data = shop_data
   

    @app_commands.command(name="shop", description="View items available in the shop by category.")
    @app_commands.describe(category="Category to view: pets, titles, food, lootboxes, nametags")
    async def shop(self, interaction: discord.Interaction, category: str):
        await interaction.response.defer()

        category = category.lower()
        if category not in self.shop_data:
            return await interaction.followup.send("❌ Invalid category. Try pets, titles, food, lootboxes, or nametags.")

        embed = discord.Embed(title=f"🛒 {category.title()} Shop", color=0xF4C2C2)
        for item, price in self.shop_data[category].items():
            embed.add_field(name=item, value=f"{price} StarDust", inline=False)

        await interaction.followup.send(embed=embed)





class Buy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shop_data = shop_data

    @app_commands.command(name="buy", description="Purchase an item from the shop")
    @app_commands.describe(category="What do you want to buy?", item="The item name from that category")
    async def buy(self, interaction: discord.Interaction, category: str, item: str):
        user_id = interaction.user.id

       
        matched_category = next((cat for cat in self.shop_data if cat.lower() == category.lower()), None)
        if not matched_category:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Invalid Category ❌",
                    description="That category doesn't exist. Use `/shop` to see available categories.",
                    color=0xFF746C
                ),
                ephemeral=True
            )

        
        matched_item = next((i for i in self.shop_data[matched_category] if i.lower() == item.lower()), None)
        if not matched_item:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Invalid Item ❌",
                    description="That item doesn't exist in this category. Check spelling or use `/shop`.",
                    color=0xFF746C
                ),
                ephemeral=True
            )

        price = self.shop_data[matched_category][matched_item]
        balance = await economy.get_balance(user_id)

        if balance < price:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Enough Stardust ⚠️",
                    description=f"You need {price} StarDust but you only have {balance}... Time to `/work` or `/explore`!",
                    color=0x808080
                ),
                ephemeral=True
            )

        await economy.remove_balance(user_id, price)



        await interaction.response.send_message(
            embed=discord.Embed(
                title="Purchase Successful 🛒",
                description=f"You bought **{matched_item}** from **{matched_category}** for **{price} StarDust**!",
                color=0xB5E8FF
            )
        )


       
        reward_msg = ""
        if category == "pets":
            from explore import PETS_BY_RARITY  
            rarity = item.capitalize()
            import random
            pet = random.choice(PETS_BY_RARITY[rarity])
            await self.economy.add_pet(user_id, pet, rarity)
            reward_msg = f"You adopted a **{pet}** (*{rarity}*)!"

        elif category == "titles":
            await self.economy.add_title(user_id, item)
            reward_msg = f"You unlocked the title: **{item.title()}**!"

        elif category == "food":
            await self.economy.add_food(user_id, item)
            reward_msg = f"You got a **{item.title()}** for your pet!"

        elif category == "lootboxes":
            await self.economy.give_lootbox(user_id, item)
            reward_msg = f"A mysterious **{item.title()}** has been added to your inventory..."

        elif category == "name tags":
            await self.economy.add_item(user_id, "name tag")
            reward_msg = "A **Name Tag** was added to your inventory. Use it to rename your pet!"

        await interaction.response.send_message(
            embed=discord.Embed(
                title="Purchase Successful ✨",
                description=f"You spent **{price}** StarDust\n{reward_msg}",
                color=0x9CAF88
            )
        )




class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="inventory", description="Check out your inventory 🪐")
    async def inventory(self, interaction: discord.Interaction):
        user = interaction.user
        user_id = user.id
        await interaction.response.defer()

        balance = await economy.get_balance(user_id)
        pets = await economy.get_user_pets(user_id)
        food = await get_user_items(user_id, "user_food", "food_name")
        lootboxes = await get_user_items(user_id, "user_lootboxes", "box_type")
        name_tags = await get_user_items(user_id, "user_items", "item_name")
        titles = await get_user_items(user_id, "user_titles", "title")

       
        def format_list(items, emoji="•"):
            if not items:
                return "None"
            counts = {}
            for item in items:
                counts[item] = counts.get(item, 0) + 1
            return "\n".join([f"{emoji} {name.title()} ×{count}" for name, count in counts.items()])

        pet_section = "None"
        if pets:
            pet_section = "\n".join([
                f"• {name.title()} 〔*{rarity}*〕" for name, rarity in pets
            ])

        embed = discord.Embed(
            title=f"︵︵﹆ . ⁺ . ✦ {user.display_name}'s Inventory ✦ .⁺ .﹆︵︵",
            color=0xB084F7
        )

        embed.add_field(name="👛 StarDust", value=f"**{balance}** ✨", inline=False)
        embed.add_field(name="🐾 Pets", value=pet_section, inline=False)

        embed.add_field(name="🍪 Pet Food", value=format_list(food, "🍽️"), inline=False)
        embed.add_field(name="🎁 Lootboxes", value=format_list(lootboxes, "📦"), inline=False)
        embed.add_field(name="🏷️ Name Tags", value=format_list(name_tags, "🔖"), inline=False)
        embed.add_field(name="🏅 Titles", value=format_list(titles, "📜"), inline=False)

        embed.set_footer(text="‧˚₊꒷꒦︶︶︶ Inventory Powered by Stardust ︶︶︶꒦꒷‧₊˚⊹")
        await interaction.followup.send(embed=embed)


async def get_user_items(user_id: int, table: str, column: str):
    import aiosqlite
    async with aiosqlite.connect("saathi_economy.db") as db:
        async with db.execute(f"SELECT {column} FROM {table} WHERE user_id = ?", (user_id,)) as cursor:
            results = await cursor.fetchall()
            return [row[0] for row in results]




class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="profile", description="View your profile card 🌌")
    async def profile(self, interaction: discord.Interaction):
        user = interaction.user
        user_id = user.id
        await interaction.response.defer()

   
        balance = await economy.get_balance(user_id)
        equipped_pet = await get_equipped(user_id, "user_pets", "pet_name", "rarity")
        equipped_title = await get_equipped(user_id, "user_titles", "title")
        rarest_item = await get_rarest_item(user_id)

        embed = discord.Embed(
            title=f"🌠 {user.display_name}'s Profile 🌠",
            color=0x9C8DF2
        )

        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="🪪 Username", value=f"{user.name}", inline=True)
        embed.add_field(name="✨ Stardust", value=f"{balance}", inline=True)

        embed.add_field(
            name="🏅 Equipped Title",
            value=f"{equipped_title if equipped_title else '*None equipped*'}",
            inline=False
        )
        embed.add_field(
            name="🐾 Companion",
            value=f"{equipped_pet[0]} (*{equipped_pet[1]}*)" if equipped_pet else "*None equipped*",
            inline=False
        )
        embed.add_field(
            name="🔮 Rarest Item",
            value=f"{rarest_item}" if rarest_item else "*No rare items found*",
            inline=False
        )

        embed.set_footer(text="︵﹒₊˚𓂃★ Profile Generated by Saathi Bot ★˚₊﹒︵")
        await interaction.followup.send(embed=embed)




class PetCare(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="feed", description="Feed your currently equipped pet some yummy space food!")
    @app_commands.describe(food_name="Name of the food you want to use (check your inventory)")
    async def feed(self, interaction: discord.Interaction, food_name: str):
        user_id = interaction.user.id
        food_name = food_name.lower()

        # Get pet
        pet = await economy.get_equipped_pet(user_id)
        if not pet:
            return await interaction.response.send_message("You don't have a pet equipped! Use `/equip_pet` first.", ephemeral=True)

        # Get food
        user_food = await economy.get_user_food(user_id)
        user_food_lower = [f.lower() for f in user_food]

        if food_name not in user_food_lower:
            return await interaction.response.send_message("You don't have that food item in your inventory!", ephemeral=True)

        # Feed the pet
        await economy.remove_food(user_id, food_name)
        await economy.add_balance(user_id, 50)  # lil reward

        embed = discord.Embed(
            title="🐾 Feeding Time!",
            description=f"Your pet **{pet[0]}** (*{pet[1]}*) happily munched on a **{food_name.title()}**!\nYou gained **50 StarDust**!",
            color=0xFFCEFE
        )
        embed.set_thumbnail(url="https://i.pinimg.com/originals/d9/e1/41/d9e141c49b6e9e98b973b5b85ceac1c0.gif")

        await interaction.response.send_message(embed=embed)



class EquipUse(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="equip_pet", description="Equip one of your pets to follow you around! 🐾")
    @app_commands.describe(pet_name="The name of the pet you want to equip")
    async def equip_pet(self, interaction: discord.Interaction, pet_name: str):
      await interaction.response.defer()
      user_id = interaction.user.id
      pet_name = pet_name.lower()

      if not await economy.has_pet(user_id, pet_name):
        return await interaction.followup.send(
            embed=discord.Embed(
                title="Pet Not Found ❌",
                description=f"You don't own a pet named `{pet_name}`! Use `/inventory` to see your pets.",
                color=0xFF6B6B
            ),
            ephemeral=True
        )

      await economy.equip_pet(user_id, pet_name)
      await interaction.followup.send(
        embed=discord.Embed(
            title="Pet Equipped ✅",
            description=f"Your pet `{pet_name}` is now following you around. Make sure to take care of your Saathi 💗",
            color=0xB6E3FF
        )
    )
    @app_commands.command(name="equip_title", description="Equip a title to show off your status ✨")
    @app_commands.describe(title="The title you want to equip")
    async def equip_title(self, interaction: discord.Interaction, title: str):
     user_id = interaction.user.id
     title = title.lower()

     if not await economy.has_title(user_id, title):
        return await interaction.followup.send(
            embed=discord.Embed(
                title="Title Not Found ❌",
                description=f"You don't have the title `{title}`! Use `/inventory` to check what you own.",
                color=0xFF6B6B
            ),
            ephemeral=True
        )

     await economy.equip_title(user_id, title)
     await interaction.followup.send(
        embed=discord.Embed(
            title="Title Equipped 👑",
            description=f"You now go by **{title.title()}**. Fancy! 💫",
            color=0xF5D0FE
        )
    )


        
    


async def setup(bot):
    await bot.add_cog(Shop(bot))
    await bot.add_cog(Buy(bot))
    await bot.add_cog(Inventory(bot))
    await bot.add_cog(Profile(bot))
    await bot.add_cog(PetCare(bot))
    await bot.add_cog(EquipUse(bot))


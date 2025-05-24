import random
import discord
from discord import app_commands
from discord.ext import commands
import economy  # Your existing economy system

class Explore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.pets_by_rarity = {
            "common": ["Zebulon Pup", "Rocky-3", "DustBoi", "Echo-Lite", "Pluto Jr"],
            "uncommon": ["Xandar-9", "Draconis", "Kepler Kitten", "Orbitron", "NovaNom"],
            "rare": ["Aurora Prime", "CrysTalos", "StarVine", "NebuPuff", "Vortex Vee"],
            "epic": ["Gliese-581c", "QuasiFluff", "DarkMatter Dragon", "Omega-77", "Spectra"],
        }

    def get_random_pet(self):
        chance = random.randint(1, 100)
        if chance <= 50:
            rarity = "common"
        elif chance <= 75:
            rarity = "uncommon"
        elif chance <= 90:
            rarity = "rare"
        else:
            rarity = "epic"
        pet = random.choice(self.pets_by_rarity[rarity])
        return pet, rarity

    @app_commands.command(name="explore", description="Explore a new part of space and find a space pet!")
    async def explore(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        await economy.ensure_user(user_id)

        pet, rarity = self.get_random_pet()
        stardust = random.randint(50, 100)
        await economy.add_balance(user_id, stardust)
        await economy.add_pet(user_id, pet, rarity)


        await interaction.response.send_message(
            f"🛰️ {interaction.user.mention} explored the stars and found a **{rarity}** space pet: **{pet}**!\n"
            f"You earned **{stardust} Stardust ✨**!"
        )

    @app_commands.command(name="deep_space", description="Explore far into deep space... high risk, high reward!")
    async def explore_far(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        await economy.ensure_user(user_id)

        if random.random() < 0.5:  # 50% death chance
            loss = random.randint(100, 200)
            current = await economy.get_balance(user_id)
            loss = min(loss, current)
            await economy.remove_balance(user_id, loss)
           
            await interaction.response.send_message(
                f"☠️ {interaction.user.mention} flew too far and got caught in a wormhole!\n"
                f"You lost **{loss} Stardust ⭐**. Better luck next time!"
            )
            return

        pet_count = random.randint(2, 3)
        pets_found = []
        for _ in range(pet_count):
            pet, rarity = self.get_random_pet()
            pets_found.append((pet, rarity))

        stardust = random.randint(200, 400)
        await economy.add_balance(user_id, stardust)
        for pet, rarity in pets_found:
          await economy.add_pet(user_id, pet, rarity)

        pet_list = "\n".join([f"• **{pet}** (*{rarity}*)" for pet, rarity in pets_found])
        

        await interaction.response.send_message(
            f"🚀 {interaction.user.mention} ventured FAR into the galaxy!\n"
            f"You found:\n{pet_list}\nAnd earned **{stardust} Stardust ✨**! Cosmic jackpot!"
        )

async def setup(bot):
    await bot.add_cog(Explore(bot))
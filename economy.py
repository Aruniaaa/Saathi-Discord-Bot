# economy.py
import aiosqlite

DB_NAME = "saathi_economy.db"


async def setup():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA journal_mode=WAL;")
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER DEFAULT 0
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_pets (
               user_id INTEGER,
               pet_name TEXT,
               rarity TEXT
    )
""")
        await db.execute("""
    CREATE TABLE IF NOT EXISTS user_titles (
        user_id INTEGER,
        title TEXT
    )
""")
        await db.execute("""
    CREATE TABLE IF NOT EXISTS user_food (
        user_id INTEGER,
        food_name TEXT
    )
""")
        await db.execute("""
    CREATE TABLE IF NOT EXISTS user_lootboxes (
        user_id INTEGER,
        box_type TEXT
    )
""")
        await db.execute("""
    CREATE TABLE IF NOT EXISTS user_items (
        user_id INTEGER,
        item_name TEXT
    )
""")
        await db.execute("""
    CREATE TABLE IF NOT EXISTS user_pets (
        user_id INTEGER,
        pet_name TEXT,
        rarity TEXT,
        equipped INTEGER DEFAULT 0
    )
""")

        await db.execute("""
    CREATE TABLE IF NOT EXISTS user_titles (
        user_id INTEGER,
        title TEXT,
        equipped INTEGER DEFAULT 0
    )
""")
   



        await db.commit()


async def add_pet(user_id: int, pet_name: str, rarity: str):
    await ensure_user(user_id)
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO user_pets (user_id, pet_name, rarity) VALUES (?, ?, ?)
        """, (user_id, pet_name, rarity))
        await db.commit()


async def get_user_pets(user_id: int) -> list[tuple[str, str]]:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("""
            SELECT pet_name, rarity FROM user_pets WHERE user_id = ?
        """, (user_id,)) as cursor:
            return await cursor.fetchall()




async def ensure_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, 0)
        """, (user_id,))
        await db.commit()


async def get_balance(user_id: int) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0


async def add_balance(user_id: int, amount: int):
    await ensure_user(user_id)
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE users SET balance = balance + ? WHERE user_id = ?
        """, (amount, user_id))
        await db.commit()


async def remove_balance(user_id: int, amount: int):
    await ensure_user(user_id)
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE users SET balance = balance - ? WHERE user_id = ?
        """, (amount, user_id))
        await db.commit()

async def transfer_balance(from_id: int, to_id: int, amount: int) -> bool:
    if amount <= 0:
        return False
    await ensure_user(from_id)
    await ensure_user(to_id)
    if await get_balance(from_id) < amount:
        return False
    await remove_balance(from_id, amount)
    await add_balance(to_id, amount)
    return True

async def add_title(user_id: int, title: str):
    await ensure_user(user_id)
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO user_titles (user_id, title) VALUES (?, ?)", (user_id, title))
        await db.commit()



async def add_food(user_id: int, food_name: str):
    await ensure_user(user_id)
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO user_food (user_id, food_name) VALUES (?, ?)", (user_id, food_name))
        await db.commit()

async def give_lootbox(user_id: int, box_type: str):
    await ensure_user(user_id)
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO user_lootboxes (user_id, box_type) VALUES (?, ?)", (user_id, box_type))
        await db.commit()


async def add_item(user_id: int, item_name: str):
    await ensure_user(user_id)
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO user_items (user_id, item_name) VALUES (?, ?)", (user_id, item_name))
        await db.commit()

async def equip_pet(user_id: int, pet_name: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE user_pets SET equipped = 0 WHERE user_id = ?", (user_id,))
        await db.execute("UPDATE user_pets SET equipped = 1 WHERE user_id = ? AND pet_name = ?", (user_id, pet_name))
        await db.commit()

async def equip_title(user_id: int, title: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE user_titles SET equipped = 0 WHERE user_id = ?", (user_id,))
        await db.execute("UPDATE user_titles SET equipped = 1 WHERE user_id = ? AND title = ?", (user_id, title))
        await db.commit()


async def remove_food(user_id: int, food_name: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            DELETE FROM user_food 
            WHERE rowid = (
                SELECT rowid FROM user_food 
                WHERE user_id = ? AND food_name = ? 
                LIMIT 1
            )
        """, (user_id, food_name))
        await db.commit()




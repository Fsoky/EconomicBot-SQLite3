import aiosqlite


class DataBase:

    def __init__(self):
        self.db_name = "test-database.db"

    async def get_data(self, member, *, all_data: bool=False, filters: str=None):
        async with aiosqlite.connect(self.db_name) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.cursor()

            result = None
            if all_data:
                # :member: - like guild id
                await cursor.execute(f"SELECT * FROM users WHERE guild_id = ? {filters}", [member])
                result = await cursor.fetchall()
            else:
                await cursor.execute("SELECT * FROM users WHERE member_id = ? AND guild_id = ?", [member.id, member.guild.id])
                result = await cursor.fetchone()

            return result

    async def create_table(self):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.cursor()

            query = """
            CREATE TABLE IF NOT EXISTS users(
                member_id INTEGER,
                guild_id INTEGER,
                balance BIGINT NOT NULL DEFAULT 300,
                reputation INTEGER NOT NULL DEFAULT 0,
                xp INTEGER NOT NULL DEFAULT 0,
                level INTEGER NOT NULL DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS shop(
                role_id INTEGER,
                guild_id INTEGER,
                cost BIGINT
            )
            """
            await cursor.executescript(query)
            await db.commit()

    async def insert_new_member(self, member):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.cursor()

            await cursor.execute("SELECT * FROM users WHERE member_id = ? AND guild_id = ?", [member.id, member.guild.id])
            if await cursor.fetchone() is None:
                await cursor.execute("INSERT INTO users(member_id, guild_id) VALUES(?, ?)", [member.id, member.guild.id])

            await db.commit()

    async def update_member(self, query, values: list):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.cursor()

            await cursor.execute(query, values)
            await db.commit()

    """Methods for shop"""

    async def insert_new_role(self, role, cost):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.cursor()

            await cursor.execute("INSERT INTO shop VALUES(?, ?, ?)", [role.id, role.guild.id, cost])
            await db.commit()

    async def delete_role_from_shop(self, role):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.cursor()

            await cursor.execute("DELETE FROM shop WHERE role_id = ? AND guild_id = ?", [role.id, role.guild.id])
            await db.commit()

    async def get_shop_data(self, role, *, all_data: bool=False):
        async with aiosqlite.connect(self.db_name) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.cursor()

            result = None
            if all_data:
                # :role: - like guild id
                await cursor.execute("SELECT * FROM shop WHERE guild_id = ?", [role])
                result = await cursor.fetchall()
            else:
                await cursor.execute("SELECT * FROM shop WHERE role_id = ? AND guild_id = ?", [role.id, role.guild.id])
                result = await cursor.fetchone()

            return result

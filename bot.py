""" Премечание
В случае неисправностей отписать в группу ВК
https://vk.com/fsoky

"""

import sqlite3

import disnake # pip install disnake
from disnake.ext import commands

bot = commands.Bot(command_prefix=".", intents=disnake.Intents.all())
db = sqlite3.connect("server.db")
cursor = db.cursor()


@bot.event
async def on_ready():
	cursor.execute("""CREATE TABLE IF NOT EXISTS users (
		id INT,
		guild_id INT,
		cash BIGINT,
		rep INT,
		lvl INT
	)""")

	cursor.execute("""CREATE TABLE IF NOT EXISTS shop (
		role_id INT,
		guild_id INT,
		cost BIGINT
	)""")

	for guild in bot.guilds:
		for member in guild.members:
			if cursor.execute("SELECT id FROM users WHERE id = ? AND guild_id = ?", (member.id, guild.id,)).fetchone() is None:
				cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (member.id, guild.id, 300, 0, 1,))

	db.commit()
	print("BOT CONNECTED")


@bot.event
async def on_member_join(member):
	if cursor.execute("SELECT id FROM users WHERE id = ? AND guild_id = ?", (member.id, member.guild.id,)).fetchone() is None:
		cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (member.id, guild.id, 300, 0, 1,))

	db.commit()


@bot.event
async def on_guild_join(guild):
	for member in guild.members:
		if cursor.execute("SELECT id FROM users WHERE id = ? AND guild_id = ?", (member.id, member.guild.id,)).fetchone() is None:
			cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (member.id, member.guild.id, 300, 0, 1,))

	db.commit()


@bot.command(aliases=["деньги", "cash"])
async def balance(ctx, member: disnake.Member=None):
	user_balance = cursor.execute("SELECT cash FROM users WHERE id = ? AND guild_id = ?", (ctx.author.id, ctx.guild.id,)).fetchone()[0]

	if member is not None:
		user_balance = cursor.execute("SELECT cash FROM users WHERE id = ? AND guild_id = ?", (member.id, ctx.guild.id,)).fetchone()[0]
		await ctx.send(embed=disnake.Embed(
			description=f"Баланс пользователя: **{ctx.author}** | {user_balance}"
		))

	await ctx.send(embed=disnake.Embed(
		description=f"Баланс пользователя: **{ctx.author}** | {user_balance}"
	))


@bot.command(name="наградить")
async def award(ctx, member: disnake.Member, amount: int):
	if amount < 1:
		await ctx.send("Сумма не должна быть меньше 1")
	else:
		cursor.execute("UPDATE users SET cash = cash + ? WHERE id = ? AND guild_id = ?", (amount, member.id, ctx.guild.id,))
		db.commit()

		await ctx.message.add_reaction('✅')


@bot.command(name="забрать")
async def take(ctx, member: disnake.Member, amount):
	if amount == "all":
		cursor.execute("UPDATE users SET cash = ? WHERE id = ? AND guild_id = ?", (0, member.id, ctx.guild.id,))
	elif int(amount) < 1:
		await ctx.send("Сумма не должна быть меньше 1")
	elif not amount.is_digit():
		await ctx.send("Должна быть сумма или all")
	else:
		cursor.execute("UPDATE users SET cash = cash + ? WHERE id = ? AND guild_id = ?", (amount, member.id, ctx.guild.id,))
	
	db.commit()
	await ctx.message.add_reaction('✅')


@bot.command(name="добавить-роль")
async def add_shop(ctx, role: disnake.Role, cost: int):
	if cost < 0:
		await ctx.send("Сумма не должна быть меньше 0")
	else:
		cursor.execute("INSERT INTO shop VALUES (?, ?, ?)", (role.id, ctx.guild.id, cost,))
		db.commit()

		await ctx.message.add_reaction('✅')


@bot.command(name="удалить-товар")
async def remove_shop(ctx, role: disnake.Role):
	if ctx.guild.get_role(role.id) is None:
		await ctx.send("Данной роли не существует")
	else:
		cursor.execute("DELETE FROM shop WHERE role_id = ? AND guild_id = ?", (role.id, ctx.guild.id,))
		db.commit()

		await ctx.message.add_reaction('✅')


@bot.command(name="магазин")
async def shop(ctx):
	embed = disnake.Embed(title="Магазин ролей")
	for row in cursor.execute("SELECT role_id, cost FROM shop WHERE guild_id = ?", (ctx.guild.id,)):
		if ctx.guild.get_role(row[0]) != None:
			embed.add_field(
				name=f"Стоимость **{row[1]}**",
				value=f"Роль: {ctx.guild.get_role(row[0]).mention}",
				inline=False
			)

	await ctx.send(embed=embed)


@bot.command(name="купить")
async def buy(ctx, role: disnake.Role):
	if role in ctx.author.roles:
		await ctx.send(f"**{ctx.author}**, у вас уже имеется данная роль")
	elif cursor.execute("SELECT cost FROM shop WHERE role_id = ? AND guild_id = ?", (role.id, ctx.guild.id,)).fetchone()[0] > \
		cursor.execute("SELECT cash FROM users WHERE id = ? AND guild_id = ?", (ctx.author.id, ctx.guild.id)).fetchone()[0]:
		await ctx.send(f"**{ctx.author}**, у вас недостаточно средств для покупки данной роли")
	else:
		await ctx.author.add_roles(role)

		cost = cursor.execute("SELECT cost FROM shop WHERE role_id = ? AND guild_id = ?", (role.id, ctx.guild.id,)).fetchone()[0]
		cursor.execute("UPDATE users SET cash = cash - ? WHERE id = ? AND guild_id = ?", (cost, ctx.author.id, ctx.guild.id,))
		db.commit()

		await ctx.message.add_reaction('✅')


@bot.command(name="+rep")
async def rep(ctx, member: disnake.Member):
	if member.id == ctx.author.id:
		await ctx.send(f"**{ctx.author}**, вы не можете указать смого себя")
	else:
		cursor.execute("UPDATE users SET rep = rep + ? WHERE id = ? AND guild_id = ?", (1, member.id, ctx.guild.id,))
		db.commit()

		await ctx.message.add_reaction('✅')


@bot.command(name="лидеры")
async def leaderboard(ctx):
	embed = disnake.Embed(title="Топ 10 сервера")
	counter = 0

	for row in cursor.execute("SELECT id, cash FROM users WHERE guild_id = ? ORDER BY cash DESC LIMIT 10", (ctx.guild.id,)):
		counter += 1
		embed.add_field(
			name=f"# {counter} | `{bot.get_user(row[0])}`",
			value=f"Баланс: {row[1]}",
			inline=False
		)

	await ctx.send(embed=embed)


bot.run("YOUR TOKEN")

import disnake
from disnake.ext import commands

from utils import database


class Events(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.db = database.DataBase()

	@commands.Cog.listener()
	async def on_ready(self):
		await self.db.create_table()

		for guild in self.bot.guilds:
			for member in guild.members:
				await self.db.insert_new_member(member)

	@commands.Cog.listener()
	async def on_member_join(self, member):
		await self.db.insert_new_member(member)

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author == self.bot.user:
			return

		data = await self.db.get_data(message.author)
		if data["xp"] == 500+100 * data["level"]:
			await self.db.update_member("UPDATE users SET level = level + ? AND xp = ? WHERE member_id = ? AND guild_id = ?",
				[1, 0, message.author.id, message.guild.id]
			)
			await message.channel.send(f"{message.author.mention} +1 LVL")
		else:
			await self.db.update_member("UPDATE users SET xp = xp + ? WHERE member_id = ? AND guild_id = ?",
				[50, message.author.id, message.guild.id]
			)

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		print(error)

		if isinstance(error, commands.UserInputError):
			await ctx.send(embed=disnake.Embed(
				description=f"Правильное использование команды: `{ctx.prefix}{ctx.command.name}` ({ctx.command.brief}): `{ctx.prefix}{ctx.command.usage}`"
			))


def setup(bot):
	bot.add_cog(Events(bot))

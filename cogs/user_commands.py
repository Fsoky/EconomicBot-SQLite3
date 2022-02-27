import disnake
from disnake.ext import commands

from utils import database


class UserCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db = database.DataBase()

    @commands.command(
        name="баланс",
        aliases=["cash", "balance", "деньги"],
        brief="Баланс пользователя",
        usage="balance <@user=None>"
    )
    async def user_balance(self, ctx, member: disnake.Member=None):
        balance = await self.db.get_data(ctx.author)
        embed = disnake.Embed(description=f"Баланс *{ctx.author}*: {balance['balance']}")

        if member is not None:
            balance = await self.db.get_data(member)
            embed.description = f"Баланс *{member}*: {balance['balance']}"
        await ctx.send(embed=embed)

    @commands.command(
        name="наградить",
        aliases=["award"],
        brief="Наградить пользователя суммой денег",
        usage="award <@user> <amount>"
    )
    async def award_user(self, ctx, member: disnake.Member, amount: int):
        if amount < 1:
            await ctx.send("Сумма не должна быть меньше 1")
        else:
            await self.db.update_member("UPDATE users SET balance = balance + ? WHERE member_id = ? AND guild_id = ?", [amount, member.id, ctx.guild.id])
            await ctx.message.add_reaction("💖")

    @commands.command(
        name="забрать",
        aliases=["take", "отнять"],
        brief="Забрать сумму денег у пользователя",
        usage="take <@user> <amount (int or all)>"
    )
    async def take_cash(self, ctx, member: disnake.Member, amount):
        if amount == "all":
            await self.db.update_member("UPDATE users SET balance = ? WHERE member_id = ? AND guild_id = ?", [0, member.id, ctx.guild.id])
        elif int(amount) < 1:
            await ctx.send("Сумма не должна быть меньше 1")
        else:
            await self.db.update_member("UPDATE users SET balance = balance - ? WHERE member_id = ? AND guild_id = ?", [amount, member.id, ctx.guild.id])

        await ctx.message.add_reaction("💖")

    @commands.command(
        name="перевести",
        aliases=["pay", "transfer", "перевод"],
        brief="Перевести деньги пользователю",
        usage="pay <@user> <amount>"
    )
    async def pay_cash(self, ctx, member: disnake.Member, amount: int):
        balance = await self.db.get_data(member)

        if amount > balance["balance"]:
            await ctx.send("Недостаточно средств")
        elif amount <= 0:
            await ctx.send("Сумма не должна быть меньше 1")
        else:
            await self.db.update_member("UPDATE users SET balance = balance - ? WHERE member_id = ? AND guild_id = ?", [amount, ctx.author.id, ctx.guild.id])
            await self.db.update_member("UPDATE users SET balance = balance + ? WHERE member_id = ? AND guild_id = ?",  [amount, member.id, ctx.guild.id])

        await ctx.message.add_reaction("💖")

    @commands.command(
        name="+репутация",
        aliases=["rep", "+rep", "реп", "репутация"],
        brief="Респект пользователю",
        usage="rep <@user>"
    )
    async def reputation(self, ctx, member: disnake.Member):
        if member.id == ctx.author.id:
            await ctx.send("Нельзя выдать репутацию себе")
        else:
            await self.db.update_member("UPDATE users SET reputation = reputation + ? WHERE member_id = ? AND guild_id = ?", [1, member.id, ctx.guild.id])
            await ctx.message.add_reaction("💖")

    @commands.command(
        name="лидеры",
        aliases=["leaders", "leadersboard", "лидер", "top"],
        brief="Таблица лидеров"
    )
    async def server_leadersboard(self, ctx):
        embed = disnake.Embed(title="Топ 10 сервера")
        counter = 0

        data = await self.db.get_data(ctx.guild.id, all_data=True, filters="ORDER BY balance DESC LIMIT 10")
        for row in data:
            counter += 1
            embed.add_field(
                name=f"#{counter} | `{self.bot.get_user(row['member_id'])}`",
                value=f"Баланс: {row['balance']}",
                inline=False
            )

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(UserCommands(bot))

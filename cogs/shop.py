import disnake
from disnake.ext import commands

from utils import database


class Shop(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db = database.DataBase()

    @commands.command(
        name="добавить-роль",
        aliases=["add", "add-shop", "добавить"],
        brief="Добавить новую роль в магазин",
        usage="add <@role> <cost>"
    )
    async def add_role_to_shop(self, ctx, role: disnake.Role, cost: int=0):
        if cost < 0:
            await ctx.send("Сумма не должна быть меньше 0")
        else:
            await self.db.insert_new_role(role, cost)
            await ctx.message.add_reaction("💖")

    @commands.command(
        name="удалить-роль",
        aliases=["remove", "rm-role", "remove-role", "удалить"],
        brief="Удалить роль из магазина",
        usage="remove <@role>"
    )
    async def remove_role(self, ctx, role: disnake.Role):
        if ctx.guild.get_role(role.id) is None:
            await ctx.send("Роли не существует")
        else:
            await self.db.delete_role_from_shop(role)
            await ctx.message.add_reaction("💖")

    @commands.command(
        name="купить-роль",
        aliases=["buy", "buy-role", "купить"],
        brief="Купить роль",
        usage="buy <@role>"
    )
    async def buy_role(self, ctx, role: disnake.Role):
        if ctx.guild.get_role(role.id) is None:
            await ctx.send("Роли не существует")
        elif role in ctx.author.roles:
            await ctx.send("У вас уже имеется такая роль")
        else:
            role_data = await self.db.get_shop_data(role)
            balance = await self.db.get_data(ctx.author)

            if balance["balance"] < role_data["cost"]:
                await ctx.send("Недостаточно средств")
            elif balance["balance"] <= 0:
                await ctx.send("Недостаточно средств")
            else:
                await self.db.update_member("UPDATE users SET balance = balance - ? WHERE member_id = ? AND guild_id = ?", [role_data["cost"], ctx.author.id, ctx.guild.id])

                await ctx.author.add_roles(role)
                await ctx.message.add_reaction("💖")

    @commands.command(
        name="магазин-ролей",
        aliases=["shop", "roles-shop", "магазин"],
        brief="Магазин ролей"
    )
    async def view_shop(self, ctx):
        embed = disnake.Embed(title="Магазин ролей")

        data = await self.db.get_shop_data(ctx.guild.id, all_data=True)
        for row in data:
            if ctx.guild.get_role(row["role_id"]) is not None:
                embed.add_field(
                    name=f"Стоимость: {row['cost']}",
                    value=f"Роль: {ctx.guild.get_role(row['role_id']).mention}",
                    inline=False
                )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Shop(bot))

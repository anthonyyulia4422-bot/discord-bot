import discord
from discord import app_commands
from discord.ext import commands


class ModerationCog(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="clear", description="批量刪除指定數量的訊息")
  @app_commands.checks.has_permissions(manage_messages=True)
  async def clear(self, interaction: discord.Interaction, count: int):
    if count <= 0:
      await interaction.response.send_message(
          "請輸入大於 0 的數字！", ephemeral=True
      )
      return
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=count)
    await interaction.followup.send(
        f"成功刪除了 {len(deleted)} 則訊息！", ephemeral=True
    )


async def setup(bot):
  await bot.add_cog(ModerationCog(bot))

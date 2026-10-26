import discord
from discord.ext import commands


class CivilFilterCog(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_message(self, message: discord.Message):
    if message.author.bot or not message.guild:
      return
    if message.content.startswith(("!", "/")) or not message.content.strip():
      return

    content = message.content

    # 雙重觸發條件：同時包含「ㄐㄧ」與「ㄅㄚ」系注音
    has_ji = "ㄐㄧ" in content
    has_ba = "ㄅㄚ" in content

    if not (has_ji and has_ba):
      return

    try:
      await message.reply("說祭不說吧，文明你我他", mention_author=True)
    except Exception as e:
      print(f"❌ 文明淨化模組發生錯誤: {e}")


async def setup(bot):
  await bot.add_cog(CivilFilterCog(bot))

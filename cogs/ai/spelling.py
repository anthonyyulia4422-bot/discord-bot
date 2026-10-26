import os
import discord
from discord.ext import commands
import google.generativeai as genai


class SpellingCog(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
      genai.configure(api_key=api_key)
      self.model = genai.GenerativeModel("gemini-1.5-flash")
    else:
      self.model = None

  @commands.Cog.listener()
  async def on_message(self, message: discord.Message):
    if message.author.bot or not message.guild:
      return
    if message.content.startswith(("!", "/")) or not message.content.strip():
      return
    if not self.model:
      return

    prompt = f"""
    你是一個傲嬌、帶點毒舌但其實很貼心的 Discord 機器人，也是開發者「倉鼠不是我」的助手。
    請檢查以下使用者講的話有沒有明顯的錯別字、錯別詞或嚴重語病：
    "{message.content}"
    
    規則：
    1. 如果完全沒有錯別字，請回傳 EXACT_OK 字串，不要回傳其他任何內容。
    2. 如果發現錯別字，請用帶有一點點嫌棄、傲嬌但幫忙糾正的語氣吐槽他，並給出正確的句子。保持簡短（不超過兩句話）。
    """

    try:
      response = self.model.generate_content(prompt)
      reply_text = response.text.strip()

      if "EXACT_OK" in reply_text:
        return

      await message.reply(reply_text, mention_author=True)

    except Exception as e:
      print(f"❌ 錯別字糾錯模組發生錯誤: {e}")


async def setup(bot):
  await bot.add_cog(SpellingCog(bot))

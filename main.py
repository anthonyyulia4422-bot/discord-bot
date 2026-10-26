import asyncio
import os
from threading import Thread
import discord
from discord.ext import commands
from flask import Flask
import google.generativeai as genai

# -----------------------------------------
# Flask 網頁伺服器 (讓 Render 進行 Health Check)
# -----------------------------------------
app = Flask("")


@app.route("/")
def home():
  return "Yukishita Orika Bot is running smoothly!"


# -----------------------------------------
# Discord Bot 初始化
# -----------------------------------------
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
  genai.configure(api_key=GEMINI_API_KEY)
  model = genai.GenerativeModel("gemini-1.5-flash")
else:
  model = None

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


# 🌟 自動遞迴掃描 cogs 底下的所有子資料夾與檔案 (加上 flush=True 強制即時印出 Logs)
async def load_extensions():
  for root, dirs, files in os.walk("./cogs"):
    for filename in files:
      if filename.endswith(".py"):
        if filename == "__init__.py":
          continue
        rel_path = os.path.relpath(os.path.join(root, filename), ".")
        module_name = rel_path[:-3].replace(os.sep, ".")
        try:
          await bot.load_extension(module_name)
          print(f"✅ 已載入模組: {module_name}", flush=True)
        except Exception as e:
          print(f"❌ 載入模組 {module_name} 失敗: {e}", flush=True)


@bot.event
async def on_ready():
  print(f"🤖 機器人已登入為 {bot.user}", flush=True)
  try:
    synced = await bot.tree.sync()
    print(f"🌐 同步了 {len(synced)} 個 Slash 指令", flush=True)
  except Exception as e:
    print(f"❌ 同步 Slash 指令失敗: {e}", flush=True)


# 🛡️ 統一在這裡接收所有被 @ 的對話
@bot.event
async def on_message(message):
  if message.author.bot:
    return

  # 判斷是否 @ 機器人
  if bot.user in message.mentions:
    user_input = (
        message.content.replace(f"<@{bot.user.id}>", "")
        .replace(f"<@!{bot.user.id}>", "")
        .strip()
    )

    if not user_input:
      await message.channel.send(
          f"嗨 {message.author.mention}！我是開發者「倉鼠不是我」的助手，有什麼要事談談呢～"
      )
      return

    if model:
      try:
        async with message.channel.typing():
          prompt = f"你現在是開發者「倉鼠不是我」的傲嬌助手，帶點毒舌。回覆與使用者 ({message.author.display_name}) 的對話風格：充滿傲嬌強硬、口吻毒舌、多用表情符號 (-)\n使用者對話內容：{user_input}"

          response = await asyncio.to_thread(model.generate_content, prompt)
          reply_text = (
              response.text.strip()
              if response and response.text
              else "哼，本小姐才懶得理你了呢～"
          )
          await message.reply(reply_text, mention_author=True)
      except Exception as e:
        print(f"❌ AI 回覆發生錯誤: {e}", flush=True)
        await message.reply(
            f"呼‧才‧才不是本小姐網路卡住（錯誤：{e}）-", mention_author=False
        )
    else:
      await message.reply(
          "AI 核心目前尚未啟用或是 GEMINI_API_KEY 未設定！",
          mention_author=False,
      )

  await bot.process_commands(message)


async def main():
  async with bot:
    await load_extensions()
    await bot.start(DISCORD_TOKEN)


def run_discord():
  try:
    print("🚀 [背景執行緒] 正在啟動 Discord 機器人核心...", flush=True)
    asyncio.run(main())
  except Exception as e:
    print(f"❌ [Discord 執行緒發生嚴重錯誤]: {e}", flush=True)


if DISCORD_TOKEN:
  Thread(target=run_discord, daemon=True).start()
else:
  print("❌ [嚴重錯誤] 找不到 DISCORD_TOKEN 環境變數！請檢查 Render 設定。", flush=True)

if __name__ == "__main__":
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)

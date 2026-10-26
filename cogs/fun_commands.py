import random
import discord
from discord import app_commands
from discord.ext import commands


class FunCommands(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="fortune", description="抽取你今天的專屬運勢！")
  async def fortune(self, interaction: discord.Interaction):
    fortunes = [
        "大吉 🌟",
        "中吉 ✨",
        "小吉 🍀",
        "吉 😊",
        "平 🍃",
        "凶 💧",
        "大凶 💥 (天啊！今天出門小心...)",
    ]
    result = random.choice(fortunes)
    await interaction.response.send_message(
        f"🔮 **{interaction.user.display_name}** 今天的運勢是：**{result}**"
    )

  @app_commands.command(
      name="help", description="顯示機器人的所有功能與指令指南！"
  )
  async def help_command(self, interaction: discord.Interaction):
    embed = discord.Embed(
        title="❄️ 倉鼠不是我副手 - 伺服器指令與功能指南",
        description=(
            "本機器人是伺服器的專屬小幫手！\n"
            "以下是所有可用的 Slash 指令與自動互動功能介紹："
        ),
        color=0x87CEEB,
    )
    embed.add_field(
        name="📌 Slash 互動指令",
        value=(
            "• `/help` - 顯示本說明選單\n"
            "• `/fortune` - 抽取你今天的專屬運勢\n"
            "• `/rps` - 向其他人發起 PvP 剪刀石頭布（輸家將被禁言 1 分鐘）\n"
            "• `/roast` - 指定一人進行雌小鬼毒舌處刑\n"
            "• `/random_roast` - 隨機抽獎，處刑頻道裡的倒霉鬼\n"
            "• `/favor` - 查詢隱藏好感度狀態\n"
            "• `/poll` - 建立自訂選項投票箱\n"
            "• `/clear` - 批量刪除訊息（需管理員權限）"
        ),
        inline=False,
    )
    embed.add_field(
        name="⚡ 自動觸發與聊天互動",
        value=(
            "• **@機器人**：純 `@` 打招呼；`@` + 文字可與 AI 進行智慧聊天。\n"
            "• **AI 智慧強奪接龍**：由旗艦 AI 嚴格識別語境進行一問一答接龍。\n"
        ),
        inline=False,
    )
    embed.set_footer(text="—— 雑魚❤️~ 趕快去伺服器裡試試看吧！")
    await interaction.response.send_message(embed=embed)

  @app_commands.command(
      name="favor", description="查看你和助手的目前好感度！"
  )
  async def favor(self, interaction: discord.Interaction):
    # 已移除 ephemeral=True，現在全頻道都看得到這則訊息！
    await interaction.response.send_message(
        "💖 想知道好感度多少？做夢去吧，雜魚~❤️"
        " 這種高度機密本小姐才不會告訴你呢！"
    )

  @app_commands.command(
      name="poll", description="發起一個可自訂選項的投票（支援 2~5 個選項）"
  )
  async def poll(
      self,
      interaction: discord.Interaction,
      question: str,
      opt1: str,
      opt2: str,
      opt3: str = None,
      opt4: str = None,
      opt5: str = None,
  ):
    options = [opt1, opt2]
    if opt3:
      options.append(opt3)
    if opt4:
      options.append(opt4)
    if opt5:
      options.append(opt5)

    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
    description = f"**問題：** {question}\n\n"
    for i, opt in enumerate(options):
      description += f"{emojis[i]} {opt}\n"

    embed = discord.Embed(
        title="📊 伺服器自訂投票箱", description=description, color=0x3498db
    )
    embed.set_footer(text=f"發起人：{interaction.user.display_name}")
    await interaction.response.send_message(embed=embed)
    message = await interaction.original_response()
    for i in range(len(options)):
      await message.add_reaction(emojis[i])


async def setup(bot):
  await bot.add_cog(FunCommands(bot))


import datetime
import discord
from discord import app_commands
from discord.ext import commands


class PvPRPSView(discord.ui.View):

  def __init__(self, challenger: discord.Member, opponent: discord.Member):
    super().__init__(timeout=60)
    self.challenger = challenger
    self.opponent = opponent
    self.choices = {}
    self.timeout_cooldowns = {}

  async def handle_choice(
      self, interaction: discord.Interaction, player_choice: str
  ):
    user_id = interaction.user.id
    if user_id not in [self.challenger.id, self.opponent.id]:
      await interaction.response.send_message(
          "這不是你的生死對決！請自己發起 `/rps` 指令。",
          ephemeral=True,
      )
      return
    if user_id in self.choices:
      await interaction.response.send_message(
          "你已經出過拳囉！請等待對手選擇。", ephemeral=True
      )
      return

    self.choices[user_id] = player_choice
    await interaction.response.send_message(
        f"你已選擇出 **{player_choice}**！等待對手選擇中...",
        ephemeral=True,
    )

    if len(self.choices) == 2:
      await self.resolve_game(interaction)

  async def resolve_game(self, interaction: discord.Interaction):
    for child in self.children:
      child.disabled = True

    c_choice = self.choices[self.challenger.id]
    o_choice = self.choices[self.opponent.id]

    outcomes = {
        ("剪刀 ✂️", "剪刀 ✂️"): 0,
        ("剪刀 ✂️", "石頭 🪨"): -1,
        ("剪刀 ✂️", "布 📄"): 1,
        ("石頭 🪨", "剪刀 ✂️"): 1,
        ("石頭 🪨", "石頭 🪨"): 0,
        ("石頭 🪨", "布 📄"): -1,
        ("布 📄", "剪刀 ✂️"): -1,
        ("布 📄", "石頭 🪨"): 1,
        ("布 📄", "布 📄"): 0,
    }

    res = outcomes[(c_choice, o_choice)]
    msg = (
        f"⚔️ **PvP 生死對決結果公佈！**\n\n"
        f"👤 {self.challenger.mention} 出了 **{c_choice}**\n"
        f"👤 {self.opponent.mention} 出了 **{o_choice}**\n\n"
    )

    loser = None
    if res == 0:
      msg += "🤝 **平手！** 雙方勢均力敵，免受懲罰！"
    elif res == 1:
      msg += f"🎉 {self.challenger.mention} **獲勝！**\n💀 {self.opponent.mention} 敗北！"
      loser = self.opponent
    else:
      msg += f"🎉 {self.opponent.mention} **獲勝！**\n💀 {self.challenger.mention} 敗北！"
      loser = self.challenger

    await interaction.channel.send(content=msg, view=self)

    if loser:
      now = datetime.datetime.now(datetime.timezone.utc)
      last_timeout = self.timeout_cooldowns.get(loser.id)
      can_timeout = True

      if last_timeout and (now - last_timeout).total_seconds() < 3600:
        can_timeout = False
        remaining_minutes = int(
            (3600 - (now - last_timeout).total_seconds()) // 60
        )
        await interaction.channel.send(
            f"🛡️ {loser.mention} *(免除禁言：一小時內已被禁言過，冷卻剩餘 {remaining_minutes} 分鐘)*"
        )

      if can_timeout:
        try:
          await loser.timeout(
              datetime.timedelta(minutes=1), reason="PvP 剪刀石頭布對決落敗"
          )
          self.timeout_cooldowns[loser.id] = now
          await interaction.channel.send(
              f"💀 {loser.mention} 已進入禁言 1 分鐘懲罰，**看告復活中...** ⏳"
          )
        except discord.Forbidden:
          await interaction.channel.send(
              "⚠️ 機器人權限不足（請確認身分組階級高於該成員，且具備「禁言成員」權限）！"
          )
        except Exception as e:
          await interaction.channel.send(f"❌ 執行禁言時發生錯誤：{e}")

  @discord.ui.button(
      label="剪刀 ✂️", style=discord.ButtonStyle.primary, custom_id="pvp_scissors"
  )
  async def scissors(self, interaction: discord.Interaction, button: discord.ui.Button):
    await self.handle_choice(interaction, "剪刀 ✂️")

  @discord.ui.button(
      label="石頭 🪨", style=discord.ButtonStyle.success, custom_id="pvp_rock"
  )
  async def rock(self, interaction: discord.Interaction, button: discord.ui.Button):
    await self.handle_choice(interaction, "石頭 🪨")

  @discord.ui.button(
      label="布 📄", style=discord.ButtonStyle.danger, custom_id="pvp_paper"
  )
  async def paper(self, interaction: discord.Interaction, button: discord.ui.Button):
    await self.handle_choice(interaction, "布 📄")


class RPSCog(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(
      name="rps", description="向伺服器其他玩家發起剪刀石頭布生死對決！"
  )
  async def rps(self, interaction: discord.Interaction, target: discord.Member):
    if target.id == interaction.user.id or target.bot:
      await interaction.response.send_message(
          "無法向自己或機器人發起對決！", ephemeral=True
      )
      return
    view = PvPRPSView(interaction.user, target)
    await interaction.response.send_message(
        f"⚔️ **{interaction.user.mention}** 向 **{target.mention}** 發起了 PvP"
        f" 剪刀石頭布生死對決！\n請兩位點擊按鈕秘密出拳（輸家將被**禁言 1"
        f" 分鐘**！）：",
        view=view,
    )


async def setup(bot):
  await bot.add_cog(RPSCog(bot))

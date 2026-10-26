import asyncio
import xml.etree.ElementTree as ET
import discord
from discord.ext import commands, tasks
import requests

CHANNEL_ID = 156357122987963668
YT_CHANNEL_ID = "UCH2dAEECzniZIShBZ50Iujg"


class YouTubeCog(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.last_stream_id = None
    self.is_initialized = False
    self.check_live_status.start()

  def cog_unload(self):
    self.check_live_status.cancel()

  def _fetch_rss(self):
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={YT_CHANNEL_ID}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=10)
    return response.status_code, response.content

  async def get_latest_video_from_rss(self):
    try:
      status_code, content = await asyncio.to_thread(self._fetch_rss)
      if status_code != 200:
        print(f"❌ YouTube RSS 回傳狀態碼異常: {status_code}")
        return None, None

      root = ET.fromstring(content)
      ns = {
          "atom": "http://www.w3.org/2005/Atom",
          "yt": "http://www.youtube.com/xml/schemas/2015",
      }

      entry = root.find("atom:entry", ns)
      if entry is not None:
        video_id_elem = entry.find("yt:videoId", ns)
        video_id = video_id_elem.text if video_id_elem is not None else None
        return video_id, entry
      return None, None
    except Exception as e:
      print(f"❌ 解析 RSS 發生錯誤: {e}")
      return None, None

  @tasks.loop(minutes=3)
  async def check_live_status(self):
    video_id, _ = await self.get_latest_video_from_rss()
    if not video_id:
      return

    if not self.is_initialized:
      self.last_stream_id = video_id
      self.is_initialized = True
      return

    if video_id != self.last_stream_id:
      self.last_stream_id = video_id
      channel = self.bot.get_channel(CHANNEL_ID)
      if channel:
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        await channel.send(f"@everyone 倉鼠的婆開播了，還不快去捧場\n{video_url}")

  @check_live_status.before_loop
  async def before_check_live_status(self):
    await self.bot.wait_until_ready()

  @commands.command(name="testyt")
  async def test_youtube(self, ctx: commands.Context):
    """測試 YouTube 直播狀態指令"""
    await ctx.send("🔍 正在為開發者「倉鼠不是我」檢查最新直播狀態...")
    video_id, _ = await self.get_latest_video_from_rss()

    if video_id:
      video_url = f"https://www.youtube.com/watch?v={video_id}"
      await ctx.send(f"@everyone 倉鼠的婆開播了，還不快去捧場\n{video_url}")
    else:
      # 🌟 加了這段：目前沒有直播時給予明確回應
      await ctx.send(
          "📢 報告！目前頻道沒有抓到最新動態或直播喔～"
      )


async def setup(bot):
  await bot.add_cog(YouTubeCog(bot))

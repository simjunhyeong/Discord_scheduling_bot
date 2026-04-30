from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import CHANNEL_ID
from db import load_db, reset_db, WEEK_ORDER
from schedule_img import create_schedule_image
import discord

scheduler = AsyncIOScheduler(timezone="Asia/Seoul")


def setup_scheduler(bot):
    scheduler.configure(event_loop=bot.loop)

    scheduler.add_job(
        start_schedule,
        "cron",
        day_of_week="wed",
        hour=1,
        minute=0,
        args=[bot]
    )

    scheduler.add_job(
        end_schedule,
        "cron",
        day_of_week="wed",
        hour=9,
        minute=0,
        args=[bot]
    )

    scheduler.start()


async def start_schedule(bot):
    channel = bot.get_channel(CHANNEL_ID) or await bot.fetch_channel(CHANNEL_ID)

    reset_db()

    await channel.send("📢 **스케줄 입력 시작! (오늘 18시까지)**")


async def end_schedule(bot):
    channel = bot.get_channel(CHANNEL_ID) or await bot.fetch_channel(CHANNEL_ID)

    db = load_db()

    # =========================
    # 🔥 여기서 "통계 직접 계산"
    # =========================
    day_count = {}

    for day in WEEK_ORDER:
        count = 0
        for schedule in db.values():
            value = schedule.get(day)
            if value and value not in ["❌", "x", "=="]:
                count += 1
        day_count[day] = count

    # =========================
    # 이미지 생성
    # =========================
    path = create_schedule_image(db, channel.guild)
    file = discord.File(path, filename="schedule.png")

    # =========================
    # 메시지 생성 (여기서 완결)
    # =========================
    msg = "📢 **스케줄 마감 공지**\n\n"

    high = [f"{d}({c})" for d, c in day_count.items() if c >= 5]
    mid = [f"{d}({c})" for d, c in day_count.items() if c == 4]
    low = [f"{d}({c})" for d, c in day_count.items() if c <= 3]

    if high:
        msg += "🟢 5인 이상\n" + ", ".join(high) + "\n\n"
    if mid:
        msg += "🟡 4인\n" + ", ".join(mid) + "\n\n"
    if low:
        msg += "🔴 3인 이하\n" + ", ".join(low) + "\n\n"

    await channel.send(content=msg, file=file)
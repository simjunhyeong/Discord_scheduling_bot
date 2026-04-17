import json
import os
import discord
from datetime import datetime
from config import WEEK_ORDER
import re

FILE_PATH = "schedule_db.json"

def norm_time(value):
    if not value:
        return value

    value = value.strip()
    # x 데이터 보정
    if value.lower() == "x":
        return "❌"

    # 시간 데이터 보정
    if re.fullmatch(r"\d{1,2}", value):
        hour = int(value)
        if 0 <= hour <= 23:
            return f"{hour:02d}:00"

    # 10:3 → 10:03
    if re.fullmatch(r"\d{1,2}:\d{1,2}", value):
        h, m = value.split(":")
        h, m = int(h), int(m)
        if 0 <= h <= 23 and 0 <= m <= 59:
            return f"{h:02d}:{m:02d}"

    return value

def norm_data(data):
    if isinstance(data, dict):
        return {k: norm_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [norm_data(v) for v in data]
    elif isinstance(data, str):
        return norm_time(data)
    else:
        return data

def normalize_schedule(selected_days):
    return {
        day: selected_days.get(day, "❌")
        for day in WEEK_ORDER
    }
# 데이터 로드
def load_db():
    if not os.path.exists(FILE_PATH):
        return {}
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# 데이터 저장
def save_db(data):
    data = norm_data(data)

    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 스케줄 초기화
def reset_db():
    save_db({})



# 유저 스케줄 저장
def save_schedule(user_id, schedule: dict):
    db = load_db()
    db[str(user_id)] = schedule
    save_db(db)

# 유저 스케줄 불러오기
def get_schedule(user_id):
    db = load_db()
    return db.get(str(user_id), {})


def show_schedule(username: str, schedule: dict):
    lines = []
    for day in WEEK_ORDER:
        time = schedule.get(day, "❌")

        icon = "🟦" if time != "❌" else "⬜"
        lines.append(f"{icon} {day}  {time}")

    embed = discord.Embed(
        title=f"📅 {username}님의 스케줄",
        description="\n".join(lines),
        color=0x00ffcc
    )

    return embed


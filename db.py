import json
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

scheduler = AsyncIOScheduler(timezone="Asia/Seoul")


FILE_PATH = "schedule_db.json"

def normalize_schedule(selected_days):
    WEEK_ORDER = ["월", "화", "수", "목", "금", "토", "일"]

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
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 스케줄 초기화
def reset_json():
    with open("schedule_db.json", "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=4)

def set_schedule():
    # 매주 수요일 오전 10시
    scheduler.add_job(
        reset_json,
        trigger="cron",
        day_of_week="wed",
        hour=10,
        minute=0
    )

# 유저 스케줄 저장
def save_schedule(user_id, schedule: dict):
    db = load_db()
    db[str(user_id)] = schedule
    save_db(db)

# 유저 스케줄 불러오기
def get_schedule(user_id):
    db = load_db()
    return db.get(str(user_id), {})
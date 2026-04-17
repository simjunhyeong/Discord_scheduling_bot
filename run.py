from config import client,tree,my_token
from db import scheduler, set_schedule
import bot_command
started = False
print(my_token)
@client.event
async def on_ready():
    global started

    if not started:
        set_schedule()
        scheduler.start()
        started = True

    synced = await tree.sync()
    print(f"명령어 개수: {len(synced)}")
    print("봇 준비 완료")

if __name__ == "__main__":
    client.run(my_token)

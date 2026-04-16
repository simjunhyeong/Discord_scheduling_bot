from My_bot import WeekView,ac ,discord
from config import tree
from db import load_db
print("command 입력시작")

#--------- 단순 command--------#
@tree.command(name="이름", description="봇이 당신의 이름을 출력합니당")
async def name(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"{interaction.user.display_name}님이 저를 불렀어요!")

@tree.command(name="핑", description="우리 탁구치자!")
async def pingpong(interaction: discord.Interaction):
    await interaction.response.send_message("퐁🏓")

'''
@tree.command(name="스케줄", description="원하는 요일을 클릭하세요")
async def Scedule(interaction: discord.Interaction):
   await interaction.response.send_message(
        "요일을 선택하세요 (여러 개 가능) 👇",
        view=WeekView()
    )
'''
#--------- Scedule Command_Group-------------------#
Sch_group = ac.Group(
    name="스케줄",
    description="스케줄 기능"
)

@Sch_group.command(name="등록", description="원하는 요일을 입력해 스케줄을 등록하세요")
async def reservation(interaction: discord.Interaction):
    await interaction.response.send_message(
        "요일을 선택하세요 (여러 개 가능) 👇",
        view=WeekView()
    )

@Sch_group.command(name="확인", description="내 스케줄을 확인하세요")
async def Check(interaction: discord.Interaction):

    db = load_db()
    user_id = str(interaction.user.id)
    schedule = db.get(user_id)

    if not schedule:
        await interaction.response.send_message(
            f"{interaction.user.display_name}님의 등록된 스케줄이 없습니다."
        )
        return

    WEEK_ORDER = ["월", "화", "수", "목", "금", "토", "일"]
    lines = []
    for day in WEEK_ORDER:
        time = schedule.get(day)
        icon = "🟦" if time != "❌" else "⬜"
        lines.append(f"{icon} {day}  {time}")

    embed = discord.Embed(
        title=f"📅 {interaction.user.display_name}님의 스케줄",
        description="\n".join(lines),
        color=0x00ffcc
    )
    await interaction.response.send_message(embed=embed)

tree.add_command(Sch_group)
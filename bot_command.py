from My_bot import WeekView,FinishView, ScheduleView, ac ,Change_Modal, discord
from config import tree, client ,WEEK_ORDER
from db import load_db, save_db, show_schedule 
print("command 입력시작")

#--------- 단순 command--------#
@tree.command(name="이름", description="봇이 당신의 이름을 출력합니당")
async def name(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"{interaction.user.display_name}님이 저를 불렀어요!")

@tree.command(name="핑", description="우리 탁구치자!")
async def pingpong(interaction: discord.Interaction):
    await interaction.response.send_message("퐁🏓")

#--------- Scedule Command_Group-------------------#
Sch_group = ac.Group(name="스케줄",description="스케줄 기능")

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
            f"{interaction.user.display_name}님의 등록된 스케줄이 없습니다.")
        return
    embed =  show_schedule(interaction.user.display_name,schedule)
 
    await interaction.response.send_message(embed=embed)

@Sch_group.command(name="변경", description="변경할 요일 입력"
                " (ex 월 화 수)  요일 사이에 스페이스바 입력해주세요")
async def change(interaction: discord.Interaction, 요일: str):

    db = load_db()
    user_id = str(interaction.user.id)
    schedule = db.get(user_id, {})

    # "월 화 수" → ["월","화","수"]
    day_list = [d.strip() for d in 요일.split()]

    # 유효성 검사
    for d in day_list:
        if d not in WEEK_ORDER:
            await interaction.response.send_message(f"❌ {d} 잘못된 요일")
            return

    # 5개 제한 체크
    if len(day_list) > 5:
        await interaction.response.send_message("❌ 최대 5개까지 가능")
        return

    await interaction.response.send_modal(
       Change_Modal(schedule, day_list)
    )
 
@Sch_group.command(name="편성표", description="요일별 쌍장모 스케줄을 확인합니다.")
async def All_schedule(interaction: discord.Interaction):
    db = load_db()

    await interaction.response.send_message(
        content="원하는 요일을 선택하세요",
        view=ScheduleView()
    )

tree.add_command(Sch_group)
import discord 
from config import WEEK_ORDER
from discord import app_commands as ac
from db import show_schedule,save_schedule, load_db, save_db 
from db import normalize_schedule as ns
from schedule_img import create_schedule_image
def format_days(selected_days):
    return ", ".join([d for d in WEEK_ORDER if d in selected_days and d in WEEK_ORDER]) or "없음"
#-------------------- 내부 클래스 -----------------------------#

# =========================
# 🔹 요일 선택 View
# =========================
class WeekView(discord.ui.View):

    def __init__(self,selected_days=None):
        super().__init__(timeout=60)
        if selected_days == None: 
            self.selected_days = set()
        else:
            self.selected_days = selected_days

    async def update_display(self, interaction):
        text = f"현재 선택: {format_days(self.selected_days)}"

        await interaction.response.edit_message(
            content=text,
            view=self
        )

    async def toggle_day(self, interaction, day):
        if day in self.selected_days:
            self.selected_days.remove(day)
        else:
            self.selected_days.add(day)

        await self.update_display(interaction)

    # 요일 버튼
    @discord.ui.button(label="월", style=discord.ButtonStyle.primary)
    async def mon(self, interaction, button):
        await self.toggle_day(interaction, "월")

    @discord.ui.button(label="화", style=discord.ButtonStyle.primary)
    async def tue(self, interaction, button):
        await self.toggle_day(interaction, "화")

    @discord.ui.button(label="수", style=discord.ButtonStyle.primary)
    async def wed(self, interaction, button):
        await self.toggle_day(interaction, "수")

    @discord.ui.button(label="목", style=discord.ButtonStyle.primary)
    async def thu(self, interaction, button):
        await self.toggle_day(interaction, "목")

    @discord.ui.button(label="금", style=discord.ButtonStyle.primary)
    async def fri(self, interaction, button):
        await self.toggle_day(interaction, "금")

    @discord.ui.button(label="토", style=discord.ButtonStyle.success)
    async def sat(self, interaction, button):
        await self.toggle_day(interaction, "토")

    @discord.ui.button(label="일", style=discord.ButtonStyle.danger)
    async def sun(self, interaction, button):
        await self.toggle_day(interaction, "일")

    # 완료 버튼
    @discord.ui.button(label="완료", style=discord.ButtonStyle.secondary)
    async def confirm(self, interaction, button):
        result = format_days(self.selected_days)

        await interaction.response.edit_message(
            content=f"최종 선택: {result} 맞습니까?",
            view=ConfirmView(self.selected_days)
        )
        self.stop()
    @discord.ui.button(label="등록취소", style=discord.ButtonStyle.red)
    async def exit(self, interaction, button):
        result = format_days(self.selected_days)

        await interaction.response.edit_message(
            content=f"스케줄 등록취소 하겠습니까?",
            view=ExitView(self.selected_days)
        )
        self.stop()

# 취소 view 
class ExitView(discord.ui.View):
    def __init__(self, selected_days):
        super().__init__(timeout=30)
        self.selected_days = selected_days
        self.selected_text = format_days(self.selected_days)
       
    @discord.ui.button(label="예", style=discord.ButtonStyle.success)
    async def y_exit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(content= "등록이 취소되었습니다")
        self.stop()

    @discord.ui.button(label="아니오", style=discord.ButtonStyle.danger)
    async def n_exit(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 다시 원래 UI로 복귀
        view = WeekView(selected_days=self.selected_days)
        
        await interaction.response.edit_message(
        content=f"현재선택: {self.selected_text}",
        view=view
        )

        self.stop()    
class ConfirmView(discord.ui.View):
    def __init__(self, selected_days):
        super().__init__(timeout=30)
        self.selected_days = selected_days
        self.selected_text = format_days(self.selected_days)
        self.confirm_days ={}
        self.day = ""
    @discord.ui.button(label="O", style=discord.ButtonStyle.success)
    

    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.confirm_days = {day: None for day in self.selected_text if day in WEEK_ORDER}
        for day in self.confirm_days:
            if day !=None:
                self.day = day
                break

        await interaction.response.send_message(
           content= f"✅ 최종 완료: {self.selected_text}"
        )
        await interaction.followup.send(
            content=f"{day}요일 시간선택:",
            view = TimeView(self.confirm_days)
        )
        self.stop()

    @discord.ui.button(label="X", style=discord.ButtonStyle.danger)

    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 다시 원래 UI로 복귀
        view = WeekView(selected_days=self.selected_days)
        
        await interaction.response.edit_message(
        content=f"현재선택: {self.selected_text}",
        view=view
        )

        self.stop()


class TimeView(discord.ui.View):
    def __init__(self, selected_days):
        super().__init__(timeout=60)
        self.selected_days = selected_days
        self.pending = [d for d in WEEK_ORDER if d in selected_days]

    @discord.ui.select(
        placeholder="시간 선택",
        options=[
            discord.SelectOption(label="8:00"),
            discord.SelectOption(label="9:00"),
            discord.SelectOption(label="10:00"),
            discord.SelectOption(label="11:00"),
        ]
    )
    async def select_time(self, interaction, select):
        # 현재 처리할 요일
        day = self.pending.pop(0)

        # 저장
        self.selected_days[day] = select.values[0]

        # 다음 단계
        if self.pending:
            await interaction.response.edit_message(
                content=f"{self.pending[0]}요일 시간 선택",
                view=self
            )
        else:
            await interaction.response.edit_message(
                content=f"✅최종 완료: {self.selected_days}",
                view=None
            )
            final_data = ns(self.selected_days)
            save_schedule(interaction.user.id, final_data)
            self.stop()
        
class FinishView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.finished = False

    @discord.ui.button(label="완료", style=discord.ButtonStyle.success)
    async def finish(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.finished = True
        await interaction.response.send_message("✅ 수정 완료!", ephemeral=True)
        self.stop()

class Change_Modal(discord.ui.Modal):

    def __init__(self, schedule, days):
        super().__init__(title="변경할 시간을 입력(미참여시 x 입력)")
        self.inputs = {}
        self.schedule = schedule
        for day in days:
            input_field = discord.ui.TextInput(
                label=f"{day}",
                default=schedule.get(day, "❌"),
                required=False
            )
            self.inputs[day] = input_field
            self.add_item(input_field)

    async def on_submit(self, interaction: discord.Interaction):

        db = load_db()
        user_id = str(interaction.user.id)

        for day, field in self.inputs.items():
            value = field.value.strip()
            if value:
                db[user_id][day] = value

        save_db(db)

        new_db = load_db()
        self.schedule = new_db.get(user_id, {})
        embed =  show_schedule(interaction.user.display_name,self.schedule)
        await interaction.response.send_message(
            content = "✅ 스케줄 변경 완료",
            embed=embed,
            ephemeral=True
            )
        
class ScheduleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.start = False
    async def update(self, interaction, day=None):
        db = load_db()

        path = create_schedule_image(db, interaction.guild, day)
        file = discord.File(path, filename="schedule.png")

        await interaction.response.edit_message(
            content=f"📅 {'전체' if not day else day} 스케줄",
            attachments=[file],
            view=self
        )

    # 요일 버튼들
    @discord.ui.button(label="월", style=discord.ButtonStyle.primary)
    async def mon(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.start = True
        await self.update(interaction, "월")

    @discord.ui.button(label="화", style=discord.ButtonStyle.primary)
    async def tue(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.start = True
        await self.update(interaction, "화")

    @discord.ui.button(label="수", style=discord.ButtonStyle.primary)
    async def wed(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.start = True
        await self.update(interaction, "수")

    @discord.ui.button(label="목", style=discord.ButtonStyle.primary)
    async def thu(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.start = True
        await self.update(interaction, "목")

    @discord.ui.button(label="금", style=discord.ButtonStyle.primary)
    async def fri(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.start = True
        await self.update(interaction, "금")

    @discord.ui.button(label="토", style=discord.ButtonStyle.primary)
    async def sat(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.start = True
        await self.update(interaction, "토")

    @discord.ui.button(label="일", style=discord.ButtonStyle.primary)
    async def sun(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.start = True
        await self.update(interaction, "일")

    @discord.ui.button(label="전체", style=discord.ButtonStyle.success)
    async def all(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.start = True
        await self.update(interaction, None)

    @discord.ui.button(label="종료", style=discord.ButtonStyle.red)
    async def schedule_stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(
            content="스케줄 보기를 종료하였습니다",
            view=self,
            attachments=[]
        )
        self.stop()
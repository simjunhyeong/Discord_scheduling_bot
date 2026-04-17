from PIL import Image, ImageDraw, ImageFont
from config import WEEK_ORDER

def get_day_color(count):
    if count >= 5:
        return (144, 238, 144)  # 연한 초록
    elif count == 4:
        return (255, 255, 153)  # 연한 노랑
    elif count == 0:
        return (0,0,0)
    else:
        return None

def create_schedule_image(db, guild, selected_day=None):
    days = [selected_day] if selected_day else WEEK_ORDER

    try:
        font = ImageFont.truetype("fonts/malgun.ttf", 24)
        small_font = ImageFont.truetype("fonts/malgun.ttf", 20)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    day_count = {}

    for day in days:
        count = 0
        for schedule in db.values():
            value = schedule.get(day)

            if value and value not in ["x", "❌", "=="]:
                count += 1

        day_count[day] = count

    # 크기 설정
    cell_w = 120
    cell_h = 50

    rows = len(db) + 1
    cols = len(days) + 1

    img_w = cols * cell_w
    img_h = rows * cell_h

    img = Image.new("RGB", (img_w, img_h), "white")
    draw = ImageDraw.Draw(img)

    # ===== 헤더 =====
    draw.text((10, 10), "이름", font=font, fill="black")

    for i, day in enumerate(days):
        x = (i + 1) * cell_w + 20
        draw.text((x, 10), day, font=font, fill="black")

    # ===== 내용 =====
    for row_idx, (user_id, schedule) in enumerate(db.items()):
        member = guild.get_member(int(user_id))
        name = member.display_name[-3:] if member else user_id

        y = (row_idx + 1) * cell_h + 10

        # 이름
        draw.text((10, y), name, font=small_font, fill="black")

        # 시간
        for col_idx, day in enumerate(days):
            value = schedule.get(day)
            if value in ["x", "❌", "=="]:
                value =  "=="
                
            x = (col_idx + 1) * cell_w + 20
           
            cell_left = (col_idx + 1) * cell_w
            cell_top = (row_idx + 1) * cell_h
            cell_right = cell_left + cell_w
            cell_bottom = cell_top + cell_h

            bg_color = get_day_color(day_count[day])

            if bg_color:
                draw.rectangle(
                    [cell_left, cell_top, cell_right, cell_bottom],
                    fill=bg_color
                )

            color = "red" if value == "==" else "black"
            draw.text((x, y), value, font=small_font, fill=color)

    # ===== 격자선 =====
    for i in range(rows):
        y = i * cell_h
        draw.line([(0, y), (img_w, y)], fill="black")

    for j in range(cols):
        x = j * cell_w
        draw.line([(x, 0), (x, img_h)], fill="black")

    path = "schedule.png"
    img.save(path)

    return path


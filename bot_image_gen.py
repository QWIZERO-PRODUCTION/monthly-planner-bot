from PIL import Image, ImageDraw, ImageFont

class ImageGenerator:
    def generate_stats_image(self, stats):
        img = Image.new('RGB', (1080, 1920), (20, 25, 35))
        draw = ImageDraw.Draw(img)
        
        try:
            f_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 50)
            f_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 35)
            f_normal = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        except:
            f_title = ImageFont.load_default()
            f_large = ImageFont.load_default()
            f_normal = ImageFont.load_default()
        
        y = 100
        accent = (138, 43, 226)
        success = (76, 175, 80)
        text_col = (255, 255, 255)
        warning = (255, 193, 7)
        
        # Заголовок
        month = stats.get('month', 'Month')
        draw.text((540, y), f"📅 {month}", fill=accent, font=f_title, anchor="mm")
        y += 120
        
        # ЗАДАЧИ
        draw.text((80, y), "✅ ЗАДАЧИ", fill=text_col, font=f_large)
        y += 60
        
        tasks_total = stats.get('tasks_total', 0)
        tasks_done = stats.get('tasks_done', 0)
        pct = (tasks_done/tasks_total*100) if tasks_total else 0
        
        # Прогресс бар
        bar_w = 900
        draw.rectangle([80, y, 80+bar_w, y+40], outline=accent, width=2)
        bar_fill = int(bar_w * pct / 100)
        draw.rectangle([80, y, 80+bar_fill, y+40], fill=success)
        draw.text((540, y+20), f"{pct:.0f}%", fill=text_col, font=f_large, anchor="mm")
        y += 80
        
        draw.text((80, y), f"{tasks_done} из {tasks_total} выполнено", fill=text_col, font=f_normal)
        y += 120
        
        # СОН
        draw.text((80, y), "😴 СОН", fill=text_col, font=f_large)
        y += 60
        
        avg_sleep = stats.get('avg_sleep', 0)
        draw.text((80, y), f"{avg_sleep:.1f} часов в среднем", fill=text_col, font=f_normal)
        y += 70
        
        if avg_sleep >= 8:
            status = "🟢 Отличный сон!"
            col = success
        elif avg_sleep >= 7:
            status = "🟡 Норма"
            col = warning
        else:
            status = "🔴 Мало сна"
            col = (255, 76, 76)
        
        draw.text((80, y), status, fill=col, font=f_normal)
        y += 130
        
        # ДОСТИЖЕНИЯ
        draw.text((80, y), "🏆 ДОСТИЖЕНИЯ", fill=text_col, font=f_large)
        y += 70
        
        if pct >= 80:
            draw.text((100, y), "✨ Успешный месяц!", fill=accent, font=f_normal)
            y += 50
        
        if avg_sleep >= 7:
            draw.text((100, y), "🌙 Здоровый сон!", fill=accent, font=f_normal)
            y += 50
        
        if pct == 100:
            draw.text((100, y), "💪 Железная воля!", fill=accent, font=f_normal)
            y += 50
        
        y = 1850
        draw.text((540, y), "Поделись результатом в истории!", 
                 fill=text_col, font=f_normal, anchor="mm")
        
        path = "/tmp/stats.png"
        img.save(path)
        return path
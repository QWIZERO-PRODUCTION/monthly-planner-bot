#!/usr/bin/env python3
import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from database import Database
from image_generator import ImageGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = Database()
img_gen = ImageGenerator()

class PlannerBot:
    def __init__(self, token):
        self.token = token
        self.app = Application.builder().token(token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help_cmd))
        self.app.add_handler(CommandHandler("new_plan", self.new_plan))
        self.app.add_handler(CommandHandler("add_goal", self.add_goal))
        self.app.add_handler(CommandHandler("add_task", self.add_task))
        self.app.add_handler(CommandHandler("log_sleep", self.log_sleep))
        self.app.add_handler(CommandHandler("view_plan", self.view_plan))
        self.app.add_handler(CommandHandler("statistics", self.statistics))
        self.app.add_handler(CommandHandler("export_image", self.export_image))
        self.app.add_handler(CommandHandler("mark_done", self.mark_done))
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        username = update.effective_user.username or "User"
        db.create_user(user_id, username)
        
        text = ("👋 Привет! Я твой месячный планировщик!\n\n"
                "🎯 Я помогу тебе:\n"
                "• Планировать дела на месяц\n"
                "• Отслеживать сон\n"
                "• Видеть прогресс\n\n"
                "/help для команд или /new_plan начать!")
        await update.message.reply_text(text)
    
    async def help_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = ("/new_plan - Новый план\n"
                "/add_goal - Добавить цель\n"
                "/add_task - Добавить дело\n"
                "/log_sleep - Логировать сон\n"
                "/view_plan - Показать план\n"
                "/statistics - Статистика\n"
                "/export_image - Картинка для истории\n"
                "/mark_done - Отметить выполненное")
        await update.message.reply_text(text)
    
    async def new_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        now = datetime.now()
        plan_id = db.create_monthly_plan(user_id, now.year, now.month)
        
        if plan_id:
            text = f"✅ План на {now.strftime('%B %Y')} создан!"
        else:
            text = "❌ План уже существует!"
        await update.message.reply_text(text)
    
    async def add_goal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        now = datetime.now()
        plan = db.get_current_plan(user_id, now.year, now.month)
        
        if not plan:
            await update.message.reply_text("❌ Создайте план! /new_plan")
            return
        
        context.user_data['plan_id'] = plan['id']
        context.user_data['mode'] = 'add_goal'
        await update.message.reply_text("📝 Введите цель:")
    
    async def add_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        now = datetime.now()
        plan = db.get_current_plan(user_id, now.year, now.month)
        
        if not plan:
            await update.message.reply_text("❌ Создайте план! /new_plan")
            return
        
        context.user_data['plan_id'] = plan['id']
        context.user_data['mode'] = 'add_task_day'
        
        keyboard = []
        for day in range(1, 32, 7):
            row = [InlineKeyboardButton(str(d), callback_data=f"day_{d}") 
                   for d in range(day, min(day+7, 32))]
            keyboard.append(row)
        
        await update.message.reply_text("📅 День:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def log_sleep(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        now = datetime.now()
        context.user_data['sleep_date'] = (now.year, now.month, now.day)
        context.user_data['mode'] = 'log_sleep'
        await update.message.reply_text(f"😴 Часов сна для {now.strftime('%d.%m')}:")
    
    async def view_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        now = datetime.now()
        plan = db.get_current_plan(user_id, now.year, now.month)
        
        if not plan:
            await update.message.reply_text("❌ Нет плана!")
            return
        
        goals = db.get_goals(plan['id'])
        text = f"📅 План на {now.strftime('%B')}\n\n"
        
        for i, g in enumerate(goals, 1):
            text += f"{'✅' if g['completed'] else '⭕'} {g['title']}\n"
        
        await update.message.reply_text(text)
    
    async def statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        now = datetime.now()
        plan = db.get_current_plan(user_id, now.year, now.month)
        
        if not plan:
            await update.message.reply_text("❌ Нет плана!")
            return
        
        tasks = db.get_tasks_by_plan(plan['id'])
        sleep = db.get_sleep_log(user_id, now.year, now.month)
        
        completed = sum(1 for t in tasks if t['completed'])
        pct = (completed/len(tasks)*100) if tasks else 0
        avg_sleep = sum(s['hours'] for s in sleep)/len(sleep) if sleep else 0
        
        text = (f"📊 Статистика {now.strftime('%B')}\n\n"
                f"✅ Задачи: {completed}/{len(tasks)} ({pct:.0f}%)\n"
                f"😴 Средний сон: {avg_sleep:.1f}ч")
        
        await update.message.reply_text(text)
    
    async def export_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        now = datetime.now()
        plan = db.get_current_plan(user_id, now.year, now.month)
        
        if not plan:
            await update.message.reply_text("❌ Нет плана!")
            return
        
        await update.message.reply_text("⏳ Генерирую картинку...")
        
        tasks = db.get_tasks_by_plan(plan['id'])
        sleep = db.get_sleep_log(user_id, now.year, now.month)
        
        stats = {
            'month': now.strftime('%B'),
            'tasks_done': sum(1 for t in tasks if t['completed']),
            'tasks_total': len(tasks),
            'avg_sleep': sum(s['hours'] for s in sleep)/len(sleep) if sleep else 0
        }
        
        image_path = img_gen.generate_stats_image(stats)
        
        with open(image_path, 'rb') as f:
            await update.message.reply_photo(f, caption="📊 Поделись в истории!")
        
        os.remove(image_path)
    
    async def mark_done(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        now = datetime.now()
        plan = db.get_current_plan(user_id, now.year, now.month)
        
        if not plan:
            await update.message.reply_text("❌ Нет плана!")
            return
        
        tasks = db.get_tasks_by_plan(plan['id'])
        keyboard = [[InlineKeyboardButton(f"✅ {t['title'][:20]}", 
                                         callback_data=f"done_{t['id']}")] 
                    for t in tasks if not t['completed']]
        
        await update.message.reply_text("✅ Выберите:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("day_"):
            day = int(query.data.split("_")[1])
            context.user_data['task_day'] = day
            await query.edit_message_text(f"📝 Задача на день {day}:")
        
        elif query.data.startswith("done_"):
            task_id = int(query.data.split("_")[1])
            db.mark_task_complete(task_id)
            await query.edit_message_text("✅ Выполнено!")
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        mode = context.user_data.get('mode')
        user_id = update.effective_user.id
        
        if mode == 'add_goal':
            plan_id = context.user_data.get('plan_id')
            db.create_goal(plan_id, user_id, text)
            await update.message.reply_text("✅ Цель добавлена!")
            context.user_data.pop('mode', None)
        
        elif mode == 'add_task_day':
            if 'task_day' in context.user_data:
                plan_id = context.user_data.get('plan_id')
                day = context.user_data.pop('task_day')
                db.create_task(plan_id, user_id, day, text)
                await update.message.reply_text(f"✅ Дело добавлено на день {day}!")
                context.user_data.pop('mode', None)
        
        elif mode == 'log_sleep':
            try:
                hours = float(text)
                year, month, day = context.user_data['sleep_date']
                db.log_sleep(user_id, year, month, day, hours)
                await update.message.reply_text(f"✅ Сон: {hours}ч")
                context.user_data.pop('mode', None)
            except:
                await update.message.reply_text("❌ Число!")
    
    def run(self):
        self.app.run_polling()

if __name__ == '__main__':
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("❌ TELEGRAM_BOT_TOKEN не установлен!")
    
    bot = PlannerBot(token)
    logger.info("🚀 Бот запущен!")
    bot.run()
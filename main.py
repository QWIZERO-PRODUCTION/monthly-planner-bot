import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from database import Database

db = Database()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db.create_user(user_id, "user")
    await update.message.reply_text("👋 Привет! Я твой планировщик!\n/help для команд")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "/new_plan - Новый план\n/add_task - Добавить дело\n/log_sleep - Логировать сон\n/statistics - Статистика"
    await update.message.reply_text(text)

async def new_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    result = db.create_monthly_plan(user_id)
    if result:
        await update.message.reply_text("✅ План создан!")
    else:
        await update.message.reply_text("❌ Ошибка или план уже есть")

async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📝 Введите название дела:")
    context.user_data['mode'] = 'add_task'

async def log_sleep(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("😴 Введите часы сна:")
    context.user_data['mode'] = 'log_sleep'

async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Статистика: пока нет данных")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get('mode')
    user_id = update.effective_user.id
    text = update.message.text
    
    if mode == 'add_task':
        await update.message.reply_text(f"✅ Дело добавлено: {text}")
        context.user_data.pop('mode', None)
    elif mode == 'log_sleep':
        try:
            hours = float(text)
            db.log_sleep(user_id, hours)
            await update.message.reply_text(f"✅ Сон: {hours}ч")
            context.user_data.pop('mode', None)
        except:
            await update.message.reply_text("❌ Введи число!")

def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    app = Application.builder().token(token).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("new_plan", new_plan))
    app.add_handler(CommandHandler("add_task", add_task))
    app.add_handler(CommandHandler("log_sleep", log_sleep))
    app.add_handler(CommandHandler("statistics", statistics))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    app.run_polling()

if __name__ == '__main__':
    main()

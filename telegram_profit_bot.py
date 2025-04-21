from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

# Твой токен
TOKEN = "8100338546:AAGc8L9G13by2oO_OTVGK2aIe0x3HgS6a70"

def generate_pdf(data):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica", 14)
    p.drawString(100, 800, f"Отчёт за {datetime.now().strftime('%d.%m.%Y')}")
    y = 770
    for key, value in data.items():
        p.drawString(100, y, f"{key}: {value}₽")
        y -= 25
    p.drawString(100, y - 10, "-" * 30)
    y -= 35
    profit = data['Работа'] + data['Запчасти'] - data['Закупка'] - data['Затраты']
    p.drawString(100, y, f"Прибыль: {profit}₽")
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

def handle_day(update: Update, context: CallbackContext):
    try:
        text = update.message.text.replace("/день", "").strip()
        parts = text.split()
        data = {}
        for part in parts:
            key, value = part.split("=")
            value = int(value)
            if key.lower() == "работа":
                data["Работа"] = value
            elif key.lower() == "запчасти":
                data["Запчасти"] = value
            elif key.lower() == "закупка":
                data["Закупка"] = value
            elif key.lower() == "затраты":
                data["Затраты"] = value

        if len(data) != 4:
            update.message.reply_text("Нужны все 4 параметра: работа, запчасти, закупка, затраты.")
            return

        revenue = data["Работа"] + data["Запчасти"]
        expenses = data["Закупка"] + data["Затраты"]
        profit = revenue - expenses

        message = (
            f"Отчёт за {datetime.now().strftime('%d.%m.%Y')}:\n\n"
            f"Работа: {data['Работа']}₽\n"
            f"Запчасти: {data['Запчасти']}₽\n"
            f"Закупка: {data['Закупка']}₽\n"
            f"Затраты: {data['Затраты']}₽\n\n"
            f"Выручка: {revenue}₽\n"
            f"Расходы: {expenses}₽\n"
            f"Прибыль: {profit}₽"
        )

        update.message.reply_text(message)

        pdf = generate_pdf(data)
        update.message.reply_document(document=pdf, filename="report.pdf")

    except Exception as e:
        update.message.reply_text(f"Ошибка: {str(e)}")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("день", handle_day))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

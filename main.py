import os
import math
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_NAME = "Eventora 🎉"

WAITERS_COST = 1200  # per waiter
DECOR_BASE = 8000
LIGHTING_COST = 5000
FLOWER_PLASTIC = 3000
FLOWER_REAL = 7000

POPULAR_FOODS = [
    "সাদাবাত পোলাও", "মুরগির রোস্ট", "গরুর গোস্ত", "খাসির গোস্ত", "ডাল",
    "সবজি", "ডিম", "বোরহানি", "দই", "মিষ্টি", "জর্দা", "সালাদ",
    "চিকেন কাবাব", "বিফ কাবাব", "নান রুটি", "পরোটা", "ফ্রাইড রাইস",
    "চিকেন ফ্রাই", "চিকেন কারি", "বিফ কারি"
]

USER_DATA = {}

def estimate_food_cost(food_count):
    # আনুমানিক প্রতি প্লেট খরচ (কমিয়ে ধরা)
    base = 180
    return base + (food_count * 12)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🎉 Welcome to {BOT_NAME}\n\n"
        "আপনার অতিথির সংখ্যা লিখুন (৫০ - ২০০০):"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_id not in USER_DATA:
        USER_DATA[user_id] = {}

    data = USER_DATA[user_id]

    # Step 1: Guest count
    if "guests" not in data:
        try:
            guests = int(text)
            if guests < 50 or guests > 2000:
                raise ValueError
            data["guests"] = guests

            food_list_text = "\n".join([f"✅ {f}" for f in POPULAR_FOODS])
            await update.message.reply_text(
                "খাবারের তালিকা (ধরে নেওয়া হয়েছে জনপ্রিয় আইটেম):\n\n"
                f"{food_list_text}\n\n"
                "OK লিখুন খাবার কনফার্ম করতে"
            )
        except:
            await update.message.reply_text("❌ দয়া করে ৫০ থেকে ২০০০ এর মধ্যে সংখ্যা দিন")
        return

    # Step 2: Food confirm
    if "food_confirmed" not in data:
        if text.lower() == "ok":
            data["food_confirmed"] = True
            await update.message.reply_text(
                "ডেকোরেশন কনফার্ম করা হয়েছে ✅\n"
                "ফুল টাইপ লিখুন:\n1 = প্লাস্টিক ফুল\n2 = অরিজিনাল ফুল"
            )
        else:
            await update.message.reply_text("খাবার কনফার্ম করতে OK লিখুন")
        return

    # Step 3: Flower type
    if "flower" not in data:
        if text == "1":
            data["flower"] = "plastic"
        elif text == "2":
            data["flower"] = "real"
        else:
            await update.message.reply_text("1 বা 2 লিখুন")
            return

        guests = data["guests"]
        food_cost_per_plate = estimate_food_cost(len(POPULAR_FOODS))
        total_food = guests * food_cost_per_plate

        waiters = math.ceil(guests / 10)
        waiter_cost = waiters * WAITERS_COST

        flower_cost = FLOWER_PLASTIC if data["flower"] == "plastic" else FLOWER_REAL

        total = (
            total_food +
            DECOR_BASE +
            LIGHTING_COST +
            flower_cost +
            waiter_cost
        )

        summary = f"""
📊 Event Summary - {BOT_NAME}

👥 অতিথি: {guests}

🍽️ প্রতি প্লেট আনুমানিক: {food_cost_per_plate} টাকা
🍛 মোট খাবার খরচ: {total_food} টাকা

🎪 ডেকোরেশন: {DECOR_BASE} টাকা
💡 লাইটিং: {LIGHTING_COST} টাকা
🌸 ফুল: {flower_cost} টাকা
🧑‍🍳 ওয়েটার ({waiters} জন): {waiter_cost} টাকা

====================
💰 মোট আনুমানিক খরচ: {total} টাকা
====================

ধন্যবাদ Eventora ব্যবহার করার জন্য 🎉
"""

        await update.message.reply_text(summary)

        USER_DATA.pop(user_id, None)

def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        print("BOT_TOKEN not set")
        return

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Eventora Bot Started...")
    app.run_polling()

if __name__ == "__main__":
    main()

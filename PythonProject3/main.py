import asyncio
import logging
import os

from dotenv import load_dotenv

import aiosqlite
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    CallbackQuery,
    BotCommand
)
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage


# ================= CONFIG =================
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN not found")

bot = Bot(token=TOKEN)

dp = Dispatcher(storage=MemoryStorage())


# ================= DATABASE =================
async def init_db():

    async with aiosqlite.connect("fitness.db") as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            weight INTEGER,
            height INTEGER,
            goal TEXT,
            calories INTEGER,
            protein INTEGER,
            fat INTEGER,
            carbs INTEGER
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            workout TEXT,
            date TEXT
        )
        """)

        await db.commit()


# ================= BOT COMMANDS =================
async def set_commands():

    commands = [

        BotCommand(
            command="start",
            description="Start the bot"
        ),

        BotCommand(
            command="help",
            description="Show all commands"
        ),

        BotCommand(
            command="profile",
            description="Calculate calories"
        ),

        BotCommand(
            command="workouts",
            description="Workout programs"
        ),

        BotCommand(
            command="plan",
            description="Weekly training plan"
        ),

        BotCommand(
            command="log",
            description="Save workout log"
        ),

        BotCommand(
            command="logs",
            description="Show recent workouts"
        ),

        BotCommand(
            command="nutrition",
            description="Nutrition tips"
        ),

        BotCommand(
            command="water",
            description="Water recommendation"
        ),

        BotCommand(
            command="sleep",
            description="Sleep recommendation"
        ),

        BotCommand(
            command="cardio",
            description="Cardio recommendation"
        ),

        BotCommand(
            command="motivation",
            description="Motivation quote"
        )
    ]

    await bot.set_my_commands(commands)


# ================= FSM =================
class Form(StatesGroup):

    weight = State()

    height = State()

    goal = State()

    log = State()


# ================= CALCULATOR =================
def calculate(data):

    weight = int(data["weight"])

    goal = data["goal"]

    calories = weight * 30

    if goal == "mass":
        calories += 300

    else:
        calories -= 300

    protein = weight * 2

    fat = weight * 1

    carbs = (calories - (protein * 4 + fat * 9)) // 4

    return calories, protein, fat, carbs


# ================= MENU =================
def main_menu():

    kb = InlineKeyboardBuilder()

    kb.button(text="📊 Profile", callback_data="profile")

    kb.button(text="🏋️ Workouts", callback_data="workouts")

    kb.button(text="📅 Plan", callback_data="plan")

    kb.button(text="📝 Log Workout", callback_data="log")

    kb.button(text="📜 My Logs", callback_data="mylogs")

    kb.button(text="🥗 Nutrition", callback_data="food")

    kb.button(text="💧 Water", callback_data="water")

    kb.button(text="😴 Sleep", callback_data="sleep")

    kb.button(text="🏃 Cardio", callback_data="cardio")

    kb.button(text="💪 Motivation", callback_data="motivation")

    kb.button(text="📖 Help", callback_data="help")

    kb.adjust(2)

    return kb.as_markup()


# ================= WORKOUT MENU =================
def workouts_menu():

    kb = InlineKeyboardBuilder()

    kb.button(text="🔥 Push", callback_data="push")

    kb.button(text="💪 Pull", callback_data="pull")

    kb.button(text="🦵 Legs", callback_data="legs")

    kb.adjust(1)

    return kb.as_markup()


# ================= WORKOUTS =================
WORKOUTS = {

    "push": (
        "🔥 PUSH DAY\n\n"
        "1. Bench Press — 4x8\n"
        "2. Dumbbell Press — 3x10\n"
        "3. Shoulder Press — 3x12\n"
        "4. Triceps Pushdown — 3x10"
    ),

    "pull": (
        "💪 PULL DAY\n\n"
        "1. Pull-ups — 4x\n"
        "2. Barbell Row — 4x8\n"
        "3. Lat Pulldown — 3x10\n"
        "4. Biceps Curl — 3x10"
    ),

    "legs": (
        "🦵 LEGS DAY\n\n"
        "1. Squats — 4x8\n"
        "2. Leg Press — 3x10\n"
        "3. Lunges — 3x12\n"
        "4. Calves — 4x15"
    )
}


# ================= START =================
@dp.message(CommandStart())
async def start(message: Message):

    text = (
        "🔥 FITNESS BOT PRO\n\n"

        "Welcome to your personal fitness assistant 💪\n\n"

        "📌 FEATURES:\n"
        "• calorie calculator\n"
        "• workout programs\n"
        "• nutrition tips\n"
        "• workout logs\n"
        "• cardio & recovery\n\n"

        "👇 Choose a menu option"
    )

    await message.answer(
        text,
        reply_markup=main_menu()
    )


# ================= HELP =================
@dp.message(Command("help"))
@dp.callback_query(F.data == "help")
async def help_menu(event):

    text = (
        "📖 COMMANDS\n\n"

        "/start — start bot\n"
        "/help — show commands\n"
        "/profile — calculate calories\n"
        "/workouts — workout programs\n"
        "/plan — weekly plan\n"
        "/log — save workout\n"
        "/logs — recent workouts\n"
        "/nutrition — nutrition tips\n"
        "/water — water advice\n"
        "/sleep — sleep advice\n"
        "/cardio — cardio tips\n"
        "/motivation — motivation\n\n"

        "💬 TEXT COMMANDS:\n"
        "protein\n"
        "creatine\n"
        "abs\n"
        "warmup\n"
        "bcaa\n"
        "mass\n"
        "cut"
    )

    if isinstance(event, Message):

        await event.answer(
            text,
            reply_markup=main_menu()
        )

    else:

        await event.message.answer(
            text,
            reply_markup=main_menu()
        )

        await event.answer()


# ================= PROFILE =================
@dp.message(Command("profile"))
@dp.callback_query(F.data == "profile")
async def profile(event, state: FSMContext):

    if isinstance(event, Message):

        await event.answer(
            "⚖️ Enter your weight:"
        )

    else:

        await event.message.answer(
            "⚖️ Enter your weight:"
        )

        await event.answer()

    await state.set_state(Form.weight)


@dp.message(Form.weight)
async def weight(message: Message, state: FSMContext):

    try:
        weight = int(message.text)

    except:
        await message.answer("❌ Enter a number")
        return

    if weight < 30 or weight > 300:

        await message.answer(
            "❌ Invalid weight"
        )

        return

    await state.update_data(weight=weight)

    await message.answer(
        "📏 Enter your height:"
    )

    await state.set_state(Form.height)


@dp.message(Form.height)
async def height(message: Message, state: FSMContext):

    try:
        height = int(message.text)

    except:
        await message.answer("❌ Enter a number")
        return

    if height < 100 or height > 250:

        await message.answer(
            "❌ Invalid height"
        )

        return

    await state.update_data(height=height)

    await message.answer(
        "🎯 Enter your goal:\n\n"
        "mass — muscle gain\n"
        "cut — fat loss"
    )

    await state.set_state(Form.goal)


@dp.message(Form.goal)
async def goal(message: Message, state: FSMContext):

    goal = message.text.lower()

    if goal not in ["mass", "cut"]:

        await message.answer(
            "❌ Enter mass or cut"
        )

        return

    data = await state.get_data()

    data["goal"] = goal

    calories, protein, fat, carbs = calculate(data)

    async with aiosqlite.connect("fitness.db") as db:

        await db.execute("""
        INSERT OR REPLACE INTO users
        VALUES(?,?,?,?,?,?,?,?)
        """, (
            message.from_user.id,
            data["weight"],
            data["height"],
            goal,
            calories,
            protein,
            fat,
            carbs
        ))

        await db.commit()

    await message.answer(
        f"📊 YOUR RESULTS\n\n"
        f"🔥 Calories: {calories}\n"
        f"🍗 Protein: {protein} g\n"
        f"🥑 Fat: {fat} g\n"
        f"🍞 Carbs: {carbs} g",
        reply_markup=main_menu()
    )

    await state.clear()


# ================= WORKOUTS =================
@dp.message(Command("workouts"))
@dp.callback_query(F.data == "workouts")
async def workouts(event):

    if isinstance(event, Message):

        await event.answer(
            "🏋️ Choose workout:",
            reply_markup=workouts_menu()
        )

    else:

        await event.message.answer(
            "🏋️ Choose workout:",
            reply_markup=workouts_menu()
        )

        await event.answer()


@dp.callback_query(F.data.in_(WORKOUTS.keys()))
async def show_workout(callback: CallbackQuery):

    await callback.message.answer(
        WORKOUTS[callback.data],
        reply_markup=main_menu()
    )

    await callback.answer()


# ================= PLAN =================
@dp.message(Command("plan"))
@dp.callback_query(F.data == "plan")
async def plan(event):

    text = (
        "📅 WEEKLY PLAN\n\n"
        "Monday — Push\n"
        "Tuesday — Rest\n"
        "Wednesday — Pull\n"
        "Thursday — Rest\n"
        "Friday — Legs\n"
        "Saturday — Cardio\n"
        "Sunday — Rest"
    )

    if isinstance(event, Message):

        await event.answer(
            text,
            reply_markup=main_menu()
        )

    else:

        await event.message.answer(
            text,
            reply_markup=main_menu()
        )

        await event.answer()


# ================= LOG =================
@dp.message(Command("log"))
@dp.callback_query(F.data == "log")
async def log(event, state: FSMContext):

    if isinstance(event, Message):

        await event.answer(
            "📝 Write today's workout:"
        )

    else:

        await event.message.answer(
            "📝 Write today's workout:"
        )

        await event.answer()

    await state.set_state(Form.log)


@dp.message(Form.log)
async def save_log(message: Message, state: FSMContext):

    async with aiosqlite.connect("fitness.db") as db:

        await db.execute("""
        INSERT INTO logs(user_id, workout, date)
        VALUES(?,?,datetime('now'))
        """, (
            message.from_user.id,
            message.text
        ))

        await db.commit()

    await message.answer(
        "✅ Workout saved",
        reply_markup=main_menu()
    )

    await state.clear()


# ================= LOGS =================
@dp.message(Command("logs"))
@dp.callback_query(F.data == "mylogs")
async def my_logs(event):

    user_id = (
        event.from_user.id
        if isinstance(event, Message)
        else event.from_user.id
    )

    async with aiosqlite.connect("fitness.db") as db:

        cursor = await db.execute("""
        SELECT workout, date
        FROM logs
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 5
        """, (user_id,))

        logs = await cursor.fetchall()

    if not logs:

        text = "❌ No logs found"

    else:

        text = "📜 RECENT WORKOUTS\n\n"

        for workout, date in logs:

            text += f"• {workout}\n📅 {date}\n\n"

    if isinstance(event, Message):

        await event.answer(
            text,
            reply_markup=main_menu()
        )

    else:

        await event.message.answer(
            text,
            reply_markup=main_menu()
        )

        await event.answer()


# ================= SIMPLE CALLBACKS =================
async def simple_message(event, text):

    if isinstance(event, Message):

        await event.answer(
            text,
            reply_markup=main_menu()
        )

    else:

        await event.message.answer(
            text,
            reply_markup=main_menu()
        )

        await event.answer()


@dp.message(Command("nutrition"))
@dp.callback_query(F.data == "food")
async def nutrition(event):

    await simple_message(
        event,
        "🥗 Eat more protein and vegetables"
    )


@dp.message(Command("water"))
@dp.callback_query(F.data == "water")
async def water(event):

    await simple_message(
        event,
        "💧 Drink 2-3 liters daily"
    )


@dp.message(Command("sleep"))
@dp.callback_query(F.data == "sleep")
async def sleep(event):

    await simple_message(
        event,
        "😴 Sleep 7-8 hours"
    )


@dp.message(Command("cardio"))
@dp.callback_query(F.data == "cardio")
async def cardio(event):

    await simple_message(
        event,
        "🏃 20-30 min cardio"
    )


@dp.message(Command("motivation"))
@dp.callback_query(F.data == "motivation")
async def motivation(event):

    await simple_message(
        event,
        "💪 Discipline beats motivation"
    )


# ================= TEXT COMMANDS =================
@dp.message(F.text.lower() == "protein")
async def protein(message: Message):

    await message.answer(
        "🍗 Protein: 1.6-2.2g per kg"
    )


@dp.message(F.text.lower() == "creatine")
async def creatine(message: Message):

    await message.answer(
        "⚡ Creatine: 5g daily"
    )


@dp.message(F.text.lower() == "abs")
async def abs_workout(message: Message):

    await message.answer(
        "🔥 Crunches 3x20\n"
        "🔥 Plank 3x1 min"
    )


@dp.message(F.text.lower() == "warmup")
async def warmup(message: Message):

    await message.answer(
        "🔥 5 minutes cardio warm-up"
    )


@dp.message(F.text.lower() == "bcaa")
async def bcaa(message: Message):

    await message.answer(
        "⚡ BCAA helps recovery"
    )


@dp.message(F.text.lower() == "mass")
async def mass(message: Message):

    await message.answer(
        "🍚 Calorie surplus for muscle gain"
    )


@dp.message(F.text.lower() == "cut")
async def cut(message: Message):

    await message.answer(
        "🥗 Calorie deficit for fat loss"
    )


# ================= UNKNOWN =================
@dp.message()
async def unknown(message: Message):

    await message.answer(
        "❌ Unknown command\nUse /help"
    )


# ================= RUN =================
async def main():

    logging.basicConfig(level=logging.INFO)

    await init_db()

    await set_commands()

    print("🚀 BOT STARTED")

    try:
        await dp.start_polling(bot)

    finally:
        await bot.session.close()


if __name__ == "__main__":

    asyncio.run(main())
# 🤖 Fitness Bot Pro

## 1. Project Name

**Fitness Bot Pro**

---

## 2. Project Description

Fitness Bot Pro is a Telegram chatbot developed in Python using the aiogram framework. The bot helps users calculate calories and macronutrients, save workouts, track progress, and receive fitness recommendations.

### Main Features

* Calorie calculator
* Protein, fat, and carbs calculation
* Workout plans
* Workout logs
* Nutrition recommendations
* Cardio and sleep tips
* Motivation commands
* SQLite database support

---

## 3. Technologies Used

* Python 3
* aiogram
* aiosqlite
* SQLite
* python-dotenv
* asyncio
* Telegram Bot API

---

## 4. Installation Guide

### 1. Download project files

Download all project files into one folder.

---

### 2. Install dependencies

Open terminal in the project folder and run:

```bash id="nrh4v4"
pip install aiogram aiosqlite python-dotenv
```

---

### 3. Create `.env` file

Create a file named `.env` in the project folder.

Add your Telegram bot token:

```env id="jlwm2k"
BOT_TOKEN=YOUR_BOT_TOKEN
```

Example:

```env id="b7j7de"
BOT_TOKEN=123456789:ABCDEF_EXAMPLE_TOKEN
```

---

## 5. Running the Bot

Run the bot with:

```bash id="0mhb3z"
python main.py
```

If the bot starts successfully, you will see:

```bash id="a4mjlwm"
🚀 BOT STARTED
```

---

## 6. Examples of Bot Usage

### `/start`

```text id="y4x8sl"
🔥 FITNESS BOT PRO

Welcome!

This bot helps you:
• calculate calories and macros
• save workouts
• get workout plans
• track progress
• receive fitness tips
```

---

### Profile Example

User input:

```text id="sfxl9f"
70
180
mass
```

Bot response:

```text id="wtg0n9"
📊 YOUR PLAN

🔥 Calories: 2400
🍗 Protein: 140 g
🥑 Fat: 70 g
🍞 Carbs: 282 g
```

---

### Workout Example

```text id="e9q2d0"
🔥 PUSH DAY

1. Bench Press — 4x8
2. Dumbbell Press — 3x10
3. Shoulder Press — 3x12
4. Triceps — 3x10
```

---

### Workout Log Example

User:

```text id="9k78yq"
Bench press + cardio
```

Bot:

```text id="fkr4lr"
✅ Log saved
```

---

### Motivation Command

User:

```text id="ryon3k"
motivation
```

Bot:

```text id="69p49h"
💪 Never give up.
Discipline is more important than motivation.
```

---

## 7. Interface Screenshots

### Start menu
<img src="../screenshots/start.jpg" width="200">

### Workout menu
<img src="../screenshots/workout.jpg" width="200">

### Nutrition calculator
<img src="../screenshots/kcal.jpg" width="200">

### Workout logs
<img src="../screenshots/logs.jpg" width="200">

### Help menu
<img src="../screenshots/help.jpg" width="200">


Example structure:

```text id="6u7vku"
project/
│
├── main.py
├── .env
├── fitness.db
└── screenshots/
    ├── start.png
    ├── workouts.png
    ├── profile.png
    └── logs.png
```
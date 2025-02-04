from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext
import json
import os

DATA_FILE = "data.json"


def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users_balance": {}, "purchase_history": {}}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("⚠ Ошибка чтения JSON, создаем пустые данные.")
        return {"users_balance": {}, "purchase_history": {}}


# Функция загрузки данных
def save_data():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"users_balance": users_balance, "purchase_history": purchase_history}, f, indent=4)
        print("✅ Данные успешно сохранены!")
    except Exception as e:
        print(f"❌ Ошибка сохранения данных: {e}")

# Загружаем данные при старте бота
data = load_data()
users_balance = data["users_balance"]
users_data = {}  # Словарь для хранения ID пользователей
purchase_history = data["purchase_history"]



print(f"📂 Файл найден? {os.path.exists(DATA_FILE)}")
print(f"📑 Содержимое перед загрузкой: {open(DATA_FILE, 'r', encoding='utf-8').read() if os.path.exists(DATA_FILE) else 'Файл отсутствует'}")


print("Загруженные данные:", data)  # Отладка

# Словарь фруктов с активными статусами и ценами
fruits = {
    "Gas": {"active": True, "price": 150, "description": "Физический Фрукт Газа."},
    "Dough": {"active": True, "price": 55, "description": "Физический Фрукт Теста."},
    "Leopard": {"active": True, "price": 70, "description": "Физический Фрукт Леопарда."},
    "T-Rex": {"active": True, "price": 30, "description": "Физический Фрукт Ти-Рекса."},
    "Spirit": {"active": True, "price": 8, "description": "Физический Фрукт Спирита."},
    "Mammoth": {"active": True, "price": 10, "description": "Физический Фрукт Мамонта."}
}


purchase_history = {}

# Администратор
ADMIN_ID = 5363826493
ADMIN_USERNAME = "@PlaySetYT"


async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    # Запоминаем ID пользователя
    if username:
        users_data[username] = user_id

    await update.message.reply_text(
        "Добро пожаловать на PlayFun!\n"
        "Это тест запуска бота на Python.\n"
        "Все команды - /help\n"
        "ДАННЫЕ ПРИ ПЕРЕЗАГРУЗКЕ БОТА ИЛИ ОБНОВЛЕНИИ НЕ СОХРАНЯЮТСЯ "
        "(перезагрузка с 00:00 до 14:25 по выходным) за поддержкой - @playrolls_playfun (TikTok) \n"
    )



# /help
async def help_command(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    help_text = (
        "Доступные команды:\n"
        "/start - Приветствие\n"
        "/help - Информация о командах\n"
        "/shop - Просмотр доступных фруктов\n"
        "/balance - Проверить баланс\n"

    )
    if update.message.from_user.id == ADMIN_ID:
        help_text += (
            "/add_balance <сумма> @username - Пополнить баланс пользователя (только для админа)\n"
            "/active <fruit_name> - Активировать фрукт (только для админа)\n"
            "/unactive <fruit_name> - Деактивировать фрукт (только для админа)\n"
            "/history @username - История покупок пользователя (только для админа)\n"
            "/m @username - Написать пользователю (только для админа)"
            "/mID @username - Получить ID пользователя (только для админа)"
        )
    await update.message.reply_text(help_text)


# /balance
async def balance(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    balance = users_balance.get(user_id, 0)
    await update.message.reply_text(f"Ваш баланс: {balance} Рублей.")
    save_data()


# /add_balance
async def add_balance(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("У вас нет прав на пополнение баланса.")
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Неправильный формат команды. Используйте: /add_balance <сумма> @username")
        return

    try:
        amount = int(args[0])
        username = args[1].replace('@', '')
        user = await context.bot.get_chat(username)
        user_id = user.id

        if user_id not in users_balance:
           users_balance[user_id] = 0
        users_balance[user_id] = users_balance.get(user_id, 0) + amount  # Добавляет сумму
        save_data()
        await update.message.reply_text(f"Баланс пользователя @{username} пополнен на {amount} Рублей.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

async def get_user_id(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("У вас нет прав для использования этой команды.")
        return

    if len(context.args) < 1:
        await update.message.reply_text("Используйте: /mID @username")
        return

    username = context.args[0].replace('@', '')

    if username in users_data:
        user_id = users_data[username]
        await update.message.reply_text(f"ID пользователя @{username}: `{user_id}`")
    else:
        await update.message.reply_text(f"Пользователь @{username} еще не писал боту.")


# Команды для активации и деактивации фруктов
async def active(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("У вас нет прав для активации фруктов.")
        return
    
    args = context.args
    if not args:
        return await update.message.reply_text("Укажите фрукт для активации.")
    
    fruit_name = args[0]
    
    if fruit_name not in fruits:
        return await update.message.reply_text(f"Фрукт с именем {fruit_name} не найден.")
    
    fruits[fruit_name]["active"] = True
    await update.message.reply_text(f"Фрукт {fruit_name} теперь активен.")


async def unactive(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("У вас нет прав для деактивации фруктов.")
        return
    
    args = context.args
    if not args:
        return await update.message.reply_text("Укажите фрукт для деактивации.")
    
    fruit_name = args[0]
    
    if fruit_name not in fruits:
        return await update.message.reply_text(f"Фрукт с именем {fruit_name} не найден.")
    
    fruits[fruit_name]["active"] = False
    await update.message.reply_text(f"Фрукт {fruit_name} теперь неактивен.")


# Обработчик выбора фрукта
async def fruits_list(update: Update, context: CallbackContext) -> None:
    keyboard = []
    available_fruits = [fruit for fruit, data in fruits.items() if data["active"]]
    
    if not available_fruits:
        return await update.message.reply_text("Нет доступных фруктов.")
    
    for fruit in available_fruits:
        keyboard.append([InlineKeyboardButton(fruit, callback_data=f"fruit_{fruit}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("PlayFun/Shop\nВыберите фрукт:", reply_markup=reply_markup)


# Обработчик выбора фрукта и оплаты
async def fruit_button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    fruit_name = query.data.split("_")[1]

    # Убедимся, что фрукт существует
    if fruit_name not in fruits:
        return await query.answer(f"Фрукт {fruit_name} не найден.")
    
    fruit = fruits[fruit_name]
    text = f"Вы выбрали фрукт: {fruit_name}\n{fruit['description']}\nЦена: {fruit['price']} Рублей."
    
    keyboard = [[InlineKeyboardButton("Подтвердить оплату", callback_data=f"pay_{fruit_name}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)


# Подтверждение оплаты
async def confirm_payment(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    action_data = query.data.split("_")
    
    if len(action_data) != 2 or action_data[0] != "pay":
        return await query.answer("Некорректное действие!")

    fruit_name = action_data[1]
    fruit = fruits.get(fruit_name)

    if not fruit or not fruit["active"]:
        return await query.edit_message_text(f"Этот фрукт {fruit_name} недоступен.")

    user_id = query.from_user.id
    balance = users_balance.get(user_id, 0)

    if balance >= fruit["price"]:
        users_balance[user_id] = users_balance.get(user_id, 0) - fruit["price"]
        
        # Добавление истории покупки
        if user_id not in purchase_history:
            purchase_history[user_id] = []
        purchase_history[user_id].append(f"Куплен фрукт {fruit_name} за {fruit['price']} Рублей.")

        save_data()  # Сохранение данных
        print(f"Покупка сохранена: {purchase_history}")  # Отладка

        # Оповещение администратора
        await context.bot.send_message(ADMIN_ID, f"Пользователь {query.from_user.id} совершил покупку: {fruit_name} за {fruit['price']} Рублей.")
        
        await query.edit_message_text(f"Вы купили фрукт {fruit_name}, с вами скоро свяжутся.")
    else:
        await query.edit_message_text(f"Недостаточно средств для покупки фрукта {fruit_name}. Баланс: {balance} Рублей.")


# Функция отправки сообщения админу
async def send_message(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("У вас нет прав на отправку сообщений.")
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Неправильный формат команды. Используйте: /m @username <сообщение>")
        return

    username = args[0].replace('@', '')
    message = " ".join(args[1:])

    try:
        user = await context.bot.get_chat(username)
        await user.send_message(message)
        await update.message.reply_text(f"Сообщение отправлено пользователю @{username}.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")


# Функция истории покупок
async def history(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("У вас нет прав для просмотра истории покупок.")
        return

    if len(context.args) < 1:
        return await update.message.reply_text("Укажите пользователя (например, @username).")
    
    username = context.args[0].replace('@', '')

    try:
        user = await context.bot.get_chat(username)
        user_id = user.id
        purchases = purchase_history.get(user_id, [])

        if not purchases:
            return await update.message.reply_text(f"У пользователя @{username} нет истории покупок.")

        # Отправляем историю покупок
        history_text = "\n".join(purchases)
        await update.message.reply_text(f"История покупок пользователя @{username}:\n{history_text}")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")


# Основная функция
def main():
    application = Application.builder().token("7773121702:AAFNl4wnM1JEPGg7XkviYCjgoHOBDJWyAdo").build()

    # Добавляем команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("shop", fruits_list))

    # Только для администратора
    application.add_handler(CommandHandler("add_balance", add_balance))
    application.add_handler(CommandHandler("active", active))
    application.add_handler(CommandHandler("unactive", unactive))
    application.add_handler(CommandHandler("history", history))
    application.add_handler(CommandHandler("m", send_message))
    application.add_handler(CommandHandler("mID", get_user_id))


    # Обработчики кнопок
    application.add_handler(CallbackQueryHandler(fruit_button, pattern="^fruit_"))
    application.add_handler(CallbackQueryHandler(fruits_list, pattern="^fruit_list$"))
    application.add_handler(CallbackQueryHandler(confirm_payment, pattern="^pay_"))

    application.run_polling()


if __name__ == "__main__":
    main()

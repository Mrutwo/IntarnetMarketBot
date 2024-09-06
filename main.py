import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import token
from logic import init_db, save_custom_question, find_similar_question, save_response, get_pending_requests, get_request_details

bot = telebot.TeleBot(token)

init_db()

LANGUAGES = {
    "ru": "Русский",
    "en": "English",
    "he": "עברית"
}

FAQ = {
    "ru": {
        "orders": [
            ("Как оформить заказ?", "Для оформления заказа выберите товар, добавьте его в корзину и следуйте инструкциям."),
            ("Как узнать статус заказа?", "Вы можете узнать статус заказа в разделе 'Мои заказы' на сайте."),
            ("Как отменить заказ?", "Свяжитесь с нашей службой поддержки для отмены заказа.")
        ],
        "delivery": [
            ("Сроки доставки", "Доставка занимает 3-5 рабочих дней."),
            ("Как отслеживать доставку?", "Вы получите трек-номер для отслеживания после отправки заказа.")
        ]
    },
    "en": {
        "orders": [
            ("How to place an order?", "To place an order, choose the product, add it to your cart, and follow the instructions."),
            ("How to check my order status?", "You can check your order status in the 'My Orders' section on the website."),
            ("How to cancel an order?", "Contact our support service to cancel your order.")
        ],
        "delivery": [
            ("Delivery times", "Delivery usually takes 3-5 business days."),
            ("How to track delivery?", "You will receive a tracking number after your order is shipped.")
        ]
    },
    "he": {
        "orders": [
            ("איך לבצע הזמנה?", "כדי לבצע הזמנה, בחרו מוצר, הוסיפו אותו לעגלה ופעלו לפי ההוראות."),
            ("איך לבדוק את מצב ההזמנה?", "ניתן לבדוק את מצב ההזמנה באזור 'ההזמנות שלי' באתר."),
            ("איך לבטל הזמנה?", "צרו קשר עם שירות הלקוחות שלנו כדי לבטל את ההזמנה.")
        ],
        "delivery": [
            ("זמני משלוח", "משלוח אורך בדרך כלל 3-5 ימי עסקים."),
            ("איך לעקוב אחר המשלוח?", "תקבלו מספר מעקב לאחר שליחת ההזמנה.")
        ]
    }
}

user_language = {}

ADMIN_ID = #id user in telegram

@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    for code, language in LANGUAGES.items():
        markup.add(InlineKeyboardButton(language, callback_data=f"lang_{code}"))
    
    bot.send_message(
        message.chat.id,"""Здраствуйте! Я бот по Тех.Потдержке Интарнет магазина 'абракадабрабимбумбам' У меня вы сможете задать вопросы по доставке и по заказам, если вам будет нужна какая либо помощь вы можете связаться с администраций!
------------------------------------------------------------------------------------------------------     
Hello! I am a bot for Technical Support of the Intarnet store 'abracadabrabimbumbam'. You can ask questions about delivery and orders from me, if you need any help, you can contact the administrations!"""
                        
    )

    bot.send_message(
        message.chat.id,
        "Выберите язык / Choose your language / בחרו שפה:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def set_language(call):
    language_code = call.data.split('_')[1]
    user_language[call.from_user.id] = language_code

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Вопросы по заказам / Order questions / שאלות על הזמנות", callback_data="orders"),
        InlineKeyboardButton("Вопросы по доставке / Delivery questions / שאלות על משלוח", callback_data="delivery"),
        InlineKeyboardButton("Другие вопросы / Other questions / שאלות אחרות", callback_data="other_questions"),
        InlineKeyboardButton("Вернуться / Return / חזור", callback_data="return_to_main")
    )

    lang_text = {
        "ru": "Выберите категорию вашего вопроса:",
        "en": "Choose your question category:",
        "he": "בחרו קטגוריה לשאלה שלכם:"
    }

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=lang_text.get(language_code, "Choose your question category:"),
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data in ["orders", "delivery", "other_questions", "return_to_main"])
def handle_category(call):
    language = user_language.get(call.from_user.id, "ru")
    if call.data in ["orders", "delivery"]:
        markup = InlineKeyboardMarkup()
        for question, _ in FAQ[language][call.data]:
            markup.add(InlineKeyboardButton(question, callback_data=f"q_{call.data}_{question}"))

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text={
                "ru": "Выберите ваш вопрос:",
                "en": "Choose your question:",
                "he": "בחרו את השאלה שלכם:"
            }.get(language, "Choose your question:"),
            reply_markup=markup
        )
    elif call.data == "other_questions":
        bot.send_message(
            call.message.chat.id,
            {
                "ru": "Введите ваш вопрос, и мы постараемся помочь вам.",
                "en": "Please type your question, and we will try to help you.",
                "he": "הקלידו את השאלה שלכם וננסה לעזור לכם."
            }.get(language, "Please type your question, and we will try to help you.")
        )
        bot.register_next_step_handler(call.message, process_custom_question)
    elif call.data == "return_to_main":
        start(call.message)

@bot.callback_query_handler(func=lambda call: call.data.startswith("q_"))
def handle_standard_question(call):
    language = user_language.get(call.from_user.id, "ru")
    category, question_text = call.data.split('_')[1], call.data.split('_')[2]
    for question, answer in FAQ[language][category]:
        if question == question_text:
            bot.send_message(call.message.chat.id, answer)
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(
                "Вернуться / Return / חזור",
                callback_data="return_to_main"
            ))
            bot.send_message(
                call.message.chat.id,
                "Что еще вам нужно?",
                reply_markup=markup
            )
            break

def process_custom_question(message):
    user_id = message.from_user.id
    username = message.from_user.username
    user_question = message.text
    language = user_language.get(user_id, "ru")

    similar_answer = find_similar_question(user_question)
    if similar_answer:
        bot.send_message(
            message.chat.id,
            similar_answer
        )
    else:
        question_id = save_custom_question(user_id, username, user_question)
        bot.send_message(
            message.chat.id,
            {
                "ru": "Ваш вопрос был отправлен на рассмотрение.",
                "en": "Your question has been submitted for review.",
                "he": "השאלה שלכם נשלחה לבדיקה."
            }.get(language, "Your question has been submitted for review.")
        )

@bot.message_handler(commands=['admin'])
def admin_command(message):
    if message.from_user.id == ADMIN_ID:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Показать ожидающие запросы", callback_data="show_pending_requests"))

        bot.send_message(
            message.chat.id,
            "Выберите действие:",
            reply_markup=markup
        )

@bot.callback_query_handler(func=lambda call: call.data == "show_pending_requests")
def show_pending_requests(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "У вас нет прав для этой команды.")
        return

    requests = get_pending_requests()
    if not requests:
        bot.send_message(call.message.chat.id, "Нет ожидающих запросов.")
        return

    text = "Ожидающие запросы:\n\n"
    for request_id, question in requests:
        text += f"Запрос ID {request_id}: {question}\n"

    markup = InlineKeyboardMarkup()
    for request_id, _ in requests:
        markup.add(InlineKeyboardButton(f"Ответить на запрос ID {request_id}", callback_data=f"respond_{request_id}"))

    bot.send_message(
        call.message.chat.id,
        text,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("respond_"))
def respond_to_request(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "У вас нет прав для этой команды.")
        return

    request_id = int(call.data.split('_')[1])
    details = get_request_details(request_id)
    if not details:
        bot.send_message(call.message.chat.id, "Запрос не найден.")
        return

    user_id, question = details
    bot.send_message(call.message.chat.id, f"Вы ответите на запрос ID {request_id}:\n\nВопрос пользователя: {question}")

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Отправить ответ", callback_data=f"send_response_{request_id}"))
    bot.send_message(
        call.message.chat.id,
        "Введите ваш ответ:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("send_response_"))
def send_response(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "У вас нет прав для этой команды.")
        return

    try:
        request_id = int(call.data.split('_')[2])
    except (IndexError, ValueError) as e:
        bot.send_message(call.message.chat.id, "Произошла ошибка при обработке запроса.")
        print(f"Ошибка: {e}, данные call.data: {call.data}")
        return

    bot.send_message(call.message.chat.id, "Пожалуйста, введите ваш ответ.")

    bot.register_next_step_handler(call.message, process_admin_response, request_id)

def process_admin_response(message, request_id):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "У вас нет прав для этого действия.")
        return

    response = message.text
    save_response(request_id, response)
    bot.send_message(message.chat.id, "Ваш ответ был отправлен пользователю.")

    request_details = get_request_details(request_id)
    if request_details:
        user_id = request_details[0]
        bot.send_message(
            user_id,
            f"Ваш запрос был обработан. Ответ: {response}"
        )

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Показать ожидающие запросы", callback_data="show_pending_requests"))

    bot.send_message(
        message.chat.id,
        "Ответ отправлен. Выберите следующее действие:",
        reply_markup=markup
    )

bot.infinity_polling()

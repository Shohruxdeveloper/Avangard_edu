from telebot import TeleBot, types
import asyncio
import pandas as pd
from datetime import datetime
import os

bot = TeleBot()  # Bot tokenini qo'shish

# Adminlar ro'yxati
main_admins = {}  # Glavniy adminlarning chat_id'lari
admins = set(main_admins)  # Adminlarning chat_id'larini o'zgartirish orzusi

# Kursga ro'yxatdan o'tgan foydalanuvchilarni malumotlarini saqlash uchun DataFrame
course_registrations_file = "course_registrations.xlsx"
if os.path.exists(course_registrations_file):
    course_registrations = pd.read_excel(course_registrations_file, engine='openpyxl')
else:
    course_registrations = pd.DataFrame(columns=["Ism", "Telefon", "Fan", "Sertifikat", "Daraja", "Ro'yxatdan o'tgan vaqti"])

# DTM testiga ro'yxatdan o'tgan foydalanuvchilarni malumotlarini saqlash uchun DataFrame
dtm_registrations_file = "dtm_test_registrations.xlsx"
if os.path.exists(dtm_registrations_file):
    dtm_registrations = pd.read_excel(dtm_registrations_file, engine='openpyxl')
else:
    dtm_registrations = pd.DataFrame(columns=["Ism", "Telefon", "Fan", "Smena", "Ro'yxatdan o'tgan vaqti"])

# Smena vaqtlarini saqlash
shifts = ["1-smena 09:00-12:00 🕘", "2-smena 13:00-16:00 🕐"]

# Foydalanuvchi tillarini saqlash
user_languages = {}

@bot.message_handler(commands=['start'])  # yangi sintaksis
def send_welcome(message: types.Message):
    if message.from_user.id in admins:
        send_main_menu(message)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("🇺🇿 O'zbek tili"), types.KeyboardButton("🇷🇺 Русский язык"))
        bot.reply_to(message, "Tilni tanlang / Выберите язык", reply_markup=markup)
        bot.register_next_step_handler(message, set_language)

def set_language(message: types.Message):
    if message.text == "🇺🇿 O'zbek tili":
        user_languages[message.from_user.id] = 'uz'
        send_main_menu(message)
    elif message.text == "🇷🇺 Русский язык":
        user_languages[message.from_user.id] = 'ru'
        send_main_menu(message)
    else:
        bot.reply_to(message, "Iltimos, tilni tanlang / Пожалуйста, выберите язык")
        bot.register_next_step_handler(message, set_language)

def send_main_menu(message: types.Message):
    lang = user_languages.get(message.from_user.id, 'uz')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if message.from_user.id in admins:
        markup.add(types.KeyboardButton("✍️ Kurslarga ro'yxatdan o'tish" if lang == 'uz' else "✍️ Записаться на курсы"))
        markup.add(types.KeyboardButton("📝 DTM testiga ro'yxatdan o'tish" if lang == 'uz' else "📝 Записаться на тест DTM"))
        markup.add(types.KeyboardButton("📍 Lokatsiya" if lang == 'uz' else "📍 Локация"))
        markup.add(types.KeyboardButton("📊 Kursga ro'yxatdan o'tgan foydalanuvchilar" if lang == 'uz' else "📊 Пользователи, зарегистрированные на курсы"))
        markup.add(types.KeyboardButton("📊 DTM testiga ro'yxatdan o'tgan foydalanuvchilar" if lang == 'uz' else "📊 Пользователи, зарегистрированные на тест DTM"))
        if message.from_user.id in main_admins:
            markup.add(types.KeyboardButton("➕ Admin qo'shish" if lang == 'uz' else "➕ Добавить админа"))
            markup.add(types.KeyboardButton("➖ Admin o'chirish" if lang == 'uz' else "➖ Удалить админа"))
            markup.add(types.KeyboardButton("👥 Adminlar ro'yxati" if lang == 'uz' else "👥 Список админов"))
    else:
        markup.add(types.KeyboardButton("✍️ Kurslarga ro'yxatdan o'tish" if lang == 'uz' else "✍️ Записаться на курсы"))
        markup.add(types.KeyboardButton("📝 DTM testiga ro'yxatdan o'tish" if lang == 'uz' else "📝 Записаться на тест DTM"))
        markup.add(types.KeyboardButton("📍 Lokatsiya" if lang == 'uz' else "📍 Локация"))
        markup.add(types.KeyboardButton("/start"))
    bot.reply_to(message, "Assalomu alaykum! Avangard Education ga xush kelibsiz." if lang == 'uz' else "Здравствуйте! Добро пожаловать в Avangard Education.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["📍 Lokatsiya", "📍 Локация"])
def send_location(message: types.Message):
    lang = user_languages.get(message.from_user.id, 'uz')
    bot.send_location(message.chat.id, 40.3824330, 71.7841710)  # O'quv markaz lokatsiyasini yuborish
    bot.reply_to(message, "Lokatsiya yuborildi. 📍" if lang == 'uz' else "Локация отправлена. 📍")

@bot.message_handler(func=lambda message: message.text in ["✍️ Kurslarga ro'yxatdan o'tish", "✍️ Записаться на курсы"])
def register_for_course(message: types.Message):
    lang = user_languages.get(message.from_user.id, 'uz')
    bot.reply_to(message, "Iltimos, ismingizni kiriting. ✍️" if lang == 'uz' else "Пожалуйста, введите ваше имя. ✍️")
    bot.register_next_step_handler(message, get_course_contact)

def get_course_contact(message: types.Message):
    if message.text == "/start":
        send_welcome(message)
        return
    lang = user_languages.get(message.from_user.id, 'uz')
    if message.text:
        name = message.text
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button = types.KeyboardButton("📞 Kontaktni yuborish" if lang == 'uz' else "📞 Отправить контакт", request_contact=True)
        markup.add(button)
        bot.reply_to(message, "Iltimos, kontaktni yuboring yoki telefon raqamingizni kiriting. 📞" if lang == 'uz' else "Пожалуйста, отправьте контакт или введите ваш номер телефона. 📞", reply_markup=markup)
        bot.register_next_step_handler(message, get_course_subject, name=name)
    else:
        bot.reply_to(message, "Iltimos, ismingizni to'g'ri kiriting. ❗" if lang == 'uz' else "Пожалуйста, введите ваше имя правильно. ❗")
        bot.register_next_step_handler(message, get_course_contact)

def get_course_subject(message: types.Message, name: str):
    if message.text == "/start":
        send_welcome(message)
        return
    lang = user_languages.get(message.from_user.id, 'uz')
    if message.contact:
        phone_number = message.contact.phone_number
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number
    elif message.text:
        phone_number = message.text
    else:
        bot.reply_to(message, "Iltimos, kontaktni yoki telefon raqamingizni to'g'ri yuboring. ❗" if lang == 'uz' else "Пожалуйста, отправьте контакт или введите ваш номер телефона правильно. ❗")
        bot.register_next_step_handler(message, get_course_contact, name=name)
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton("🔬 Kimyo"))
    markup.add(types.KeyboardButton("🌿 Biologiya"))
    markup.add(types.KeyboardButton("📚 Ona tili va adabiyoti"))
    markup.add(types.KeyboardButton("🧮 Matematika"))
    markup.add(types.KeyboardButton("🇬🇧 Ingliz tili"))
    markup.add(types.KeyboardButton("🏯 Tarix"))
    bot.reply_to(message, "Fanlardan birini tanlang: 📚", reply_markup=markup)
    bot.register_next_step_handler(message, ask_for_level, name=name, phone_number=phone_number)

def ask_for_level(message: types.Message, name: str, phone_number: str):
    if message.text == "/start":
        send_welcome(message)
        return
    lang = user_languages.get(message.from_user.id, 'uz')
    subject = message.text
    if subject == "🇬🇧 Ingliz tili":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        markup.add(types.KeyboardButton("Beginner"))
        markup.add(types.KeyboardButton("Elementary"))
        markup.add(types.KeyboardButton("Intermediate"))
        bot.reply_to(message, "Ingliz tili uchun darajangizni tanlang: 📈", reply_markup=markup)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        markup.add(types.KeyboardButton("\"0\" guruh (boshlang'ich)"))
        markup.add(types.KeyboardButton("O'qigan guruh (o'rta)"))
        markup.add(types.KeyboardButton("Sertifikat guruh (yuqori)"))
        bot.reply_to(message, f"{subject} uchun darajangizni tanlang: 📈", reply_markup=markup)
    bot.register_next_step_handler(message, confirm_registration, name=name, phone_number=phone_number, subject=subject)

def confirm_registration(message: types.Message, name: str, phone_number: str, subject: str, level: str = None):
    if message.text == "/start":
        send_welcome(message)
        return
    lang = user_languages.get(message.from_user.id, 'uz')
    if not level:
        level = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton("Ha"))
    markup.add(types.KeyboardButton("Yo'q"))
    bot.reply_to(message, f"Ism: {name}\nTelefon: {phone_number}\nFan: {subject}\nDaraja: {level}\nTo'g'rimi? ✅", reply_markup=markup)
    bot.register_next_step_handler(message, handle_confirmation_response, name=name, phone_number=phone_number, subject=subject, level=level)

def handle_confirmation_response(message: types.Message, name: str, phone_number: str, subject: str, level: str):
    if message.text == "/start":
        send_welcome(message)
        return
    lang = user_languages.get(message.from_user.id, 'uz')
    if message.text.lower() in ["ha", "да"]:
        send_course_registration_info(message, name=name, phone_number=phone_number, subject=subject, level=level)
    else:
        bot.reply_to(message, "Iltimos, ma'lumotlarni qayta kiriting. 🔄")
        register_for_course(message)

def send_course_registration_info(message: types.Message, name: str, phone_number: str, subject: str, level: str = None):
    lang = user_languages.get(message.from_user.id, 'uz')
    user_info = f"Ism: {name}\nTelefon: {phone_number}\nFan: {subject}\nDaraja: {level}" if lang == 'uz' else f"Имя: {name}\nТелефон: {phone_number}\nПредмет: {subject}\nУровень: {level}"
    for admin in admins:
        bot.send_message(chat_id=admin, text=user_info)  # Barcha adminlarga jo'natish
    bot.reply_to(message, "Muvaffaqqiyatli ro'yxatdan o'tdingiz! 🎉" if lang == 'uz' else "Вы успешно зарегистрировались! 🎉", reply_markup=types.ReplyKeyboardRemove())  # Foydalanuvchi muvaffaqqiyatli ro'yxatdan o'tganligi haqida xabar

    # Foydalanuvchi ma'lumotlarini DataFrame ga qo'shish
    global course_registrations
    registration_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    course_registrations = pd.concat([course_registrations, pd.DataFrame([{"Ism": name, "Telefon": phone_number, "Fan": subject, "Sertifikat": "Ha" if level is None else "Yo'q", "Daraja": level, "Ro'yxatdan o'tgan vaqti": registration_time}])], ignore_index=True)
    course_registrations.to_excel(course_registrations_file, index=False, engine='openpyxl')  # Excel faylga saqlash

@bot.message_handler(func=lambda message: message.text in ["📝 DTM testiga ro'yxatdan o'tish", "📝 Записаться на тест DTM"])
def register_for_dtm_test(message: types.Message):
    lang = user_languages.get(message.from_user.id, 'uz')
    bot.reply_to(message, "Iltimos, ismingizni kiriting. ✍️" if lang == 'uz' else "Пожалуйста, введите ваше имя. ✍️")
    bot.register_next_step_handler(message, get_dtm_contact)

def get_dtm_contact(message: types.Message):
    if message.text == "/start":
        send_welcome(message)
        return
    lang = user_languages.get(message.from_user.id, 'uz')
    if message.text:
        name = message.text
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button = types.KeyboardButton("📞 Kontaktni yuborish" if lang == 'uz' else "📞 Отправить контакт", request_contact=True)
        markup.add(button)
        bot.reply_to(message, "Iltimos, kontaktni yuboring yoki telefon raqamingizni kiriting. 📞" if lang == 'uz' else "Пожалуйста, отправьте контакт или введите ваш номер телефона. 📞", reply_markup=markup)
        bot.register_next_step_handler(message, get_dtm_subject1, name=name)
    else:
        bot.reply_to(message, "Iltimos, ismingizni to'g'ri kiriting. ❗" if lang == 'uz' else "Пожалуйста, введите ваше имя правильно. ❗")
        bot.register_next_step_handler(message, get_dtm_contact)

def get_dtm_subject1(message: types.Message, name: str):
    if message.text == "/start":
        send_welcome(message)
        return
    lang = user_languages.get(message.from_user.id, 'uz')
    if message.contact:
        phone_number = message.contact.phone_number
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number
    elif message.text:
        phone_number = message.text
    else:
        bot.reply_to(message, "Iltimos, kontaktni yoki telefon raqamingizni to'g'ri yuboring. ❗" if lang == 'uz' else "Пожалуйста, отправьте контакт или введите ваш номер телефона правильно. ❗")
        bot.register_next_step_handler(message, get_dtm_contact, name=name)
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton("🔬 Kimyo"))
    markup.add(types.KeyboardButton("🌿 Biologiya"))
    markup.add(types.KeyboardButton("📚 Ona tili va adabiyoti"))
    markup.add(types.KeyboardButton("🧮 Matematika"))
    markup.add(types.KeyboardButton("🇬🇧 Ingliz tili"))
    markup.add(types.KeyboardButton("🏯 Tarix"))
    bot.reply_to(message, "1-blokni tanlang (fanlardan birini tanlang): 📚", reply_markup=markup)
    bot.register_next_step_handler(message, ask_for_certificate1, name=name, phone_number=phone_number, subject1=None)

def ask_for_certificate1(message: types.Message, name: str, phone_number: str, subject1: str):
    if message.text == "/start":
        send_welcome(message)
        return
    lang = user_languages.get(message.from_user.id, 'uz')
    subject1 = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton("Ha"))
    markup.add(types.KeyboardButton("Yo'q"))
    bot.reply_to(message, f"{subject1} fanidan sertifikatingiz bormi? 📜", reply_markup=markup)
    bot.register_next_step_handler(message, handle_certificate1_response, name=name, phone_number=phone_number, subject1=subject1)

def handle_certificate1_response(message: types.Message, name: str, phone_number: str, subject1: str):
    if message.text == "/start":
        send_welcome(message)
        return
    lang = user_languages.get(message.from_user.id, 'uz')
    if message.text.lower() in ["ha", "да"]:
        level1 = "Sertifikat bor"
        bot.reply_to(message, "Sertifikatingiz bor deb saqlanadi. ✅")
        get_dtm_subject2(message, name=name, phone_number=phone_number, subject1=subject1, level1=level1)
    else:
        ask_for_level1(message, name=name, phone_number=phone_number, subject1=subject1)

def ask_for_level1(message: types.Message, name: str, phone_number: str, subject1: str):
    if message.text == "/start":
        send_welcome(message)
        return
    lang = user_languages.get(message.from_user.id, 'uz')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    if subject1 == "🇬🇧 Ingliz tili":
        markup.add(types.KeyboardButton("Beginner"))
        markup.add(types.KeyboardButton("Elementary"))
        markup.add(types.KeyboardButton("Intermediate"))
        bot.reply_to(message, "Ingliz tili uchun darajangizni tanlang: 📈", reply_markup=markup)
    else:
        markup.add(types.KeyboardButton("\"0\" guruh (boshlang'ich)"))
        markup.add(types.KeyboardButton("O'qigan guruh (o'rta)"))
        markup.add(types.KeyboardButton("Sertifikat guruh (yuqori)"))
        bot.reply_to(message, f"{subject1} uchun darajangizni tanlang: 📈", reply_markup=markup)
    bot.register_next_step_handler(message, get_dtm_subject2, name=name, phone_number=phone_number, subject1=subject1)

def get_dtm_subject2(message: types.Message, name: str, phone_number: str, subject1: str, level1: str = None):
    if message.text == "/start":
        send_welcome(message)
        return
    lang = user_languages.get(message.from_user.id, 'uz')
    if not level1:
        level1 = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton("🔬 Kimyo"))
    markup.add(types.KeyboardButton("🌿 Biologiya"))
    markup.add(types.KeyboardButton("📚 Ona tili va adabiyoti"))
    markup.add(types.KeyboardButton("🧮 Matematika"))
    markup.add(types.KeyboardButton("🇬🇧 Ingliz tili"))
    markup.add(types.KeyboardButton("🏯 Tarix"))
    bot.reply_to(message, "2-blokni tanlang (fanlardan birini tanlang): 📚", reply_markup=markup)
    bot.register_next_step_handler(message, ask_for_certificate2, name=name, phone_number=phone_number, subject1=subject1, level1=level1)

def ask_for_certificate2(message: types.Message, name: str, phone_number: str, subject1: str, level1: str):
    if message.text == "/start":
        send_welcome(message)
        return
    lang = user_languages.get(message.from_user.id, 'uz')
    subject2 = message.text
    if subject2 == subject1:
        bot.reply_to(message, "Iltimos, boshqa fan tanlang. ❗" if lang == 'uz' else "Пожалуйста, выберите другой предмет. ❗")
        get_dtm_subject2(message, name=name, phone_number=phone_number, subject1=subject1, level1=level1)
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton("Ha"))
    markup.add(types.KeyboardButton("Yo'q"))
    bot.reply_to(message, f"{subject2} fanidan sertifikatingiz bormi? 📜", reply_markup=markup)
    bot.register_next_step_handler(message, handle_certificate2_response, name=name, phone_number=phone_number, subject1=subject1, level1=level1, subject2=subject2)

def handle_certificate2_response(message: types.Message, name: str, phone_number: str, subject1: str, level1: str, subject2: str):
    if message.text == "/start":
        send_welcome(message)
        return
    lang = user_languages.get(message.from_user.id, 'uz')
    if message.text.lower() in ["ha", "да"]:
        level2 = "Sertifikat bor"
        bot.reply_to(message, "Sertifikatingiz bor deb saqlanadi. ✅")
        confirm_dtm_subjects(message, name=name, phone_number=phone_number, subject1=subject1, level1=level1, subject2=subject2, level2=level2)
    else:
        ask_for_level2(message, name=name, phone_number=phone_number, subject1=subject1, level1=level1, subject2=subject2)

def ask_for_level2(message: types.Message, name: str, phone_number: str, subject1: str, level1: str, subject2: str):
    if message.text == "/start":
        send_welcome(message)
        return
    lang = user_languages.get(message.from_user.id, 'uz')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    if subject2 == "🇬🇧 Ingliz tili":
        markup.add(types.KeyboardButton("Beginner"))
        markup.add(types.KeyboardButton("Elementary"))
        markup.add(types.KeyboardButton("Intermediate"))
        bot.reply_to(message, "Ingliz tili uchun darajangizni tanlang: 📈", reply_markup=markup)
    else:
        markup.add(types.KeyboardButton("\"0\" guruh (boshlang'ich)"))
        markup.add(types.KeyboardButton("O'qigan guruh (o'rta)"))
        markup.add(types.KeyboardButton("Sertifikat guruh (yuqori)"))
        bot.reply_to(message, f"{subject2} uchun darajangizni tanlang: 📈", reply_markup=markup)
    bot.register_next_step_handler(message, confirm_dtm_subjects, name=name, phone_number=phone_number, subject1=subject1, level1=level1, subject2=subject2)

def confirm_dtm_subjects(message: types.Message, name: str, phone_number: str, subject1: str, level1: str, subject2: str, level2: str = None):
    if message.text == "/start":
        send_welcome(message)
        return
    lang = user_languages.get(message.from_user.id, 'uz')
    if not level2:
        level2 = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton("Ha"))
    markup.add(types.KeyboardButton("Yo'q"))
    bot.reply_to(message, f"Imtihon fanlari to'g'ri tanlanganmi?\n1-blok: {subject1}\nDaraja: {level1 if level1 else 'Sertifikat bor'}\n2-blok: {subject2}\nDaraja: {level2 if level2 else 'Sertifikat bor'}\nTo'g'rimi? ✅", reply_markup=markup)
    bot.register_next_step_handler(message, get_dtm_shift, name=name, phone_number=phone_number, subject1=subject1, level1=level1, subject2=subject2, level2=level2)

def get_dtm_shift(message: types.Message, name: str, phone_number: str, subject1: str, level1: str, subject2: str, level2: str):
    if message.text == "/start":
        send_welcome(message)
        return
    lang = user_languages.get(message.from_user.id, 'uz')
    if message.text.lower() not in ["ha", "да"]:
        bot.reply_to(message, "Iltimos, ma'lumotlarni qayta kiriting. 🔄")
        register_for_dtm_test(message)
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for shift in shifts:
        markup.add(types.KeyboardButton(shift))
    bot.reply_to(message, "Iltimos, smenani tanlang. 🕘" if lang == 'uz' else "Пожалуйста, выберите смену. 🕘", reply_markup=markup)
    bot.register_next_step_handler(message, confirm_dtm_registration, name=name, phone_number=phone_number, subject1=subject1, level1=level1, subject2=subject2, level2=level2)

def confirm_dtm_registration(message: types.Message, name: str, phone_number: str, subject1: str, level1: str, subject2: str, level2: str):
    if message.text == "/start":
        send_welcome(message)
        return
    lang = user_languages.get(message.from_user.id, 'uz')
    shift = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton("Ha"))
    markup.add(types.KeyboardButton("Yo'q"))
    bot.reply_to(message, f"Ism: {name}\nTelefon: {phone_number}\n1-blok: {subject1}\nDaraja: {level1 if level1 else 'Sertifikat bor'}\n2-blok: {subject2}\nDaraja: {level2 if level2 else 'Sertifikat bor'}\nSmena: {shift}\nTo'g'rimi? ✅", reply_markup=markup)
    bot.register_next_step_handler(message, handle_dtm_confirmation_response, name=name, phone_number=phone_number, subject1=subject1, level1=level1, subject2=subject2, level2=level2, shift=shift)

def handle_dtm_confirmation_response(message: types.Message, name: str, phone_number: str, subject1: str, level1: str, subject2: str, level2: str, shift: str):
    if message.text == "/start":
        send_welcome(message)
        return
    lang = user_languages.get(message.from_user.id, 'uz')
    if message.text.lower() in ["ha", "да"]:
        send_dtm_registration_info(message, name=name, phone_number=phone_number, subject1=subject1, level1=level1, subject2=subject2, level2=level2, shift=shift)
    else:
        bot.reply_to(message, "Iltimos, ma'lumotlarni qayta kiriting. 🔄")
        register_for_dtm_test(message)

def send_dtm_registration_info(message: types.Message, name: str, phone_number: str, subject1: str, level1: str, subject2: str, level2: str, shift: str):
    lang = user_languages.get(message.from_user.id, 'uz')
    user_info = f"Ism: {name}\nTelefon: {phone_number}\n1-blok: {subject1}\nDaraja: {level1 if level1 else 'Sertifikat bor'}\n2-blok: {subject2}\nDaraja: {level2 if level2 else 'Sertifikat bor'}\nSmena: {shift}" if lang == 'uz' else f"Имя: {name}\nТелефон: {phone_number}\n1-блок: {subject1}\nУровень: {level1 if level1 else 'Сертификат бор'}\n2-блок: {subject2}\nУровень: {level2 if level2 else 'Сертификат бор'}\nСмена: {shift}"
    for admin in admins:
        bot.send_message(chat_id=admin, text=user_info)  # Barcha adminlarga jo'natish
    bot.reply_to(message, "Muvaffaqqiyatli ro'yxatdan o'tdingiz. Imtihonga vaqtida kelishingizni so'raymiz! 🎉" if lang == 'uz' else "Вы успешно зарегистрировались. Пожалуйста, приходите на экзамен вовремя! 🎉", reply_markup=types.ReplyKeyboardRemove())  # Foydalanuvchiga muvaffaqqiyatli ro'yxatdan o'tganligi haqida xabar

    # Foydalanuvchi ma'lumotlarini DataFrame ga qo'shish
    global dtm_registrations
    registration_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dtm_registrations = pd.concat([dtm_registrations, pd.DataFrame([{"Ism": name, "Telefon": phone_number, "Fan": subject1, "Daraja": level1 if level1 else 'Sertifikat bor', "Smena": shift, "Ro'yxatdan o'tgan vaqti": registration_time}])], ignore_index=True)
    dtm_registrations.to_excel(dtm_registrations_file, index=False, engine='openpyxl')  # Excel faylga saqlash

@bot.message_handler(content_types=['contact'])
def handle_contact(message: types.Message):
    if message.text == "/start":
        send_welcome(message)
        return
    lang = user_languages.get(message.from_user.id, 'uz')
    if message.contact:
        phone_number = message.contact.phone_number
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number
        bot.reply_to(message, f"Sizning kontakt raqamingiz: {phone_number} 📞" if lang == 'uz' else f"Ваш контактный номер: {phone_number} 📞")
        choose_course_subject(message, phone_number=phone_number)  # Telefon raqami bilan birga fan tanlashga o'tish
    else:
        bot.reply_to(message, "Kontakt ma'lumoti yo'q. Iltimos, kontaktni to'g'ri yuboring. ❗" if lang == 'uz' else "Контактная информация отсутствует. Пожалуйста, отправьте контакт правильно. ❗")

def choose_course_subject(message: types.Message, phone_number: str = None):
    if message.text == "/start":
        send_welcome(message)
        return
    lang = user_languages.get(message.from_user.id, 'uz')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton("🔬 Kimyo" if lang == 'uz' else "🔬 Химия"))
    markup.add(types.KeyboardButton("🌿 Biologiya" if lang == 'uz' else "🌿 Биология"))
    markup.add(types.KeyboardButton("🧮Matematika" if lang == 'uz' else "🧮Математика"))
    markup.add(types.KeyboardButton("🇺🇿 Ona tili" if lang == 'uz' else "🇺🇿 Родной язык"))
    markup.add(types.KeyboardButton("📚 Adabyot" if lang == 'uz' else "📚 Литература"))
    markup.add(types.KeyboardButton("🏯 Tarix" if lang == 'uz' else "🏯 История"))
    markup.add(types.KeyboardButton("🔬 Kimyo"))
    markup.add(types.KeyboardButton("🌿 Biologiya"))
    markup.add(types.KeyboardButton("🧮Matematika"))
    markup.add(types.KeyboardButton("🇺🇿 Ona tili"))
    markup.add(types.KeyboardButton("📚 Adabyot"))
    markup.add(types.KeyboardButton("🏯 Tarix"))
    markup.add(types.KeyboardButton("🇷🇺 Rus tili"))
    markup.add(types.KeyboardButton("🇬🇧 Ingliz tili"))
    bot.reply_to(message, "Qaysi fan orzusi? 📚", reply_markup=markup)
    bot.register_next_step_handler(message, send_course_registration_info_with_contact, phone_number=phone_number)

def send_course_registration_info_with_contact(message: types.Message, phone_number: str = None):
    if message.text == "/start":
        send_welcome(message)
        return
    if message.text in ["🔬 Kimyo", "🌿 Biologiya", "🧮Matematika", "🇺🇿 Ona tili", "📚 Adabyot", "🏯 Tarix", "🇷🇺 Rus tili", "🇬🇧 Ingliz tili"]:
        user_info = f"Ism: {message.from_user.first_name}\nTelefon: {phone_number}\nTanlangan fan: {message.text}"
        for admin in admins:
            bot.send_message(chat_id=admin, text=user_info)  # Barcha adminlarga jo'natish
        bot.reply_to(message, "Muvaffaqqiyatli ro'yxatdan o'tdingiz! 🎉", reply_markup=types.ReplyKeyboardRemove())  # Foydalanuvchiga muvaffaqqiyatli ro'yxatdan o'tganligi haqida xabar

        # Foydalanuvchi ma'lumotlarini DataFrame ga qo'shish
        global course_registrations
        registration_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        course_registrations = pd.concat([course_registrations, pd.DataFrame([{"Ism": message.from_user.first_name, "Telefon": phone_number, "Fan": message.text, "Ro'yxatdan o'tgan vaqti": registration_time}])], ignore_index=True)
        course_registrations.to_excel(course_registrations_file, index=False, engine='openpyxl')  # Excel faylga saqlash
    else:
        bot.reply_to(message, "Iltimos, kursni to'g'ri tanlang. ❗")
        bot.register_next_step_handler(message, send_course_registration_info_with_contact, phone_number=phone_number)

@bot.message_handler(func=lambda message: message.text == "➕ Admin qo'shish")
def add_admin(message: types.Message):
    if message.from_user.id in main_admins:
        bot.reply_to(message, "Iltimos, yangi adminning chat_id'sini kiriting. ➕")
        bot.register_next_step_handler(message, add_admin_to_list)
    else:
        bot.reply_to(message, "Siz glavniy admin emassiz. Admin qo'shishga ruxsat yo'q. ❌")

def add_admin_to_list(message: types.Message):
    if message.text == "/start":
        send_welcome(message)
        return
    try:
        new_admin_id = int(message.text)
        admins.add(new_admin_id)
        bot.reply_to(message, "Yangi admin muvaffaqqiyatli qo'shildi. ✅")
        admin_names = [f"{bot.get_chat(admin).first_name} ({admin})" for admin in admins]
        admin_list = "\n".join(admin_names)
        for main_admin in main_admins:
            bot.send_message(chat_id=main_admin, text=f"Yangi admin qo'shildi: {new_admin_id}\nHozirgi adminlar:\n{admin_list}")
    except ValueError:
        bot.reply_to(message, "Iltimos, to'g'ri chat_id'sini kiriting. ❗")

@bot.message_handler(func=lambda message: message.text == "➖ Admin o'chirish")
def remove_admin(message: types.Message):
    if message.from_user.id in main_admins:
        bot.reply_to(message, "Iltimos, o'chirish uchun adminning chat_id'sini kiriting. ➖")
        bot.register_next_step_handler(message, remove_admin_from_list)
    else:
        bot.reply_to(message, "Siz glavniy admin emassiz. Admin o'chirishga ruxsat yo'q. ❌")

def remove_admin_from_list(message: types.Message):
    if message.text == "/start":
        send_welcome(message)
        return
    try:
        admin_id_to_remove = int(message.text)
        admins.remove(admin_id_to_remove)
        bot.reply_to(message, "Admin muvaffaqqiyatli o'chirildi. ✅")
        admin_names = [f"{bot.get_chat(admin).first_name} ({admin})" for admin in admins]
        admin_list = "\n".join(admin_names)
        for main_admin in main_admins:
            bot.send_message(chat_id=main_admin, text=f"Admin o'chirildi: {admin_id_to_remove}\nHozirgi adminlar:\n{admin_list}")
    except ValueError:
        bot.reply_to(message, "Iltimos, to'g'ri chat_id'sini kiriting. ❗")
    except KeyError:
        bot.reply_to(message, "Kechirasiz, bizda bu admin yo'q. ❌")

@bot.message_handler(func=lambda message: message.text == "👥 Adminlar ro'yxati")
def list_admins(message: types.Message):
    if message.from_user.id in main_admins:
        admin_names = [f"{bot.get_chat(admin).first_name} (<code>{admin}</code>)" for admin in admins]
        admin_list = "\n".join(admin_names)
        bot.reply_to(message, f"Hozirgi adminlar:\n{admin_list} 👥", parse_mode='HTML')
    else:
        bot.reply_to(message, "Siz glavniy admin emassiz. Adminlar ro'yxatini ko'rishga ruxsat yo'q. ❌")

@bot.message_handler(func=lambda message: message.text == "📊 Kursga ro'yxatdan o'tgan foydalanuvchilar")
def send_course_registrations(message: types.Message):
    if message.from_user.id in admins:
        if os.path.exists(course_registrations_file):
            bot.send_document(message.chat.id, open(course_registrations_file, "rb"))
        else:
            bot.reply_to(message, "Hozircha kursga ro'yxatdan o'tgan foydalanuvchilar yo'q. 📊")
    else:
        bot.reply_to(message, "Siz admin emassiz. Ushbu faylni olishga ruxsat yo'q. ❌")

@bot.message_handler(func=lambda message: message.text == "📊 DTM testiga ro'yxatdan o'tgan foydalanuvchilar")
def send_dtm_registrations(message: types.Message):
    if message.from_user.id in admins:
        if os.path.exists(dtm_registrations_file):
            bot.send_document(message.chat.id, open(dtm_registrations_file, "rb"))
        else:
            bot.reply_to(message, "Hozircha DTM testiga ro'yxatdan o'tgan foydalanuvchilar yo'q.")
    else:
        bot.reply_to(message, "Siz admin emassiz. Ushbu faylni olishga ruxsat yo'q.")

@bot.message_handler(func=lambda message: True)  # Har qanday xabarni ushlash
def handle_all_messages(message: types.Message):
    send_welcome(message)  # Har qanday xabar kelganda start tugmasini ko'rsatish

if __name__ == '__main__':
    try:
        bot.infinity_polling()  # infinity_polling() methodini ishlatish
    except Exception as e:
        print(f"An error occurred: {e}")  # xatolarni ustida ishlaydi

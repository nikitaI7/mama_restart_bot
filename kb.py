from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove

menu = [
    [InlineKeyboardButton(text="📝 Добавить индивидуальный код", callback_data="add_code")],
    [InlineKeyboardButton(text="🖼 Ввести код активации", callback_data="add_me")],
    [InlineKeyboardButton(text="Купить курс", callback_data='3_courses')],
    [InlineKeyboardButton(text="Попробовать бесплатно", callback_data="free_course")],
    [InlineKeyboardButton(text="Cлужба поддержки", callback_data="sos")],
]

tryy = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🖼 Ввести код активации", callback_data="add_me")]])

menu = InlineKeyboardMarkup(inline_keyboard=menu)
exit_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="◀️ Выйти в меню")]], resize_keyboard=True)
iexit_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]])

start = [
    [InlineKeyboardButton(text="Начать курс", callback_data="start_course")],
    [InlineKeyboardButton(text="Отписаться от курса", callback_data="unsubscribe")],
]

keyboard_start = InlineKeyboardMarkup(inline_keyboard=start)

start_free = [
    [InlineKeyboardButton(text="Начать", callback_data="start_free_course")],
    [InlineKeyboardButton(text="Узнать об ограничениях", callback_data="about_limitations")],
    [InlineKeyboardButton(text="Вернуться назад", callback_data="menu")]# Добавленная кнопка
]

keyboard_start_free = InlineKeyboardMarkup(inline_keyboard=start_free)

end_free = [
    [InlineKeyboardButton(text="Завершить тренировку", callback_data="end_free_course")],
    [InlineKeyboardButton(text="Вернуться назад", callback_data="free_course")],
]

keyboard_end_free = InlineKeyboardMarkup(inline_keyboard=end_free)

step_3_courses = [
    [InlineKeyboardButton(text="Продолжить восстановление", callback_data="3_courses")],
    [InlineKeyboardButton(text="Вернуться назад", callback_data="start_free_course")],
]

keyboard_step_3_courses = InlineKeyboardMarkup(inline_keyboard=step_3_courses)

about_3_courses = [
    [InlineKeyboardButton(text="Базовый тариф", callback_data="basic")],
    [InlineKeyboardButton(text="Стандартный тариф", callback_data="standart")],
    [InlineKeyboardButton(text="Тариф Люкс", callback_data="luxe")],
    [InlineKeyboardButton(text="Вернуться в меню", callback_data="menu")]
]

keyboard_about_3_courses = InlineKeyboardMarkup(inline_keyboard=about_3_courses)

base = [
    [InlineKeyboardButton(text="Приобрести Базовый тариф", callback_data="basic_buy")],
    [InlineKeyboardButton(text="Выбрать другой тариф", callback_data="3_courses")],
]

keyboard_base = InlineKeyboardMarkup(inline_keyboard=base)

simple = [
    [InlineKeyboardButton(text="Приобрести Стандартный тариф", callback_data="standart_buy")],
    [InlineKeyboardButton(text="Выбрать другой тариф", callback_data="3_courses")],
]

keyboard_simple = InlineKeyboardMarkup(inline_keyboard=simple)

luxury = [
    [InlineKeyboardButton(text="Приобрести тариф Люкс", callback_data="luxury_buy")],
    [InlineKeyboardButton(text="Выбрать другой тариф", callback_data="3_courses")],
]

keyboard_luxury = InlineKeyboardMarkup(inline_keyboard=luxury)

end_leaf_1 = [
    [InlineKeyboardButton(text="Перейти к вводу индивидуального кода", callback_data="add_me")],
    [InlineKeyboardButton(text="Вернуться к выбору тарифа", callback_data="3_courses")],
]
keyboard_end_leaf_1 = InlineKeyboardMarkup(inline_keyboard=end_leaf_1)

first_day = [
    [InlineKeyboardButton(text="Перейти к вводу индивидуального кода", callback_data="add_me")],
    [InlineKeyboardButton(text="Вернуться к выбору тарифа", callback_data="3_courses")],
]
keyboard_end_leaf_1 = InlineKeyboardMarkup(inline_keyboard=end_leaf_1)

start_1 = [
    [InlineKeyboardButton(text="Поменять время отправки видео", callback_data="start_course_1")],
    [InlineKeyboardButton(text="Отписаться от курса", callback_data="unsubscribe")],
    [InlineKeyboardButton(text="Вернуться в меню", callback_data="menu")]
]

start_course_1 = InlineKeyboardMarkup(inline_keyboard=start_1)

start_new = [
    [InlineKeyboardButton(text="Начать курс", callback_data="start_course")],
    [InlineKeyboardButton(text="Отписаться от курса", callback_data="unsubscribe")],
]

keyboard_start_new = InlineKeyboardMarkup(inline_keyboard=start_new)

cho = [
    [InlineKeyboardButton(text="Написать чат боту", callback_data="chat_bot")],
    [InlineKeyboardButton(text="Чат с оператором", callback_data="operator")],
    [InlineKeyboardButton(text="Чат с оператором Whats app", callback_data="whatsapp")],
    [InlineKeyboardButton(text="Вернуться в меню", callback_data="menu")],
]
choice = InlineKeyboardMarkup(inline_keyboard=cho)


inactive_start = [
    [InlineKeyboardButton(text="Начать курс (активировано)", callback_data="course_started")],
    [InlineKeyboardButton(text="Отписаться от курса", callback_data="unsubscribe")],
    [InlineKeyboardButton(text="Вернуться в меню", callback_data="menu")]
]

keyboard_inactive_start = InlineKeyboardMarkup(inline_keyboard=inactive_start)

go_back = [
[InlineKeyboardButton(text="Начать", callback_data="start_free_course")],
    [InlineKeyboardButton(text="Вернуться назад", callback_data="free_course")],
]
keyboard_go_back = InlineKeyboardMarkup(inline_keyboard=go_back)

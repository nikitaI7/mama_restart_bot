import asyncpg
import datetime
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery

import db
import kb

router = Router()
storage = MemoryStorage()


class Form(StatesGroup):
    adding_code = State()
    adding_individual_code = State()
    setting_time = State()
    setting_time_1 = State()


@router.message(Command("start"))
async def start_handler(msg: Message):
    user_name = msg.from_user.first_name

    # Формируем приветственное сообщение с использованием имени
    caption = (
        f"Добро пожаловать, {user_name}!\n\n"
        "Этот бот создан специально для поддержки женщин во время беременности и послеродового восстановления. "
        "Вы можете выбрать различные тарифы, которые включают уникальные программы тренировок, рекомендации по питанию, "
        "лекции от специалистов, а также персональные консультации с автором курса — Еленой Сорокотягиной.\n\n"
        "Выберите необходимый раздел в меню ниже, чтобы начать свой путь к здоровому и счастливому материнству."
    )
    await msg.answer(text=caption, reply_markup=kb.menu)


@router.callback_query(F.data == "menu")
async def add_code_handler(callback_query: CallbackQuery, state: FSMContext):
    user_name = callback_query.from_user.first_name
    caption = (
        f"Добро пожаловать, {user_name}!\n\n"
        "Этот бот создан специально для поддержки женщин во время беременности и послеродового восстановления. "
        "Вы можете выбрать различные тарифы, которые включают уникальные программы тренировок, рекомендации по питанию, "
        "лекции от специалистов, а также персональные консультации с автором курса — Еленой Сорокотягиной.\n\n"
        "Выберите необходимый раздел в меню ниже, чтобы начать свой путь к здоровому и счастливому материнству."
    )
    await callback_query.message.answer(text=caption,
                                        reply_markup=kb.menu)
    await callback_query.answer()


@router.message(F.text.in_(["Меню", "Выйти в меню", "◀️ Выйти в меню"]))
async def menu(msg: Message):
    user_name = msg.from_user.first_name
    caption = (
        f"Добро пожаловать, {user_name}!\n\n"
        "Этот бот создан специально для поддержки женщин во время беременности и послеродового восстановления. "
        "Вы можете выбрать различные тарифы, которые включают уникальные программы тренировок, рекомендации по питанию, "
        "лекции от специалистов, а также персональные консультации с автором курса — Еленой Сорокотягиной.\n\n"
        "Выберите необходимый раздел в меню ниже, чтобы начать свой путь к здоровому и счастливому материнству."
    )
    await msg.answer(caption=caption, reply_markup=kb.menu)


@router.callback_query(F.data == "add_code")
async def add_code_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите ваш индивидуальный код:")
    await state.set_state(Form.adding_individual_code)
    await callback_query.answer()


@router.message(Form.adding_individual_code)
async def process_individual_code_add(msg: Message, state: FSMContext):
    individual_code = msg.text.strip()
    await db.add_individual_code(individual_code)
    await msg.answer("Ваш индивидуальный код был добавлен в базу данных.", reply_markup=kb.menu)
    await state.clear()


@router.callback_query(F.data == "add_me")
async def request_individual_code(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if await db.user_has_access(user_id):
        caption = "У вас есть доступ к курсу! Видео будут приходить к вам в указанное вами время по поясу МСК (+3 GMT) "
        await callback_query.message.answer(text=caption, reply_markup=kb.start_course_1)
        await callback_query.answer()
    else:
        await callback_query.message.answer("Введите ваш индивидуальный код:")
        await state.set_state(Form.adding_code)
        await callback_query.answer()


@router.message(Form.adding_code)
async def handle_individual_code_add(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    individual_code = msg.text.strip()
    print(individual_code)
    if await db.check_individual_code(individual_code):
        level = await db.get_level_1(individual_code)
        await db.add_user_id(user_id)
        await db.add_code_added_date(user_id, datetime.datetime.now())
        await db.add_level(level, user_id)
        await db.delete_individual_code(individual_code)  # Удаление индивидуального кода
        await msg.answer("Ваш ID был добавлен. У вас теперь есть доступ к курсу.", reply_markup=kb.keyboard_start)
    else:
        await msg.answer("Неверный индивидуальный код. Пожалуйста, попробуйте еще раз.", reply_markup=kb.tryy)
    await state.clear()


@router.callback_query(F.data == "start_course")
async def start_course_handler(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id

    # Отправляем пользователю сообщение о начале курса
    await callback_query.message.answer(
        "Введите время (в формате ЧЧ:ММ) по поясу МСК (+3 GMT), когда вы хотите получать новое видео.",
        reply_markup=types.ReplyKeyboardRemove()
    )

    # Отправляем обновленное сообщение с неактивной кнопкой
    await callback_query.message.edit_reply_markup(reply_markup=kb.keyboard_inactive_start)

    # Устанавливаем состояние для дальнейшего ожидания времени
    await state.set_state(Form.setting_time)
    await callback_query.answer()


@router.callback_query(F.data == "start_course_1")
async def start_course_handler(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if await db.user_has_access(user_id):
        # Спросить у пользователя, когда он хочет получать видео
        await callback_query.message.answer("Введите время (в формате ЧЧ:ММ) по поясу МСК (+3 GMT), когда вы хотите получать новое видео.")
        await state.set_state(Form.setting_time_1)
        await callback_query.answer()
    else:
        await callback_query.message.answer("У вас нет доступа к курсу")
        await callback_query.answer()


@router.message(Form.setting_time_1)
async def set_time(message: Message, state: FSMContext):
    time_str = message.text.strip()

    # Проверка формата времени
    try:
        datetime.datetime.strptime(time_str, "%H:%M")
    except ValueError:
        await message.answer("Неверный формат времени. Пожалуйста, введите время в формате ЧЧ:ММ по поясу МСК (+3 GMT).",
                             reply_markup=kb.start_course_1)
        return

    user_id = message.from_user.id

    try:
        await db.update_user_video_time_1(user_id, time_str)
        await message.answer(
            "Время для получения видео установлено. Мы будем отправлять вам новое видео каждый день в это время по поясу МСК (+3 GMT).",
            reply_markup=kb.start_course_1)
    except asyncpg.PostgresError as e:
        # Ловим ошибки связанные с базой данных
        await message.answer("Произошла ошибка при обновлении времени. Попробуйте снова.",
                             reply_markup=kb.start_course_1)
        print(f"Database error: {e}")

    await state.clear()


@router.message(Form.setting_time)
async def set_time(message: Message, state: FSMContext):
    time_str = message.text.strip()

    # Проверка формата времени
    try:
        datetime.datetime.strptime(time_str, "%H:%M")
    except ValueError:
        await message.answer("Неверный формат времени. Пожалуйста, введите время в формате ЧЧ:ММ. по поясу МСК (+3 GMT)")
        return

    user_id = message.from_user.id

    try:
        await db.update_user_video_time(user_id, time_str)
        await message.answer(
            "Время для получения видео установлено. Мы будем отправлять вам новое видео каждый день в это время по поясу МСК (+3 GMT).")
    except asyncpg.PostgresError as e:
        # Ловим ошибки связанные с базой данных
        await message.answer("Произошла ошибка при обновлении времени. Попробуйте снова.", reply_markup=kb.start_course)
        print(f"Database error: {e}")

    await state.clear()


@router.callback_query(F.data == "unsubscribe")
async def unsubscribe_handler(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    await db.delete_user_id(user_id)
    await callback_query.answer("Вы успешно отписались от курса.")


@router.callback_query(F.data == "free_course")
async def request_individual_code(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Вам доступна пробная версия курса, но мы рекомендуем узнать об ограничениях",
                                        reply_markup=kb.keyboard_start_free)
    await state.set_state(Form.adding_code)
    await callback_query.answer()


@router.callback_query(F.data == "start_free_course")
async def start_course_handler(callback_query: CallbackQuery):
    bot = callback_query.bot
    path = 'BAACAgIAAxkBAAIEMGavAAEwY5Bt8YeRzwW13VD2KYScZgAC1F8AAhMbeUkzvog4Evo92jUE'
    caption = ('Приветствуем вас в первой тренировке нашей программы восстановления! Сегодня мы проведем диагностику '
               'диастаза и проверим правильность дыхания. При диастазе в первую очередь важно работать с мышцами '
               'живота. Благодаря тренировке вы научитесь контролю и подготовите свое тело к уходу за малышом и '
               'бытовым хлопотам! Эти упражнения помогут понять, как активировать мышцы тазового дна (МТД) и '
               'диафрагму. Выполните дыхательный тест и оцените состояние мышц своего живота. Каждое упражнение – это '
               'шаг к восстановлению вашего тела после родов.  Вы уже сделали первый шаг, значит вы на правильном '
               'пути! У вас обязательно все получится!')
    await bot.send_document(callback_query.from_user.id, f'{path}', caption=caption,
                            reply_markup=kb.keyboard_end_free,
                            protect_content=True)
    await callback_query.answer()


@router.callback_query(F.data == "end_free_course")
async def start_course_handler(callback_query: CallbackQuery):
    caption = "Поздравляем с завершением 1 тренировки! Для продолжения необходимо выбрать тариф"
    await callback_query.message.answer(text=caption, reply_markup=kb.keyboard_step_3_courses)
    await callback_query.answer()


@router.callback_query(F.data == "3_courses")
async def start_course_handler(callback_query: CallbackQuery):
    caption = ("Разрабатывая курс, мы учли большинство проблем, с которым сталкиваются женщины в первые месяцы после "
               "родов, и подготовили различные упражнения для улучшения самочувствия. Курс проходит в формате "
               "челленджа, где мы работаем над восстановлением здоровья, красоты и эмоционального состояния для "
               "полноценной и счастливой жизни. Вам доступны следующие тарифы")

    await callback_query.message.answer(text=caption, reply_markup=kb.keyboard_about_3_courses)
    await callback_query.answer()


@router.callback_query(F.data == "basic")
async def start_course_handler(callback_query: CallbackQuery):
    caption = (
        "В тариф «Базовый»‎ входит:\n\n"
        "- 7 дней челленджа\n"
        "- Тренировка и советы каждый день\n"
        "- Рекомендации по питанию и меню блюд 20 штук\n"
        "- Трекер тренировок\n"
        "- Лекция по грудному вскармливанию\n"
        "- Лекция гинеколога\n\n"
        "Стоимость тарифа: 2 000 рублей\n"
        "Доступ к курсу откроется сразу после оплаты и будет доступен 90 дней."
    )
    await callback_query.message.answer(text=caption, reply_markup=kb.keyboard_base)
    await callback_query.answer()


@router.callback_query(F.data == "standart")
async def start_course_handler(callback_query: CallbackQuery):
    caption = (
        "В тариф «Стандарт»‎ входит:\n\n"
        "- 30 дней челленджа\n"
        "- Тренировка и советы каждый день\n"
        "- Рекомендации по питанию и меню 50 блюд\n"
        "- Трекер тренировок\n"
        "- Лекция по грудному вскармливанию\n"
        "- Лекция гинеколога\n"
        "- Лекция доулы\n"
        "- Лекция сексолога\n"
        "- 2 бонусные тренировки\n\n"
        "Стоимость тарифа: 7 000 рублей\n"
        "Доступ к курсу откроется сразу после оплаты и будет доступен 90 дней."
    )

    await callback_query.message.answer(text=caption, reply_markup=kb.keyboard_simple)
    await callback_query.answer()


@router.callback_query(F.data == "luxe")
async def start_course_handler(callback_query: CallbackQuery):
    caption = (
        "В тариф «Люкс»‎ входит:\n\n"
        "- 30 дней челленджа\n"
        "- Тренировка и советы каждый день\n"
        "- Рекомендации по питанию и меню 50 блюд\n"
        "- Трекер тренировок\n"
        "- Лекция по грудному вскармливанию\n"
        "- Лекция гинеколога\n"
        "- Лекция доулы\n"
        "- Лекция сексолога\n"
        "- 2 бонусные тренировки\n"
        "- 4 персональные консультации с автором курса — Еленой Сорокотягиной\n\n"
        "Стоимость тарифа: 30 000 рублей\n"
        "Доступ к курсу откроется сразу после оплаты и будет доступен 90 дней."
    )
    await callback_query.message.answer(text=caption, reply_markup=kb.keyboard_luxury)
    await callback_query.answer()


@router.callback_query(F.data == "basic_buy")
async def start_course_handler(callback_query: CallbackQuery):
    caption = "Ссылка: https:/apple.com"
    await callback_query.message.answer(text=caption, reply_markup=kb.keyboard_end_leaf_1)
    await callback_query.answer()


@router.callback_query(F.data == "standart_buy")
async def start_course_handler(callback_query: CallbackQuery):
    caption = "Ссылка: https:/apple.com"
    await callback_query.message.answer(text=caption, reply_markup=kb.keyboard_end_leaf_1)
    await callback_query.answer()


@router.callback_query(F.data == "luxury_buy")
async def start_course_handler(callback_query: CallbackQuery):
    caption = "Ссылка: https:/apple.com"
    await callback_query.message.answer(text=caption, reply_markup=kb.keyboard_end_leaf_1)
    await callback_query.answer()


@router.callback_query(F.data == "sos")
async def start_course_handler(callback_query: CallbackQuery):
    caption = "Выберите в какой отдел вы хотите обратиться"
    await callback_query.message.answer(text=caption, reply_markup=kb.choice)
    await callback_query.answer()


@router.callback_query(F.data == "chat_bot")
async def start_course_handler(callback_query: CallbackQuery):
    caption = "Cсылка на чат бота"
    await callback_query.message.answer(text=caption, reply_markup=kb.exit_kb)
    await callback_query.answer()


@router.callback_query(F.data == "operator")
async def start_course_handler(callback_query: CallbackQuery):
    caption = "Cсылка на оператора: "
    await callback_query.message.answer(text=caption, reply_markup=kb.exit_kb)
    await callback_query.answer()


@router.callback_query(F.data == "whatsapp")
async def start_course_handler(callback_query: CallbackQuery):
    caption = "Cсылка на оператора в ватсапе: "
    await callback_query.message.answer(text=caption, reply_markup=kb.exit_kb)
    await callback_query.answer()


@router.callback_query(F.data == "about_limitations")
async def start_course_handler(callback_query: CallbackQuery):
    caption = (
        "Наш курс идеально подходит для каждой девушки, но подходящее время для старта занятий определяется "
        "индивидуально. Важно помнить, что индивидуальные особенности организма и процесс восстановления после родов "
        "могут влиять на сроки возвращения к фитнесу. Проконсультируйтесь с врачом и убедитесь, что состояние "
        "здоровья позволяет приступить к занятиям фитнесом.\n\n"
        "- Основные ограничения:\n\n"
        "- После естественных родов должно пройти более 3 дней.\n"
        "- После кесарева сечения должно пройти не менее 2 недель.\n"
        "- Наличие диастаза более 2 см.\n"
    )
    await callback_query.message.answer(text=caption, reply_markup=kb.keyboard_go_back)
    await callback_query.answer()

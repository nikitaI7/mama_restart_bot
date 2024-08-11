import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import datetime
import config
from handlers import router
import db
import kb
import aiohttp


async def fetch_with_retries(session, url, retries=5, timeout=1800):
    for attempt in range(retries):
        try:
            async with session.get(url, timeout=timeout) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    logging.error(f"Failed to download file. Status: {response.status}")
        except aiohttp.ClientError as e:
            logging.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
    raise Exception("Max retries exceeded")


async def get_file_download_link(path: str) -> str:
    file_path = await db.get_path(path)
    logging.info(f"File path from DB: {file_path}")
    return file_path


async def get_caption(path: str) -> str:
    caption = await db.get_caption(path)
    logging.info(f"File caption from DB: {caption}")
    return caption


async def has_90_days_passed(user_id: int) -> bool:
    code_added_date = await db.get_code_added_date(user_id)
    if code_added_date:
        days_passed = (datetime.datetime.now() - code_added_date).days
        return days_passed >= 90
    return False


async def send_video(bot: Bot, user_id: int, video_path: str):
    try:
        level = await db.get_level(user_id)
        number_of_videos = 7
        if level == 'Стандарт' or level == 'Люкс':
            number_of_videos = 30
        else:
            number_of_videos = 7
        print(number_of_videos)

        if int(video_path) <= number_of_videos:
            path = await get_file_download_link(video_path)
            caption = await get_caption(video_path)
            pre_train = 'BAACAgIAAxkBAAIEL2au_y9JSGqF6XrAYrb3knLbOoK3AALPXwACExt5SRTKhuatp0RYNQQ'
            message = await bot.send_document(user_id, f'{pre_train}', caption=f'Разминка!',
                                              protect_content=True)
            await db.add_message_record(user_id, message.message_id, 'video')

            message = await bot.send_document(user_id, f'{path}', caption=f'{caption}', reply_markup=kb.start_course_1,
                                              protect_content=True)
            await db.add_message_record(user_id, message.message_id, 'video')
            await db.update_path(user_id)
        else:
            congratulated = await db.is_congratulated(user_id)
            if not congratulated:
                await bot.send_message(user_id, "Поздравляем вас с прохождением курса!")
                await db.mark_congratulated(user_id)

    except Exception as e:
        logging.error(f"{e}")


async def daily_video_sender(bot: Bot):
    while True:
        now = datetime.datetime.now().strftime("%H:%M")

        try:
            users = await db.get_users_for_video(now)
        except Exception as e:
            logging.error(f"Error fetching users for video: {e}")
            await asyncio.sleep(60)
            continue

        for user in users:
            user_id = user[0]
            user_path = int(user[2])

            logging.info(f"Processing user {user_id} for video from path {user_path}")

            try:
                if await has_90_days_passed(user_id):
                    logging.info(
                        f"User {user_id} has not completed the course (90 days passed). Deleting video time, clearing "
                        f"messages, and notifying user...")
                    await db.delete_video_time(user_id)
                    await db.delete_user_messages(bot, user_id)
                    await bot.send_message(user_id, "Период действия вашего индивидуального кода истек.")
                    continue

                await send_video(bot, user_id, user_path)

            except Exception as e:
                logging.error(f"Error processing user {user_id}: {e}")

        await asyncio.sleep(60)


async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    db_pool = await db.create_pool()
    bot.db_pool = db_pool
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(daily_video_sender(bot))

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

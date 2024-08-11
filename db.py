from typing import Optional
import aiomysql
import config
import datetime
import logging
from aiogram import Bot, Dispatcher


async def create_pool():
    global db_pool
    db_pool = await aiomysql.create_pool(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USERNAME,
        password=config.DB_PASSWORD,
        db=config.DB_DATABASE,
        minsize=1,  # Установите минимальный размер пула подключений
        maxsize=100  # Установите максимальный размер пула подключений
    )
    return db_pool


async def query(sql, *params, ret=True):
    async with db_pool.acquire() as conn:  # type: aiomysql.Connection
        async with conn.cursor() as cursor:  # type: aiomysql.Cursor
            await cursor.execute(sql, params)
            if ret:
                res = await cursor.fetchall()
        await conn.commit()
        if ret:
            return res


async def get_users_for_video(current_time):
    sql = """
        SELECT ids, video_time, paths
        FROM mama_restart_bot_user_ids
        WHERE video_time = %s
        """
    users = await query(sql, current_time)
    # Todo
    print(users)
    return users


async def get_path(key: str):
    sql = """
        SELECT path
        FROM mama_restart_bot_videos mrbv
	    WHERE mrbv.key = %s;
	    """
    result = await query(sql, key)
    try:
        return result[0][0]
    except IndexError:
        return None


async def get_level(id: int):
    sql = """
    SELECT level
            FROM mama_restart_bot_user_ids
            WHERE ids = %s
            """
    result = await query(sql, id)

    try:
        return result[0][0]
    except IndexError:
        return None


async def is_congratulated(user_id: int) -> bool:
    sql = "SELECT congratulated FROM mama_restart_bot_user_ids WHERE ids = %s"
    result = await query(sql, str(user_id))

    try:
        return result[0][0] is True
    except IndexError:
        return False


async def add_code_added_date(user_id, date):
    print(date, user_id)
    sql = f"UPDATE mama_restart_bot_user_ids SET code_added_date = %s WHERE ids = %s"
    await query(sql, date, user_id)


async def add_level(level, user_id: int):
    await query("UPDATE mama_restart_bot_user_ids SET level = %s WHERE ids = %s", level, user_id, ret=False)


async def get_code_added_date(user_id: int):
    res = await query("SELECT code_added_date FROM mama_restart_bot_user_ids WHERE ids = %s", user_id)
    print(res)
    try:
        return res[0][0]
    except IndexError:
        return None


async def delete_video_time(user_id: int):
    await query('UPDATE mama_restart_bot_user_ids SET video_time = NULL WHERE ids = %s', user_id)


async def mark_congratulated(user_id: int):
    await query('UPDATE mama_restart_bot_user_ids SET congratulated = TRUE WHERE ids = %s', user_id)


async def add_message_record(user_id: int, message_id: int, message_type: str):
    await query('INSERT INTO mama_restart_bot_user_messages (user_id, message_id, message_type) VALUES (%s,%s,%s)',
                user_id, message_id, message_type)


async def delete_user_messages(bot: "Bot", user_id: int):
    try:
        # Получаем все сообщения типа 'video'
        message_ids = await query(
            'SELECT message_id FROM mama_restart_bot_user_messages WHERE user_id = (%s) AND message_type = (%s)',
            user_id, 'video')

        for message_id in message_ids:
            await bot.delete_message(chat_id=user_id, message_id=message_id)
        # Удаляем записи из базы данных
        await query('DELETE FROM mama_restart_bot_user_messages WHERE user_id = (%s) AND message_type = (%s)', user_id,
                    'video')
    except Exception as e:
        logging.error(f"Error deleting messages for user {user_id}: {e}")


async def get_caption(key: str):
    result = await query("SELECT captions FROM mama_restart_bot_videos qq WHERE qq.key = %s", key)

    try:
        return result[0][0]
    except IndexError:
        return None


async def update_path(user_id: int):
    sql = """
    UPDATE mama_restart_bot_user_ids 
SET paths = CAST(CAST(paths AS UNSIGNED) + 1 AS CHAR) 
WHERE ids = %s;
    """
    await query(
        #"UPDATE mama_restart_bot_user_ids SET paths = CAST(CAST(paths AS INTEGER) + 1 AS TEXT) WHERE ids = %s",
        sql, user_id)


async def add_user_id(user_id):
    await query("INSERT INTO mama_restart_bot_user_ids (ids) VALUES (%s) ON DUPLICATE KEY UPDATE ids = ids", user_id)


async def get_level_1(key: str):
    sql = """
        SELECT level
                FROM mama_restart_bot_myuser
                WHERE individual_codes = %s
                """
    result = await query(sql, str(key))

    try:
        return result[0][0]
    except IndexError:
        return None


async def update_user_video_time(user_id: int, time_str: str):
    time_obj = datetime.datetime.strptime(time_str, "%H:%M").time()
    sql = """
                UPDATE mama_restart_bot_user_ids
                SET video_time = %s, paths = 1
                WHERE ids = %s
                            """
    await query(sql, time_obj, user_id)


async def update_user_video_time_1(user_id: int, time_str: str):
    time_obj = datetime.datetime.strptime(time_str, "%H:%M").time()
    sql = """
                    UPDATE mama_restart_bot_user_ids
                    SET video_time = %s
                    WHERE ids = %s
                                """
    await query(sql, time_obj, user_id)


async def delete_individual_code(individual_code):
    sql = """DELETE FROM mama_restart_bot_myuser WHERE individual_codes = %s """
    await query(sql, individual_code)


async def check_individual_code(individual_code):
    sql = """SELECT COUNT(*) FROM mama_restart_bot_myuser WHERE individual_codes = %s """
    try:
        result = await query(sql, individual_code)
        return result[0][0] > 0

    except IndexError:
        return False


async def add_individual_code(individual_code):
    sql = """INSERT INTO mama_restart_bot_myuser (individual_codes) VALUES (%s) ON DUPLICATE KEY UPDATE 
    individual_codes = individual_codes"""
    await query(sql, individual_code)


async def user_has_access(user_id):
    sql = """SELECT COUNT(*) FROM mama_restart_bot_user_ids WHERE ids = %s"""
    try:
        result = await query(sql, user_id)
        return result[0][0] > 0
    except IndexError:
        return False


async def delete_user_id(user_id):
    sql = """DELETE FROM mama_restart_bot_user_ids WHERE ids = %s """
    await query(sql, user_id)

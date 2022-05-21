import aiosqlite

DB_PATH = 'sqlite.db'


async def create_all(*args):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("CREATE TABLE IF NOT EXISTS likes (msg_id INT, user_id INT, author TEXT)")
        await db.execute("CREATE TABLE IF NOT EXISTS settings (chat_id INT, result_message_id INT)")
        await db.commit()


async def get_count(msg_id) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        result = await db.execute_fetchall("SELECT count(*) FROM likes WHERE msg_id = ?", [msg_id])
        if result:
            return result[0][0]
    return 0


async def get_result_list() -> list[tuple[str, int]]:
    async with aiosqlite.connect(DB_PATH) as db:
        return await db.execute_fetchall(
            "SELECT author, count(*) as like_count FROM likes GROUP BY author ORDER BY like_count LIMIT 10 "
        )


async def update_log(msg_id: int, user_id: int, author: str):
    async with aiosqlite.connect(DB_PATH) as db:
        result = await db.execute_fetchall("SELECT * FROM likes WHERE msg_id = ? AND user_id = ?", [msg_id, user_id])
        if result:
            await db.execute("DELETE FROM likes WHERE msg_id = ? AND user_id = ?", [msg_id, user_id])
        else:
            await db.execute("INSERT INTO likes VALUES (?, ?, ?)", [msg_id, user_id, author])
        await db.commit()


async def get_settings() -> tuple[int, int] | None:
    async with aiosqlite.connect(DB_PATH) as db:
        result = await db.execute_fetchall("SELECT * FROM settings")
    if result:
        return result[0]


async def update_settings(chat_id: int, message_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO settings VALUES (?, ?)", [chat_id, message_id])
        await db.commit()

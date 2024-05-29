import sqlite3


# создать базу
_connection = None
def get_connection():
    global _connection
    if _connection == None:
        _connection = sqlite3.connect('garant_bot.db', check_same_thread=False)
    return _connection

def init_db(force: bool = False):
    conn = get_connection()
    c = conn.cursor()
    if force:
        c.execute('DROP TABLE IF EXISTS Users')
        c.execute('DROP TABLE IF EXISTS Meetings')
        c.execute('DROP TABLE IF EXISTS Messages')

    c. execute("""
    CREATE TABLE IF NOT EXISTS Users(
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        his_meeting TEXT
    )""")

    c.execute("""
        CREATE TABLE IF NOT EXISTS Meetings(
            id INTEGER PRIMARY KEY,
            id_meeting TEXT,
            first_member INT,
            second_member INT,
            meeting_url TEXT,
            admin_member INT,
            need_garant INT 
        )""") # Если нет, то 0 (дефолт). Если нужен, то 1

    c.execute("""
        CREATE TABLE IF NOT EXISTS Messages(
            id INTEGER PRIMARY KEY,
            id_meeting TEXT,
            message INTEGER TEXT
            of_first_member TEXT,
            of_second_member TEXT,
            of_admin_member TEXT
        )""")

    # c.execute("""
    #         CREATE TABLE IF NOT EXISTS Text_rules(
    #             id INTEGER PRIMARY KEY,
    #             text TEXT
    #         )""")

    conn.commit()

init_db()
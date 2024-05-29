from models import get_connection

class Users:
    """Пользователь"""
    def insert(self, user_id):
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            f'INSERT INTO Users (user_id) VALUES ({user_id})')
        conn.commit()

    def select_all(self):
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM Users')
        users = c.fetchall()
        return users

    def select_one(self, user_id):
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM Users WHERE user_id = ?', ([user_id]))
        user = c.fetchone()
        if not user:
            return False
        return {"id": user[0], "user_id": user[1], "his_meeting": user[2]}

    def update_his_meeting(self, user_id, id_metting):
        print(user_id)
        conn = get_connection()
        c = conn.cursor()
        c.execute(f'UPDATE users SET his_meeting = "{id_metting}" WHERE user_id = {user_id}')
        conn.commit()

class Meetings:
    """Встреча"""
    def insert(self, id_meeting, first_member):
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            f'INSERT INTO Meetings (id_meeting, first_member, need_garant) VALUES ("{id_meeting}", {first_member}, 0)')
        conn.commit()

    def select_all(self):
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM Meetings')
        return c.fetchall()

    def select_one(self, id_meeting):
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM Meetings WHERE id_meeting = ?', ([id_meeting]))
        meeting = c.fetchone()
        if not meeting:
            return False
        return {"id": meeting[0], "id_meeting": meeting[1], "first_member": meeting[2], "second_member": meeting[3], "url_meeting": meeting[4], "admin": meeting[5], "need_garant": meeting[6]}

    def select_WHERE_need_garant(self, need_garant):
        """    Достает и отправляет список сделок, которые вызвали ГАРАНТА    """
        conn = get_connection()
        c = conn.cursor()
        c.execute(f'SELECT * FROM Meetings WHERE need_garant = {need_garant}')
        meetings = c.fetchall()
        return meetings

    def update_admin_member(self, id_meeting, admin_id):
        conn = get_connection()
        c = conn.cursor()
        c.execute('UPDATE Meetings SET admin_member = ? WHERE id_meeting = ?', (admin_id, id_meeting))
        conn.commit()

    def update_second_member(self, id_meeting, second_member):
        conn = get_connection()
        c = conn.cursor()
        c.execute('UPDATE Meetings SET second_member = ? WHERE id_meeting = ?', (second_member, id_meeting))
        conn.commit()

    def update_need_garant(self, id_meeting, need_garant):
        conn = get_connection()
        c = conn.cursor()
        c.execute(f'UPDATE Meetings SET need_garant = {need_garant} WHERE id_meeting = "{id_meeting}"')
        conn.commit()

    def delete(self, id_meeting):
        conn = get_connection()
        c = conn.cursor()
        c.execute('DELETE FROM Meetings WHERE id_meeting=?', (id_meeting,))
        conn.commit()

class Messages:
    """Сообщения"""
    def insert(self, id_meeting, message, first_member=False, second_member=False, admin=False):
        conn = get_connection()
        c = conn.cursor()

        if first_member:
            c.execute(
                f'INSERT INTO Messages (id_meeting, message, of_second_member) VALUES ("{id_meeting}", "{message}", "False")')
        elif second_member:
            c.execute(
                f'INSERT INTO Messages (id_meeting, message, of_second_member) VALUES ("{id_meeting}", "{message}", "True")')
        elif admin:
            c.execute(
                f'INSERT INTO Messages (id_meeting, message, of_second_member) VALUES ("{id_meeting}", "{message}", "False")')

        conn.commit()

    def select_all_msg_of_meeting(self, id_meeting):
        """Достать все смс определенной Сделки"""
        conn = get_connection()
        c = conn.cursor()
        c.execute(f'SELECT * FROM Messages WHERE id_meeting="{id_meeting}"')
        return c.fetchall()

    def select_all(self):
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM Messages')
        return c.fetchall()

    def delete_all(self, id_meeting):
        conn = get_connection()
        c = conn.cursor()
        c.execute('DELETE FROM Messages WHERE id_meeting=?', (id_meeting,))
        conn.commit()

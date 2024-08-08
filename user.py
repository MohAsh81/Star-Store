import re
from database import cursor, mydb

class User:
    def init(self, user_id, username, password):
        self.user_id = user_id
        self.username = username
        self.password = password

    @staticmethod
    def authenticate(username, password):
        cursor.execute(
            f"""SELECT * FROM users WHERE username = '{username}' AND password = '{password}'""")
        user = cursor.fetchone()
        if user:
            return User(user[0], user[1], user[2])
        return None

    def change_password(self, new_password):
        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$', new_password):
            return "Password must be at least 8 characters long, contain a number, a lowercase and an uppercase letter."

        cursor.execute(
            f"""UPDATE users SET password = '{new_password}' WHERE user_id = {self.user_id}""")
        mydb.commit()
        return "Password changed successfully"
class Comp_table:

    def __init__(self, db):
        self.db = db

    def id_competition(self, comp_number):
        cursor = self.db.cursor( )
        cursor.execute(
            "INSERT INTO id_competition (number) VALUES (?)",
            (comp_number,))
        self.db.commit( )
    def get_id_comp(self):
        cursor = self.db.cursor( )
        cursor.execute("SELECT MAX(number) AS number FROM id_competition")
        id_comp = cursor.fetchone()[0]
        return id_comp

class Adding_user:

    def __init__(self, db):
        self.db = db

    def insert_join_message(self, from_id, added_id, time):
        cursor = self.db.cursor()
        cursor.execute("SELECT MAX(number) AS number FROM id_competition")
        id_comp = cursor.fetchone( )[0]
        cursor.execute("INSERT INTO adding_user (numb_comp, from_id, added_id, time) VALUES (?, ?, ?, ?)",
                       (id_comp, from_id, added_id, time))
        self.db.commit()

    def user_info(self, user_id, user_name, first_name, last_name):
        cursor = self.db.cursor( )
        cursor.execute("INSERT INTO user_info (user_id, user_name, first_name, last_name) VALUES (?, ?, ?, ?)",
                       (user_id, user_name, first_name, last_name))

        self.db.commit( )

class Get_info:

    def __init__(self, db):
        self.db = db

    def current_comp(self):
        cursor = self.db.cursor( )
        cursor.execute("SELECT MAX(number) AS number FROM id_competition")
        self.numb_comp = cursor.fetchone()[0]
        return self.numb_comp

    def users_count(self, from_id):
        self.current_comp()
        cursor = self.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM adding_user WHERE from_id = ? AND numb_comp = ?", (from_id, self.numb_comp))
        count_users = cursor.fetchone()[0]
        return count_users

    def all_count(self):
        self.current_comp()
        cursor = self.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM adding_user WHERE  numb_comp = ?", (self.numb_comp,))
        all_count = cursor.fetchone()[0]
        return all_count

    def new_ticket(self, from_id):
        self.current_comp( )
        cursor = self.db.cursor( )
        cursor.execute("SELECT MAX(id) AS id FROM adding_user WHERE from_id = ? AND numb_comp = ?", (from_id, self.numb_comp))
        ticket = cursor.fetchone()[0]
        return ticket

    def user_tikets(self, from_id):
        self.current_comp()
        cursor = self.db.cursor( )
        cursor.execute("SELECT id FROM adding_user WHERE from_id = ? AND numb_comp = ?", (from_id, self.numb_comp))
        l = cursor.fetchall( )
        tikets_list = ', '.join(((str(list(i))).replace("[", "")).replace("]", "") for i in l)
        return tikets_list

    def users_list(self, from_id):
        self.current_comp()
        cursor = self.db.cursor()
        cursor.execute("SELECT au.id, ui.user_name, ui.first_name, ui.last_name, au.time FROM adding_user au LEFT JOIN user_info ui ON au.added_id = ui.user_id WHERE from_id = ? AND numb_comp = ?", (from_id, self.numb_comp))
        l = cursor.fetchall()
        print(l)
        us_list = '\n'.join(((str(list(i))).replace("[", "✅")).replace("]", ";") for i in l)
        return us_list

    def winner(self, ticket_id):
        self.current_comp( )
        cursor = self.db.cursor( )
        cursor.execute(
            "SELECT ui.user_name, ui.first_name, ui.last_name FROM adding_user au LEFT JOIN user_info ui ON au.from_id = ui.user_id WHERE numb_comp = ? AND au.id = ?",
            (self.numb_comp, ticket_id))
        winner_info = cursor.fetchall()
        user_n = winner_info[0][0]
        first_n = winner_info[0][1]
        last_n = winner_info[0][2]
        win_inf = f"{user_n}, {first_n} {last_n}"
        return win_inf

    def winner_add(self, ticket_id):
        self.current_comp( )
        cursor = self.db.cursor( )
        cursor.execute(
            "SELECT ui.user_name, ui.first_name, ui.last_name, au.time FROM adding_user au LEFT JOIN user_info ui ON au.added_id = ui.user_id WHERE numb_comp = ? AND au.id = ?",
            (self.numb_comp, ticket_id))
        added_info = cursor.fetchall()
        added_un = added_info[0][0]
        added_fn = added_info[0][1]
        added_ln = added_info[0][2]
        added_time = added_info[0][3]
        added_inf = f"{added_un}, {added_fn} {added_ln}, {added_time}"
        return added_inf

    def winner_user_id(self, ticket_id):
        self.current_comp()
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT from_id FROM adding_user WHERE numb_comp = ? AND id = ?",
            (self.numb_comp, ticket_id))
        us_id = cursor.fetchone()[0]
        print(us_id)
        return us_id

    def winner_added_id(self, ticket_id):
        self.current_comp( )
        cursor = self.db.cursor( )
        cursor.execute(
            "SELECT added_id FROM adding_user WHERE numb_comp = ? AND id = ?",
            (self.numb_comp, ticket_id))
        add_id = cursor.fetchone()[0]
        return add_id

    def users_id_list(self):
        self.current_comp( )
        cursor = self.db.cursor( )
        cursor.execute(
            "SELECT user_id FROM user_info")
        l = cursor.fetchall( )
        z = []
        for i in l:
            z.append(i[0])
        #print(z)
        return z
        #print(z)
        #us_list = [(296398759,), (386732873,), (596459751,), (933693522,), (1045326246,), (1171063162,), (1316137796,), (1383123353,), (1474998265,), (1482254642,), (1536743578,), (1663506819,)]

        #return us_list

class Switch:

    def __init__(self, db):
        self.db = db

    def comp_off(self):
        cursor = self.db.cursor( )
        cursor.execute("INSERT INTO id_competition (number) VALUES (0)")
        self.db.commit()

    def comp_on(self):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM id_competition WHERE number = 0")
        self.db.commit()

    def status(self):
        cursor = self.db.cursor( )
        cursor.execute(
            "SELECT number FROM id_competition")
        added_info = cursor.fetchall()
        l = []
        for i in added_info:
            for n in i:
                l.append(n)
        if 0 in l:
            a = False
        else:
            a = True
        return a

class GroupM:

    def __init__(self, db):
        self.db = db

    def save_id(self, message_id):
        cursor = self.db.cursor( )
        cursor.execute("INSERT INTO group_mes (message_id) VALUES (?)", (message_id,))
        self.db.commit( )

    def get_id(self):
        cursor = self.db.cursor( )
        cursor.execute("SELECT MAX(message_id) AS message_id FROM group_mes")
        self.message_id = cursor.fetchone( )[0]
        print(self.message_id)
        print(type(self.message_id))
        return self.message_id














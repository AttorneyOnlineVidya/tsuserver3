import yaml
import os
import copy
import sqlite3


DATABASE_NAME = "storage/stats/aov_database.db"

class Database:


    def __init__(self, server):
        self.server = server
        self.setup_database()

    def setup_database(self):
        try:
            conn = sqlite3.connect(DATABASE_NAME)
        except FileNotFoundError:
            if not os.path.exists('storage/stats/'):
                os.makedirs('storage/stats/')
            conn = sqlite3.connect(DATABASE_NAME)
        except Exception as e:
            print(e)
        finally:
            conn.close()
        self.initialize_database()
        self.char_data = self.make_char_database()
        self.music_data = self.make_music_database()
        self.user_data = self.make_user_database()
        self.check_char_list()
        self.check_music_list()
        self.check_user_list()

    def initialize_database(self):
        conn = sqlite3.connect(DATABASE_NAME)
        cur = conn.cursor()
        try:
            cur.execute('CREATE TABLE character (id INTEGER PRIMARY KEY, name TEXT NOT NULL, picked INTEGER NOT NULL, talked_idle INTEGER NOT NULL, '
                    'talked_build_recess INTEGER NOT NULL, talked_casing INTEGER NOT NULL);')
        except sqlite3.OperationalError:
            pass
        char = self.load_json_cdatabase()
        if char:
            char_arr = []
            for cid, cdata in char.items():
                char_arr.append((cdata.id, cdata.name, cdata.data["picked"], cdata.data["times_talked_idle"],
                                 cdata.data["times_talked_build_recess"], cdata.data["times_talked_casing"]))
            cur.executemany('INSERT INTO character VALUES (?,?,?,?,?,?)', char_arr)
        try:
            cur.execute(
                'CREATE TABLE music (id INTEGER PRIMARY KEY, name TEXT NOT NULL, play_idle INTEGER NOT NULL, '
                'play_build INTEGER NOT NULL, play_casing INTEGER NOT NULL);')
        except sqlite3.OperationalError:
            pass
        music = self.load_json_mdatabase()
        if music:
            music_arr = []
            midc = 0
            for mid, mdata in music.items():
                music_arr.append((midc, mdata.name, mdata.data["times_played_idle"],
                                 mdata.data["times_played_build_recess"],
                                 mdata.data["times_played_casing"]))
                midc += 1
            cur.executemany('INSERT INTO music VALUES (?,?,?,?,?)', music_arr)
        try:
            cur.execute(
                'CREATE TABLE user (ipid TEXT PRIMARY KEY, connected INTEGER NOT NULL, '
                'talk_idle INTEGER NOT NULL, talk_recess INTEGER NOT NULL, talk_casing INTEGER NOT NULL,'
                'kicked INTEGER NOT NULL, muted INTEGER NOT NULL, banned INTEGER NOT NULL, voted INTEGER NOT NULL,'
                'docced INTEGER NOT NULL);')
        except sqlite3.OperationalError:
            pass
        user = self.load_json_udatabase()
        if user:
            user_arr = []
            for uid, udata in user.items():
                user_arr.append((udata.ipid, udata.data["times_connected"],
                                 udata.data["times_talked_idle"], udata.data["times_talked_build_recess"],
                                 udata.data["times_talked_casing"], udata.data["times_kicked"],
                                  udata.data["times_muted"], udata.data["times_banned"],
                                  udata.data["times_voted"], udata.data["times_doc"]))
            cur.executemany('INSERT INTO user VALUES (?,?,?,?,?,?,?,?,?,?)', user_arr)
        self.delete_jsons()
        conn.commit()
        conn.close()

    def load_json_cdatabase(self):
        try:
            with open('storage/stats/chars.yaml', 'r') as char:
                data = yaml.load(char)
        except FileNotFoundError:
            data = False
        except ValueError:
            return
        return data

    def load_json_mdatabase(self):
        try:
            with open('storage/stats/music.yaml', 'r') as char:
                    data =  yaml.load(char)
        except FileNotFoundError:
            data = False
        except ValueError:
            return
        return data

    def load_json_udatabase(self):
        try:
            with open('storage/stats/user.yaml', 'r') as char:
                data = yaml.load(char)
        except FileNotFoundError:
            data = False
        except ValueError:
            return
        return data

    def delete_jsons(self):
        try:
            os.remove('storage/stats/user.yaml')
            os.remove('storage/stats/chars.yaml')
            os.remove('storage/stats/music.yaml')
        except FileNotFoundError:
            return

    def make_char_database(self):
        conn = sqlite3.connect(DATABASE_NAME)
        cur = conn.cursor()
        cur.execute('SELECT count(*) FROM character')
        count = cur.fetchone()
        if count[0] == 0:
            conn.close()
            return self.create_new_char_database()
        else:
            cur.execute('SELECT * FROM character')
            cdata = cur.fetchall()
            fdata = {}
            for chara in cdata:
                fdata[chara[0]] = charData(chara[0], chara[1].lower())
                fdata[chara[0]].data["picked"] = chara[2]
                fdata[chara[0]].data["times_talked_idle"] = chara[3]
                fdata[chara[0]].data["times_talked_build_recess"] = chara[4]
                fdata[chara[0]].data["times_talked_casing"] = chara[5]
            conn.close()
            return fdata

    def make_music_database(self):
        conn = sqlite3.connect(DATABASE_NAME)
        cur = conn.cursor()
        cur.execute('SELECT count(*) FROM music')
        count = cur.fetchone()
        if count[0] == 0:
            conn.close()
            return self.create_new_music_database()
        else:
            cur.execute('SELECT * FROM music')
            mdata = cur.fetchall()
            mfdata = {}
            for music in mdata:
                mfdata[music[0]] = charData(music[0], music[1].lower())
                mfdata[music[0]].data["times_played_idle"] = music[2]
                mfdata[music[0]].data["times_played_build_recess"] = music[3]
                mfdata[music[0]].data["times_played_casing"] = music[4]
            conn.close()
            return mfdata

    def make_user_database(self):
        conn = sqlite3.connect(DATABASE_NAME)
        cur = conn.cursor()
        cur.execute('SELECT count(*) FROM user')
        count = cur.fetchone()
        if count[0] == 0:
            conn.close()
            return self.create_new_char_database()
        else:
            cur.execute('SELECT * FROM user')
            usdata = cur.fetchall()
            udata = {}
            for user in usdata:
                udata[user[0]] = userData(user[0])
                udata[user[0]].data["times_connected"] = user[1]
                udata[user[0]].data["times_talked_idle"] = user[2]
                udata[user[0]].data["times_talked_build_recess"] = user[3]
                udata[user[0]].data["times_talked_casing"] = user[4]
                udata[user[0]].data["times_kicked"] = user[5]
                udata[user[0]].data["times_muted"] = user[6]
                udata[user[0]].data["times_banned"] = user[7]
                udata[user[0]].data["times_voted"] = user[8]
                udata[user[0]].data["times_doc"] = user[9]
            conn.close()
            return udata


    def check_char_list(self):
        for char in self.char_data:
            obj = self.char_data[char]
            for index in list(obj.indexes.keys()):
                if index not in obj.data:
                    self.char_data[char].data[index] = obj.indexes[index]


    def write_music_data(self):
        data = copy.deepcopy(self.music_data)
        with open('storage/stats/music.yaml', 'w') as mdata:
            yaml.dump(data, mdata, default_flow_style = False)

    def check_music_list(self):
        for char in self.music_data:
            obj = self.music_data[char]
            for index in list(obj.indexes.keys()):
                if index not in obj.data:
                    obj.data[index] = obj.indexes[index]

    def check_user_list(self):
        for char in self.user_data:
            obj = self.user_data[char]
            for index in list(obj.indexes.keys()):
                if index not in obj.data:
                    obj.data[index] = obj.indexes[index]

    def write_user_data(self):
        data = copy.deepcopy(self.user_data)
        with open('storage/stats/user.yaml', 'w') as udata:
            yaml.dump(data, udata, default_flow_style = False)

    def create_new_char_database(self):
        data = {}
        for i, ch in enumerate(self.server.char_list):
            data[i] = charData(i, ch.lower())
        return data

    def create_new_music_database(self):
        data = {}
        i = 0
        for cat in self.server.music_list:
            for song in cat['songs']:
                data[song['name'].lower()] = musicData(i, song['name'].lower())
        return data

    def character_picked(self, cid):
        self.char_data[cid].data["picked"] += 1

    def char_talked(self, cid, ipid, status):
        if status.lower() == 'idle':
            self.char_data[cid].data["times_talked_idle"] += 1
            self.user_data[ipid].data["times_talked_idle"] += 1
        if status.lower() == 'building-open' or status.lower() == 'building-full' or status.lower() == 'recess':
            self.char_data[cid].data["times_talked_build_recess"] += 1
            self.user_data[ipid].data["times_talked_build_recess"] += 1
        if status.lower() == 'casing-open' or status.lower() == 'casing-full':
            self.char_data[cid].data["times_talked_casing"] += 1
            self.user_data[ipid].data["times_talked_casing"] += 1

    def music_played(self, name, status):
        if status.lower() == 'idle':
            self.music_data[name.lower()].data["times_talked_idle"] += 1
        if status.lower() == 'building-open' or status.lower() == 'building-full' or status.lower() == 'recess':
            self.music_data[name.lower()].data["times_played_build_recess"] += 1
        if status.lower() == 'casing-open' or status.lower() == 'casing-full':
            self.music_data[name.lower()].data["times_played_casing"] += 1

    def connect_data(self, ipid, hdid):
        if ipid not in self.user_data:
            self.user_data[ipid] = userData(ipid, hdid)
        else:
            self.user_data[ipid].data["times_connected"] += 1

    def kicked_user(self, ipid):
        try:
            self.user_data[ipid].data["times_kicked"] += 1
        except IndexError:
            return

    def muted_user(self, ipid):
        try:
            self.user_data[ipid].data["times_muted"] += 1
        except IndexError:
            return

    def banned_user(self, ipid):
        try:
            self.user_data[ipid].data["times_banned"] += 1
        except IndexError:
            return

    def user_voted(self, ipid):
        try:
            self.user_data[ipid].data["times_voted"] += 1
        except IndexError:
            return

    def user_doc(self, ipid):
        try:
            self.user_data[ipid].data["times_doc"] += 1
        except IndexError:
            return

    def save_alldata(self):
            conn = sqlite3.connect(DATABASE_NAME)
            cur = conn.cursor()
            char_arr = []
            for cid, cdata in self.char_data.items():
                char_arr.append((cdata.id, cdata.name, cdata.data["picked"], cdata.data["times_talked_idle"],
                                 cdata.data["times_talked_build_recess"], cdata.data["times_talked_casing"]))
            music_arr = []
            midc = 0
            for mid, mdata in self.music_data.items():
                music_arr.append((midc, mdata.name, mdata.data["times_played_idle"],
                                 mdata.data["times_played_build_recess"],
                                 mdata.data["times_played_casing"]))
                midc += 1
            user_arr = []
            for uid, udata in self.user_data.items():
                user_arr.append((udata.ipid, udata.data["times_connected"],
                                 udata.data["times_talked_idle"], udata.data["times_talked_build_recess"],
                                 udata.data["times_talked_casing"], udata.data["times_kicked"],
                                  udata.data["times_muted"], udata.data["times_banned"],
                                  udata.data["times_voted"], udata.data["times_doc"]))
            cur.execute('DELETE FROM character')
            cur.execute('DELETE FROM music')
            cur.execute('DELETE FROM user')
            cur.executemany('INSERT INTO character VALUES (?,?,?,?,?,?)', char_arr)
            cur.executemany('INSERT INTO music VALUES (?,?,?,?,?)', music_arr)
            cur.executemany('INSERT INTO user VALUES (?,?,?,?,?,?,?,?,?,?)', user_arr)
            conn.commit()
            conn.close()

class charData:

    indexes =  {
        "picked": 0,
        "times_talked_idle": 0,
        "times_talked_build_recess": 0,
        "times_talked_casing": 0,
    }

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.data = {}
        for i in self.indexes:
            self.data[i] = self.indexes[i]

class musicData:

    indexes =  {
        "times_played_idle": 0,
        "times_played_build_recess": 0,
        "times_played_casing": 0,
    }

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.data = {}
        for i in self.indexes:
            self.data[i] = self.indexes[i]

class userData:

    indexes =  {
        "times_connected": 0,
        "times_talked_idle": 0,
        "times_talked_build_recess": 0,
        "times_talked_casing": 0,
        "times_kicked": 0,
        "times_muted": 0,
        "times_banned": 0,
        "times_voted": 0,
        "times_doc": 0,
    }

    def __init__(self, id):
        self.ipid = id
        self.data = {}
        for i in self.indexes:
            self.data[i] = self.indexes[i]

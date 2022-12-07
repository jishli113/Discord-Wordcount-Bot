import sqlite3

CREATE_GUILD_TABLE = "CREATE TABLE guilds (id INTEGER PRIMARY KEY, name TEXT NON NULL);"
CHECK_GUILD_TABLE_EXISTS = "SELECT name FROM sqlite_master WHERE type='table' AND name='guilds';"
CHECK_GUILD_EXISTS = "SELECT id FROM guilds WHERE id = ?"
CHECK_USER_EXISTS = "SELECT userID FROM users WHERE (userID = ? AND guildId = ?)"
INSERT_GUILD = "INSERT INTO guilds (id, name) VALUES (?, ?);"
CHECK_USER_TABLE_EXISTS = "SELECT * FROM sqlite_master WHERE type='table' AND name='users'"
CREATE_USER_TABLE = "CREATE TABLE users (userID INTEGER, guildId INTEGER, FOREIGN KEY(guildId) REFERENCES guilds(id), PRIMARY KEY(userID, guildId));"
INSERT_USER = "INSERT INTO users (userID, guildId) VALUES(?, ?);"
CREATE_WORD_TABLE = "CREATE TABLE words (userID INTEGER, word VARCHAR(10), count INTEGER NOT NULL, FOREIGN KEY(userID) REFERENCES users(userID),  PRIMARY KEY(userID, word));"
CHECK_WORD_TABLE_EXISTS = "SELECT * FROM sqlite_master WHERE type='table' AND name='words'"
INSERT_WORD = "INSERT INTO words(userID, word, count) VALUES(?, ?, ?)"
UPDATE_WORD_COUNT = "UPDATE words SET count = count+? WHERE userID=?  AND word=?"
CHECK_WORD_EXISTS = "SELECT userID FROM words WHERE (userID=? AND word=?)"
GET_WORDS_BY_USER = "SELECT word, count FROM words WHERE userID = ? ORDER BY count DESC"
GET_WORDS_BY_USER_LIMIT = "SELECT word, count FROM words WHERE userID = ? ORDER BY count DESC LIMIT ?"
DROP_USER_TABLE = "DROP TABLE users"
DROP_WORD_TABLE = "DROP TABLE words"
DROP_GUILDS_TABLE = "DROP TABLE guilds"
GET_USER_COUNTS_BY_WORD = "SELECT DISTINCT words.userID, count FROM (words JOIN users) WHERE guildId=? AND word=? ORDER BY count DESC"
GET_SINGLE_WORD_COUNT = "SELECT count FROM words WHERE userID = ? AND word = ?"


def create_guild(c, connection):
    c.execute(CHECK_GUILD_TABLE_EXISTS)
    if c.fetchone() is None:
        c.execute(CREATE_GUILD_TABLE)
        connection.commit()
    else:
        print("Table Already Exists!")


def insert_guild(connection, c, guild_id, name):
    c.execute(CHECK_GUILD_EXISTS, (guild_id,))
    if c.fetchone() is not None:
        print('guild entry already exists!')
        return
    c.execute(INSERT_GUILD, (guild_id, name))
    connection.commit()


def check_user_table_exists(connection, c):
    c.execute(CHECK_USER_TABLE_EXISTS)
    if c.fetchone() is None:
        return False
    return True


def create_user(connection, c):
    c.execute(CREATE_USER_TABLE)
    connection.commit()


def insert_user(connection, c, userID, guildId):
    c.execute(CHECK_USER_EXISTS, (userID, guildId))
    if c.fetchone() is not None:
        return
    c.execute(INSERT_USER, (userID, guildId))
    print(connection.commit())


def create_word_table(c):
    c.execute(CREATE_WORD_TABLE)


def check_word_table_exists(c):
    c.execute(CHECK_WORD_TABLE_EXISTS)
    if c.fetchone() is None:
        return False
    return True


def insert_word(connection, c, userID, word, times=1):
    c.execute(CHECK_WORD_EXISTS, (userID, word))
    if c.fetchone() is not None:
        c.execute(UPDATE_WORD_COUNT, (times, userID, word))
        connection.commit()
        return
    c.execute(INSERT_WORD, (userID, word, 1))
    connection.commit()


def get_all_user_words(connection, c, userID, limit=None):
    if limit is None:
        c.execute(GET_WORDS_BY_USER, (userID,))
    else:
        c.execute(GET_WORDS_BY_USER_LIMIT, (userID, limit))

    return c.fetchall()


def drop_all_tables(connection, c):
    c.execute(DROP_WORD_TABLE)
    c.execute(DROP_USER_TABLE)
    c.execute(DROP_GUILDS_TABLE)
    connection.commit()


def get_users_by_word(c, guildID, word):
    c.execute(GET_USER_COUNTS_BY_WORD, (guildID, word))
    return c.fetchall()


def get_single_word_count(c, userID, word):
    print('times')
    c.execute(GET_SINGLE_WORD_COUNT, (userID, word))
    ret = c.fetchone()
    if ret is None:
        print('yes')
        return 0
    return ret[0]


def user_exists_in_guild(c, userID, guildID):
    c.execute(CHECK_USER_EXISTS, (userID, guildID))
    if c.fetchone() is None:
        return False
    return True

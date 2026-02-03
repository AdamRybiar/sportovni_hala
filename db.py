import sqlite3

DB_NAME = "rezervace.db"

def connect():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sportoviste (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nazev TEXT NOT NULL,
        typ TEXT NOT NULL,
        kapacita INTEGER NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS uzivatele (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        jmeno TEXT NOT NULL,
        email TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS rezervace (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        datum TEXT NOT NULL,
        cas_od TEXT NOT NULL,
        cas_do TEXT NOT NULL,
        sportoviste_id INTEGER,
        FOREIGN KEY (sportoviste_id) REFERENCES sportoviste(id)
    )
    """)

    conn.commit()
    conn.close()

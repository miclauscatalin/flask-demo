"""Migrare BD: adaug coloana preferred_lang la tabela user.
/ DB migration: add preferred_lang column to user table."""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cols = [row[1] for row in cur.execute('PRAGMA table_info(user)').fetchall()]
if 'preferred_lang' not in cols:
    cur.execute("ALTER TABLE user ADD COLUMN preferred_lang VARCHAR(5) NOT NULL DEFAULT 'ro'")
    conn.commit()
    print('Column preferred_lang added successfully.')
else:
    print('Column preferred_lang already exists — nothing to do.')

conn.close()

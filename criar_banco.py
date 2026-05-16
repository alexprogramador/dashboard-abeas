import sqlite3

conn = sqlite3.connect("abeas.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS indicadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ano INTEGER,
    tipo TEXT,
    indicador TEXT,
    valor REAL
)
""")

conn.commit()
conn.close()

print("Banco criado com sucesso!")
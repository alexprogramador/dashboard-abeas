import sqlite3

conn = sqlite3.connect("abeas.db")
cursor = conn.cursor()

dados = [
    (2025, "Pessoas Impactadas Diretamente", 1030),
    (2025, "Pessoas Impactadas Indiretamente", 3321),
    (2025, "Voluntários", 30),
    (2025, "Colaboradores", 9),
    (2025, "Atendimentos Psicossociais", 2208),
    (2025, "Cestas Básicas", 1310),
    (2025, "Alimentos (kg)", 19650),
]

cursor.executemany("""
INSERT INTO indicadores (ano, indicador, valor)
VALUES (?, ?, ?)
""", dados)

conn.commit()
conn.close()

print("Dados inseridos com sucesso!")
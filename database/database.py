import sqlite3
import pandas as pd

# Criar banco de dados
conn = sqlite3.connect('lista_compras')
cursor = conn.cursor()

# Criar tabela inicial
cursor.execute('''CREATE TABLE IF NOT EXISTS lista1 (
id integer PRIMARY KEY AUTOINCREMENT,
produto text NOT NULL,
categoria text,
checks integer);''')

# Criar tabela de produtos
dados = pd.read_excel('lista.xlsx', sheet_name=0)
dados.to_sql('produtos', conn, index=False)

conn.commit()

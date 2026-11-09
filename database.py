
import sqlite3

DB_NAME = "lumina.db"


def conectar():
    return sqlite3.connect(DB_NAME)


def criar_tabela():
    conexao = conectar()

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS despesas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            categoria TEXT NOT NULL,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conexao.commit()
    conexao.close()


def adicionar_despesa(descricao, valor, categoria):
    conexao = conectar()

    conexao.execute(
        """
        INSERT INTO despesas (descricao, valor, categoria)
        VALUES (?, ?, ?)
        """,
        (descricao, valor, categoria)
    )

    conexao.commit()
    conexao.close()


def listar_despesas():
    conexao = conectar()

    cursor = conexao.execute("""
        SELECT id, descricao, valor, categoria, data
        FROM despesas
        ORDER BY id DESC
    """)

    despesas = cursor.fetchall()
    conexao.close()

    return despesas
def excluir_despesa(id_despesa):
    conexao = conectar()

    try:
        cursor = conexao.execute(
            "DELETE FROM despesas WHERE id = ?",
            (id_despesa,)
        )
        conexao.commit()
        return cursor.rowcount > 0
    finally:
        conexao.close()
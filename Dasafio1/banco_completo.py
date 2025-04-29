import sqlite3
from hashlib import sha256
import getpass
from datetime import datetime

# Funções auxiliares
def hash_senha(senha):
    return sha256(senha.encode()).hexdigest()

def conectar():
    return sqlite3.connect("banco.db", timeout=10)

def criar_tabelas():
    with conectar() as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS contas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL,
                saldo REAL DEFAULT 0
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conta_id INTEGER,
                tipo TEXT,
                valor REAL,
                destino TEXT,
                data TEXT,
                FOREIGN KEY (conta_id) REFERENCES contas(id)
            )
        """)

# Funções principais
def criar_conta():
    nome = input("Nome completo: ")
    cpf = input("CPF: ")
    senha = input("Senha: ")
    senha_hash = hash_senha(senha)

    with conectar() as con:
        cur = con.cursor()
        try:
            cur.execute("INSERT INTO contas (nome, cpf, senha) VALUES (?, ?, ?)", (nome, cpf, senha_hash))
            print("\n✅ Conta criada com sucesso!")
        except sqlite3.IntegrityError:
            print("\n❌ CPF já cadastrado.")

def login():
    cpf = input("CPF: ")
    senha = input("Senha: ")
    senha_hash = hash_senha(senha)

    with conectar() as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM contas WHERE cpf = ? AND senha = ?", (cpf, senha_hash))
        usuario = cur.fetchone()

    if usuario:
        print(f"\n👋 Bem-vindo(a), {usuario[1]}!")
        menu_logado(usuario)
    else:
        print("\n❌ CPF ou senha incorretos.")

def registrar_transacao(conta_id, tipo, valor, destino=None):
    with conectar() as con:
        cur = con.cursor()
        cur.execute("""
            INSERT INTO transacoes (conta_id, tipo, valor, destino, data)
            VALUES (?, ?, ?, ?, ?)
        """, (conta_id, tipo, valor, destino, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

def consultar_saldo(conta):
    print(f"💰 Saldo atual: R$ {conta[4]:.2f}")

def depositar(conta):
    valor = float(input("Valor do depósito: R$ "))
    if valor <= 0:
        print("❌ Valor inválido.")
        return conta

    novo_saldo = conta[4] + valor
    with conectar() as con:
        cur = con.cursor()
        cur.execute("UPDATE contas SET saldo = ? WHERE id = ?", (novo_saldo, conta[0]))

    registrar_transacao(conta[0], "Depósito", valor)
    conta = atualizar_conta(conta[0])
    print(f"✅ Depósito realizado. Novo saldo: R$ {conta[4]:.2f}")
    return conta

def sacar(conta):
    valor = float(input("Valor do saque: R$ "))
    hoje = datetime.now().strftime("%Y-%m-%d")

    with conectar() as con:
        cur = con.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM transacoes 
            WHERE conta_id = ? AND tipo = 'Saque' AND DATE(data) = ?
        """, (conta[0], hoje))
        saques_hoje = cur.fetchone()[0]

        if saques_hoje >= 3:
            print("❌ Limite diário de 3 saques atingido.")
            return conta

        if valor > conta[4]:
            print("❌ Saldo insuficiente.")
            return conta

        if valor <= 0:
            print("❌ Valor inválido.")
            return conta

        novo_saldo = conta[4] - valor
        cur.execute("UPDATE contas SET saldo = ? WHERE id = ?", (novo_saldo, conta[0]))

    registrar_transacao(conta[0], "Saque", valor)
    conta = atualizar_conta(conta[0])
    print(f"✅ Saque realizado. Novo saldo: R$ {conta[4]:.2f}")
    return conta

def transferir(conta):
    cpf_destino = input("CPF do destinatário: ")
    valor = float(input("Valor da transferência: R$ "))

    if valor <= 0 or valor > conta[4]:
        print("❌ Valor inválido ou saldo insuficiente.")
        return conta

    with conectar() as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM contas WHERE cpf = ?", (cpf_destino,))
        destino = cur.fetchone()

        if not destino:
            print("❌ Conta de destino não encontrada.")
            return conta

        novo_saldo_origem = conta[4] - valor
        novo_saldo_destino = destino[4] + valor

        cur.execute("UPDATE contas SET saldo = ? WHERE id = ?", (novo_saldo_origem, conta[0]))
        cur.execute("UPDATE contas SET saldo = ? WHERE id = ?", (novo_saldo_destino, destino[0]))

    registrar_transacao(conta[0], "Transferência enviada", valor, destino[2])
    registrar_transacao(destino[0], "Transferência recebida", valor, conta[2])

    conta = atualizar_conta(conta[0])
    print(f"✅ Transferência realizada. Novo saldo: R$ {conta[4]:.2f}")
    return conta

def extrato(conta):
    with conectar() as con:
        cur = con.cursor()
        cur.execute("""
            SELECT tipo, valor, destino, data FROM transacoes
            WHERE conta_id = ? ORDER BY data ASC
        """, (conta[0],))
        transacoes = cur.fetchall()

    print("\n======📄EXTRATO ======")
    for t in transacoes:
        tipo, valor, destino, data = t
        linha = f"{data} - {tipo}: R$ {valor:.2f}"
        if destino:
            linha += f" (Dest/Rem: {destino})"
        print(linha)
    print("")
    print(f"💰 Saldo atual: R$ {conta[4]:.2f}")

def atualizar_conta(id):
    with conectar() as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM contas WHERE id = ?", (id,))
        return cur.fetchone()

def menu_logado(conta):
    while True:
        print("""
        1. Consultar saldo
        2. Depositar
        3. Sacar
        4. Transferir
        5. Ver extrato      
        6. Sair
        """)
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            consultar_saldo(conta)
            
        elif opcao == "2":
            conta = depositar(conta)
        elif opcao == "3":
            conta = sacar(conta)        
        elif opcao == "4":
            conta = transferir(conta)
        elif opcao == '5':
            extrato(conta)
        elif opcao == "6":
            print("👋 Até logo!")
            break
        else:
            print("❌ Opção inválida.")

def main():
    criar_tabelas()
    while True:
        print("""
        === Banco Simples ===
        1. Criar Conta
        2. Login
        3. Sair
        """)
        escolha = input("Escolha uma opção: ")

        if escolha == "1":
            criar_conta()
        elif escolha == "2":
            login()
        elif escolha == "3":
            print("👋 Encerrando o sistema...")
            break
        else:
            print("❌ Opção inválida.")

if __name__ == "__main__":
    main()

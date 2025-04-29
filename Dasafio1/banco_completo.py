import sqlite3
import hashlib
import getpass
from datetime import datetime

# Funções auxiliares
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def conectar():
    return sqlite3.connect("banco.db")

def criar_tabelas():
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            saldo REAL DEFAULT 0
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conta_id INTEGER,
            tipo TEXT,
            valor REAL,
            destino TEXT,
            data TEXT,
            FOREIGN KEY (conta_id) REFERENCES contas (id)
        );
    """)
    con.commit()
    con.close()

# Funções principais
def criar_conta():
    nome = input("Nome completo: ")
    cpf = input("CPF (somente números): ")
    senha = getpass.getpass("Crie uma senha: ")
    senha_cripto = hash_senha(senha)

    con = conectar()
    cur = con.cursor()
    try:
        cur.execute("INSERT INTO contas (nome, cpf, senha) VALUES (?, ?, ?)", (nome, cpf, senha_cripto))
        con.commit()
        print("✅ Conta criada com sucesso!")
    except sqlite3.IntegrityError:
        print("⚠️ CPF já cadastrado.")
    con.close()

def login():
    cpf = input("CPF: ")
    senha = getpass.getpass("Senha: ")
    senha_cripto = hash_senha(senha)

    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT * FROM contas WHERE cpf = ? AND senha = ?", (cpf, senha_cripto))
    usuario = cur.fetchone()
    con.close()

    if usuario:
        print(f"✅ Bem-vindo, {usuario[1]}!")
        menu_logado(usuario)
    else:
        print("❌ CPF ou senha inválidos.")

def registrar_transacao(conta_id, tipo, valor, destino=None):
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO transacoes (conta_id, tipo, valor, destino, data)
        VALUES (?, ?, ?, ?, ?)
    """, (conta_id, tipo, valor, destino, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    con.commit()
    con.close()

def consultar_saldo(conta):
    print(f"💰 Saldo atual: R$ {conta[4]:.2f}")

def depositar(conta):
    valor = float(input("Valor do depósito: R$ "))
    con = conectar()
    cur = con.cursor()
    novo_saldo = conta[4] + valor
    cur.execute("UPDATE contas SET saldo = ? WHERE id = ?", (novo_saldo, conta[0]))
    con.commit()
    registrar_transacao(conta[0], "Depósito", valor)
    con.close()
    conta = atualizar_conta(conta[0])
    print(f"✅ Depósito realizado. Novo saldo: R$ {conta[4]:.2f}")
    return conta

def sacar(conta):
    valor = float(input("Valor do saque: R$ "))
    hoje = datetime.now().strftime("%Y-%m-%d")  # formato string

    con = conectar()
    cur = con.cursor()
    cur.execute("""
        SELECT COUNT(*) FROM transacoes 
        WHERE conta_id = ? AND tipo = 'Saque' AND DATE(data) = ?
    """, (conta[0], hoje))
    saques_hoje = cur.fetchone()[0]
    
    if saques_hoje >= 3:
        print("❌ Limite diário de 3 saques atingido.")
        con.close()
        return conta

    if valor > conta[4]:
        print("❌ Saldo insuficiente.")
        con.close()
        return conta

    if valor <= 0:
        print("❌ Valor inválido.")
        con.close()
        return conta

    novo_saldo = conta[4] - valor
    cur.execute("UPDATE contas SET saldo = ? WHERE id = ?", (novo_saldo, conta[0]))
    con.commit()
    registrar_transacao(conta[0], "Saque", valor)
    con.close()

    conta = atualizar_conta(conta[0])
    print(f"✅ Saque realizado. Novo saldo: R$ {conta[4]:.2f}")
    return conta

def transferir(conta):
    cpf_destino = input("CPF do destinatário: ")
    valor = float(input("Valor da transferência: R$ "))
    if valor > conta[4]:
        print("❌ Saldo insuficiente.")
        return conta

    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT * FROM contas WHERE cpf = ?", (cpf_destino,))
    destino = cur.fetchone()
    if not destino:
        print("❌ Conta destino não encontrada.")
        con.close()
        return conta

    novo_saldo_origem = conta[4] - valor
    novo_saldo_destino = destino[4] + valor

    cur.execute("UPDATE contas SET saldo = ? WHERE id = ?", (novo_saldo_origem, conta[0]))
    cur.execute("UPDATE contas SET saldo = ? WHERE id = ?", (novo_saldo_destino, destino[0]))

    registrar_transacao(conta[0], "Transferência enviada", valor, destino[2])
    registrar_transacao(destino[0], "Transferência recebida", valor, conta[2])
    con.commit()
    con.close()
    conta = atualizar_conta(conta[0])
    print("✅ Transferência realizada com sucesso.")
    return conta

def ver_extrato(conta):
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT tipo, valor, destino, data FROM transacoes WHERE conta_id = ? ORDER BY data ASC", (conta[0],))
    transacoes = cur.fetchall()
    con.close()
    print("======📄EXTRATO ======")
    for t in transacoes:
        destino = f" → {t[2]}" if t[2] else ""
        print(f"{t[3]} | {t[0]}: R$ {t[1]:.2f}{destino}")
    print("")
    print(f"💰 Saldo atual: R$ {conta[4]:.2f}")

def atualizar_conta(conta_id):
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT * FROM contas WHERE id = ?", (conta_id,))
    nova_conta = cur.fetchone()
    con.close()
    return nova_conta

# Menu
def menu_logado(conta):
    while True:
        print("\n1. Consultar saldo")
        print("2. Depositar")
        print("3. Sacar")
        print("4. Transferir")
        print("5. Ver extrato")
        print("6. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            consultar_saldo(conta)
        elif opcao == '2':
            conta = depositar(conta)
        elif opcao == '3':
            conta = sacar(conta)
        elif opcao == '4':
            conta = transferir(conta)
        elif opcao == '5':
            ver_extrato(conta)
        elif opcao == '6':
            print("👋 Saindo...")
            break
        else:
            print("❌ Opção inválida.")

def main():
    criar_tabelas()
    while True:
        print("\n=== Banco Simples ===")
        print("1. Criar conta")
        print("2. Login")
        print("3. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            criar_conta()
        elif opcao == '2':
            login()
        elif opcao == '3':
            print("👋 Até logo!")
            break
        else:
            print("❌ Opção inválida.")

if __name__ == "__main__":
    main()

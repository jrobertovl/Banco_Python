
import sqlite3
from hashlib import sha256
from datetime import datetime
from tkinter import *
from tkinter import messagebox
import webbrowser
import os

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

def registrar_transacao(conta_id, tipo, valor, destino=None):
    with conectar() as con:
        cur = con.cursor()
        cur.execute("""
            INSERT INTO transacoes (conta_id, tipo, valor, destino, data)
            VALUES (?, ?, ?, ?, ?)
        """, (conta_id, tipo, valor, destino, datetime.now().strftime("%d-%m-%Y %H:%M:%S")))

class BancoApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Banco Simples")
        self.master.geometry("400x500")
        self.master.configure(bg="#1e1e2f")
        self.conta_atual = None
        criar_tabelas()
        self.tela_inicial()

    def limpar_tela(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def tela_inicial(self):
        self.limpar_tela()
        Label(self.master, text="Banco Simples", font=("Helvetica", 20), bg="#1e1e2f", fg="white").pack(pady=30)

        Button(self.master, text="Criar Conta", command=self.tela_criar_conta, width=20, bg="#2ecc71", fg="white").pack(pady=10)
        Button(self.master, text="Login", command=self.tela_login, width=20, bg="#3498db", fg="white").pack(pady=10)
        Button(self.master, text="Sair", command=self.master.quit, width=20, bg="#e74c3c", fg="white").pack(pady=10)

    def tela_criar_conta(self):
        self.limpar_tela()
        Label(self.master, text="Criar Conta", font=("Helvetica", 16), bg="#1e1e2f", fg="white").pack(pady=20)

        nome = Entry(self.master, width=30)
        cpf = Entry(self.master, width=30)
        senha = Entry(self.master, width=30, show="*")
        for label_text, widget in zip(["Nome completo", "CPF", "Senha"], [nome, cpf, senha]):
            Label(self.master, text=label_text, bg="#1e1e2f", fg="white").pack()
            widget.pack(pady=5)

        def criar():
            with conectar() as con:
                cur = con.cursor()
                try:
                    cur.execute("INSERT INTO contas (nome, cpf, senha) VALUES (?, ?, ?)",
                                (nome.get(), cpf.get(), hash_senha(senha.get())))
                    messagebox.showinfo("Sucesso", "Conta criada com sucesso!")
                    self.tela_inicial()
                except sqlite3.IntegrityError:
                    messagebox.showerror("Erro", "CPF já cadastrado.")

        Button(self.master, text="Criar", command=criar, bg="#2ecc71", fg="white").pack(pady=20)
        Button(self.master, text="Voltar", command=self.tela_inicial, bg="#95a5a6", fg="black").pack()

    def tela_login(self):
        self.limpar_tela()
        Label(self.master, text="Login", font=("Helvetica", 16), bg="#1e1e2f", fg="white").pack(pady=20)

        cpf = Entry(self.master, width=30)
        senha = Entry(self.master, width=30, show="*")
        for label_text, widget in zip(["CPF", "Senha"], [cpf, senha]):
            Label(self.master, text=label_text, bg="#1e1e2f", fg="white").pack()
            widget.pack(pady=5)

        def logar():
            with conectar() as con:
                cur = con.cursor()
                cur.execute("SELECT * FROM contas WHERE cpf = ? AND senha = ?", (cpf.get(), hash_senha(senha.get())))
                self.conta_atual = cur.fetchone()
                if self.conta_atual:
                    self.menu_logado()
                else:
                    messagebox.showerror("Erro", "CPF ou senha incorretos.")

        Button(self.master, text="Entrar", command=logar, bg="#3498db", fg="white").pack(pady=20)
        Button(self.master, text="Voltar", command=self.tela_inicial, bg="#95a5a6", fg="black").pack()

    def menu_logado(self):
        self.limpar_tela()
        Label(self.master, text=f"Bem-vindo, {self.conta_atual[1]}", font=("Helvetica", 14), bg="#1e1e2f", fg="white").pack(pady=20)

        botoes = [
            ("Consultar Saldo", self.consultar_saldo),
            ("Depositar", self.depositar),
            ("Sacar", self.sacar),
            ("Transferir", self.transferir),
            ("Ver Extrato", self.ver_extrato),
            ("Encerrar Conta", self.encerrar_conta),
            ("Sair", self.tela_inicial)
        ]

        for texto, comando in botoes:
            Button(self.master, text=texto, command=comando, width=25, bg="#34495e", fg="white").pack(pady=5)

    def consultar_saldo(self):
        messagebox.showinfo("Saldo", f"Saldo atual: R$ {self.conta_atual[4]:.2f}")

    def depositar(self):
        valor = self.solicitar_valor("Depósito")
        if valor > 0:
            novo_saldo = self.conta_atual[4] + valor
            with conectar() as con:
                cur = con.cursor()
                cur.execute("UPDATE contas SET saldo = ? WHERE id = ?", (novo_saldo, self.conta_atual[0]))
            registrar_transacao(self.conta_atual[0], "Depósito", valor)
            self.conta_atual = self.atualizar_conta()
            messagebox.showinfo("Sucesso", f"Depósito realizado. Novo saldo: R$ {novo_saldo:.2f}")

    def sacar(self):
        valor = self.solicitar_valor("Saque")
        hoje = datetime.now().strftime("%Y-%m-%d")
        with conectar() as con:
            cur = con.cursor()
            cur.execute("""
                SELECT COUNT(*) FROM transacoes 
                WHERE conta_id = ? AND tipo = 'Saque' AND DATE(data) = ?
            """, (self.conta_atual[0], hoje))
            saques_hoje = cur.fetchone()[0]
        if saques_hoje >= 3:
            messagebox.showerror("Erro", "Limite diário de 3 saques atingido.")
            return
        if 0 < valor <= self.conta_atual[4]:
            novo_saldo = self.conta_atual[4] - valor
            with conectar() as con:
                cur = con.cursor()
                cur.execute("UPDATE contas SET saldo = ? WHERE id = ?", (novo_saldo, self.conta_atual[0]))
            registrar_transacao(self.conta_atual[0], "Saque", valor)
            self.conta_atual = self.atualizar_conta()
            messagebox.showinfo("Sucesso", f"Saque realizado. Novo saldo: R$ {novo_saldo:.2f}")
        else:
            messagebox.showerror("Erro", "Saldo insuficiente ou valor inválido.")

    def transferir(self):
        from tkinter import simpledialog
        destino = simpledialog.askstring("Transferência", "CPF do destinatário:")
        valor = self.solicitar_valor("Transferência")
        if destino == self.conta_atual[2]:
            messagebox.showerror("Erro", "Não é possível transferir para si mesmo.")
            return
        with conectar() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM contas WHERE cpf = ?", (destino,))
            conta_destino = cur.fetchone()
            if not conta_destino:
                messagebox.showerror("Erro", "Conta destino não encontrada.")
                return
            if valor <= 0 or valor > self.conta_atual[4]:
                messagebox.showerror("Erro", "Valor inválido ou saldo insuficiente.")
                return
            cur.execute("UPDATE contas SET saldo = ? WHERE id = ?", (conta_destino[4] + valor, conta_destino[0]))
            cur.execute("UPDATE contas SET saldo = ? WHERE id = ?", (self.conta_atual[4] - valor, self.conta_atual[0]))
        registrar_transacao(self.conta_atual[0], "Transferência enviada", valor, destino)
        registrar_transacao(conta_destino[0], "Transferência recebida", valor, self.conta_atual[2])
        self.conta_atual = self.atualizar_conta()
        messagebox.showinfo("Sucesso", f"Transferência realizada. Novo saldo: R$ {self.conta_atual[4]:.2f}")

    '''def ver_extrato(self):
        with conectar() as con:
            cur = con.cursor()
            cur.execute("SELECT tipo, valor, destino, data FROM transacoes WHERE conta_id = ? ORDER BY data ASC", (self.conta_atual[0],))
            transacoes = cur.fetchall()
        texto = "\n".join([f"{data} - {tipo}: R$ {valor:.2f}" + (f" (Dest/Rem: {destino})" if destino else "") for tipo, valor, destino, data in transacoes])
        messagebox.showinfo("Extrato", texto or "Nenhuma transação.")'''
    def ver_extrato(self):
        with conectar() as con:
            cur = con.cursor()
            cur.execute("SELECT tipo, valor, destino, data FROM transacoes WHERE conta_id = ? ORDER BY data ASC", (self.conta_atual[0],))
            transacoes = cur.fetchall()

        with conectar() as con:
            cur = con.cursor()
            cur.execute("SELECT nome FROM contas WHERE id = ?", (self.conta_atual[0],))
            cliente = cur.fetchone()
            nome = cliente[0] if cliente else "Desconhecido"
            

        if not transacoes:
            html = "<p>Nenhuma transação registrada.</p>"
        else:
            saldo = 0
            for tipo, valor, destino, data in transacoes:
                if tipo in ("Depósito", "Transferência recebida"):
                    saldo += valor
                elif tipo in ("Saque", "Transferência enviada"):
                    saldo -= valor
            linhas = "".join([f"<tr><td>{data}</td><td>{tipo}</td><td>R$ {valor:.2f}</td><td>{destino or '-'}</td></tr>" for tipo, valor, destino, data in transacoes])
            html = f"""
                <html>
                <head><title>Extrato Bancário</title></head>
                <body>
                <h2>Extrato da Conta</h2>
                <h3>Cliente: {nome}</h3>
                <h4>Data: {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}</h4>
                <table border="1" cellpadding="5">
                    <tr><th>Data</th><th>Tipo</th><th>Valor</th><th>Dest/Rem</th></tr>
                    {linhas}
                    <tr><td colspan="4"><strong>💰 Saldo atual: R$ {saldo:.2f}</strong></td></tr>
                </table>
                </body>
                </html>
                """

        filename = f"extrato{self.conta_atual[0]}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)

        # Garante que o navegador entenda que é um arquivo local
        caminho_absoluto = os.path.abspath(filename)
        webbrowser.open_new_tab(f"file://{caminho_absoluto}") # 🔥 abre o HTML no navegador

    def encerrar_conta(self):
        if self.conta_atual[4] != 0:
            messagebox.showerror("Erro", "Conta só pode ser encerrada com saldo R$ 0.00.")
            return
        confirm = messagebox.askyesno("Confirmar", "Deseja mesmo encerrar a conta? Essa ação é irreversível.")
        if confirm:
            with conectar() as con:
                cur = con.cursor()
                cur.execute("DELETE FROM transacoes WHERE conta_id = ?", (self.conta_atual[0],))
                cur.execute("DELETE FROM contas WHERE id = ?", (self.conta_atual[0],))
            messagebox.showinfo("Encerrado", "Conta encerrada com sucesso.")
            self.conta_atual = None
            self.tela_inicial()

    def solicitar_valor(self, titulo):
        from tkinter import simpledialog
        try:
            return float(simpledialog.askstring(titulo, "Informe o valor:").replace(",", "."))
        except:
            return 0

    def atualizar_conta(self):
        with conectar() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM contas WHERE id = ?", (self.conta_atual[0],))
            return cur.fetchone()

if __name__ == "__main__":
    root = Tk()
    app = BancoApp(root)
    root.mainloop()

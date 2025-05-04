from datetime import datetime
import os

LIMITE_SAQUES = 3
LIMITE = 500
AGENCIA = "0001"

def sacar(conta, valor):
    if valor > conta["saldo"]:
        print("Saldo insuficiente.")
    elif valor > LIMITE:
        print("Valor acima do limite permitido.")
    elif conta["numero_saques"] >= LIMITE_SAQUES:
        print("Número máximo de saques excedido.")
    elif valor <= 0:
        print("Valor inválido.")
    else:
        conta["saldo"] -= valor
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        conta["extrato"] += f"[{timestamp}] Saque: R$ {valor:.2f}\n"
        conta["numero_saques"] += 1
        print("Saque realizado com sucesso.")

def depositar(conta, valor):
    if valor > 0:
        conta["saldo"] += valor
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        conta["extrato"] += f"[{timestamp}] Depósito: R$ {valor:.2f}\n"
        print("Depósito realizado com sucesso.")
    else:
        print("Valor de depósito inválido.")


def exibir_extrato(conta):
    data_atual = datetime.now().strftime("%Y-%m-%d")
    hora_atual = datetime.now().strftime("%H-%M-%S")

    nome_base = f"extrato_{conta['usuario']['nome'].replace(' ', '_')}_conta{conta['numero']}_{data_atual}"
    pasta_extratos = "extratos"

    # Cria a pasta se não existir
    if not os.path.exists(pasta_extratos):
        os.makedirs(pasta_extratos)

    # Conta quantos arquivos da conta existem hoje
    arquivos_hoje = [
        nome for nome in os.listdir(pasta_extratos)
        if nome.startswith(nome_base) and nome.endswith(".txt")
    ]

    if len(arquivos_hoje) >= 2:
        print("⚠️ Limite de 2 exportações de extrato por dia atingido.")
        return

    nome_arquivo = f"{nome_base}_{hora_atual}.txt"
    caminho_arquivo = os.path.join(pasta_extratos, nome_arquivo)

    extrato_str = "\n======= EXTRATO =======\n"
    extrato_str += f"Titular : {conta['usuario']['nome']}\n"
    extrato_str += f"Agência : {conta['agencia']}\n"
    extrato_str += f"Conta   : {conta['numero']}\n"
    extrato_str += f"Data    : {data_atual} {hora_atual}\n"
    extrato_str += "------------------------\n"
    extrato_str += conta["extrato"] if conta["extrato"] else "Nenhuma movimentação."
    extrato_str += f"\n\nSaldo: R$ {conta['saldo']:.2f}\n"
    extrato_str += "=======================\n"

    print(extrato_str)

    with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
        arquivo.write(extrato_str)

    print(f"✅ Extrato salvo em: {caminho_arquivo}")


def criar_usuario(usuarios):
    cpf = input("Informe o CPF (somente números): ")
    if any(u["cpf"] == cpf for u in usuarios):
        print("Usuário já cadastrado.")
        return

    nome = input("Nome completo: ")
    nascimento = input("Data de nascimento (dd/mm/aaaa): ")
    endereco = input("Endereço (logradouro, nro - bairro - cidade/UF): ")

    usuarios.append({
        "nome": nome,
        "data_nascimento": nascimento,
        "cpf": cpf,
        "endereco": endereco
    })
    print("Usuário criado com sucesso!")


def filtrar_usuario(cpf, usuarios):
    for usuario in usuarios:
        if usuario["cpf"] == cpf:
            return usuario
    return None


def criar_conta(usuarios, contas):
    cpf = input("Informe o CPF do titular: ")
    usuario = filtrar_usuario(cpf, usuarios)

    if usuario:
        numero = len(contas) + 1
        conta = {
            "agencia": AGENCIA,
            "numero": numero,
            "usuario": usuario,
            "saldo": 0,
            "extrato": "",
            "numero_saques": 0
        }
        contas.append(conta)
        print(f"Conta criada com sucesso! Número: {numero}")
    else:
        print("Usuário não encontrado. Crie um usuário antes.")


def listar_contas(contas):
    print("\n=== CONTAS CADASTRADAS ===")
    for conta in contas:
        print(f"Agência: {conta['agencia']} | Conta: {conta['numero']} | Titular: {conta['usuario']['nome']}")
    print("===========================\n")


def selecionar_conta(contas):
    numero = int(input("Informe o número da conta: "))
    for conta in contas:
        if conta["numero"] == numero:
            print(f"Conta {numero} selecionada.")
            return conta
    print("Conta não encontrada.")
    return None


def main():
    usuarios = []
    contas = []
    conta_ativa = None

    while True:
        print("""
[d] Depositar
[s] Sacar
[e] Extrato
[nu] Novo Usuário
[nc] Nova Conta
[sc] Selecionar Conta
[lc] Listar Contas
[q] Sair
""")
        opcao = input("Escolha uma opção: ").lower()

        if opcao == "d":
            if conta_ativa:
                valor = float(input("Valor para depósito: "))
                depositar(conta_ativa, valor)
            else:
                print("Nenhuma conta selecionada. Use [sc] para selecionar.")

        elif opcao == "s":
            if conta_ativa:
                valor_str = input("Informe o valor do saque: ").strip()
                if not valor_str.replace(',', '.').replace('.', '', 1).isdigit():
                    print("Operação falhou! Digite um valor numérico válido.")
                    continue

                valor = float(valor_str.replace(',', '.'))
    
                sacar(conta_ativa, valor)
            else:
                print("Nenhuma conta selecionada. Use [sc] para selecionar.")

        elif opcao == "e":
            if conta_ativa:
                exibir_extrato(conta_ativa)
            else:
                print("Nenhuma conta selecionada. Use [sc] para selecionar.")

        elif opcao == "nu":
            criar_usuario(usuarios)

        elif opcao == "nc":
            criar_conta(usuarios, contas)

        elif opcao == "sc":
            conta_ativa = selecionar_conta(contas)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "q":
            print("Saindo do sistema.")
            break

        else:
            print("Opção inválida.")

if __name__ == "__main__":
    main()

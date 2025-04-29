import sys

# Variáveis de controle
saldo = 0.0
limite_saque = 500.0
extrato = ""
numero_saques = 0
LIMITE_SAQUES = 3

# Menu principal
def menu():
    print("""
======== BANCO PYTHON ========
[1] Depósito
[2] Saque
[3] Extrato
[0] Sair
=============================
""")

while True:
    menu()
    opcao = input("Escolha uma opção: ")

    if opcao == "1":
        valor = float(input("Informe o valor do depósito: R$ "))
        if valor > 0:
            saldo += valor
            extrato += f"Depósito: R$ {valor:.2f}\n"
            print("Depósito realizado com sucesso!")
        else:
            print("Valor inválido. Só é possível depositar valores positivos.")

    elif opcao == "2":
        if numero_saques >= LIMITE_SAQUES:
            print("Limite diário de saques atingido.")
            continue

        valor = float(input("Informe o valor do saque: R$ "))
        
        if valor > saldo:
            print("Saldo insuficiente.")
        elif valor > limite_saque:
            print("Valor excede o limite por saque (R$ 500,00).")
        elif valor <= 0:
            print("Valor inválido.")
        else:
            saldo -= valor
            extrato += f"Saque:    R$ {valor:.2f}\n"
            numero_saques += 1
            print("Saque realizado com sucesso!")

    elif opcao == "3":
        print("\n====== EXTRATO ======")
        print(extrato if extrato else "Não foram realizadas movimentações.")
        print(f"\nSaldo atual: R$ {saldo:.2f}")
        print("======================")

    elif opcao == "0":
        print("Obrigado por utilizar o Banco Python!")
        sys.exit()

    else:
        print("Opção inválida. Tente novamente.")

# Desafio DIO: Banco_Python 🌌

## 📒 Descrição
Desenvolver um sistema completo, abordando funcionalidades como criação de contas, transações e segurança.

## 🤖 Tecnologias Utilizadas
- VSCode;
- SQLite3.

## 💡 Explicação simples do desenvolvimento do sistema bancário em Python
  1. Objetivo do Sistema
  -Desenvolver um sistema bancário simples, com interface em terminal, que permita aos usuários:
  -Criar contas com CPF único
  -Realizar login seguro
  -Executar operações como depósito, saque e transferência
  -Consultar extrato de transações

  2. Tecnologias Utilizadas
  -Python: linguagem principal de desenvolvimento
  -SQLite: banco de dados relacional leve e integrado
  -Hashlib: biblioteca para criptografar senhas com SHA-256
  -Datetime: controle de data e hora das transações

  3. Estrutura do Banco de Dados
  -O sistema possui duas tabelas principais:
  -contas: armazena os dados de cada usuário (ID, nome, CPF, senha criptografada, saldo)
  -transacoes: registra todas as operações realizadas (tipo, valor, data, conta relacionada)

  4. Funcionalidades Implementadas
  a) Criação de Contas
  -Verifica CPF único
  -Solicita nome completo e senha
  -Armazena senha com criptografia segura
  b) Login
  -Autenticação por CPF e senha criptografada
  -Retorna a conta ativa para uso nas operações
  c) Saques
  -Permite saque desde que o saldo seja suficiente
  -Limite de 3 saques por dia, controlado por data das transações
  d) Depósitos e Transferências
  -Permitem movimentação de valores entre contas
  -Valida saldo e existência de destino
  e) Extrato
  -Lista todas as transações da conta, com tipo, valor e data/hora

  5. Segurança
  -As senhas dos usuários são protegidas por criptografia SHA-256.
  -Cada transação é registrada com data e hora, permitindo auditoria.
  -O limite diário de saques evita abusos e simula práticas reais de segurança bancária.

## 🚀 Resultados
O sistema alcança o objetivo de simular uma aplicação bancária básica, com foco em segurança, controle financeiro e estrutura de dados relacional. É uma base sólida para futuras evoluções, como interface gráfica, autenticação em dois fatores ou integração com APIs externas.

## 💭 Reflexão
Participar deste curso e desafio foi uma grata experiência, pois mostra que podemos evoluir com os conhecimentos adquiridos, aliados a pesquisas e treinamentos na prática.

## 👨‍💻 Aluno

<p>
    <img 
      align=left 
      margin=10 
      width=80 
      src="https://avatars.githubusercontent.com/u/79292597?s=96&v=4"
    />
    <p>&nbsp&nbsp&nbspJosé Roberto Vasconcellos Lopes<br>
    &nbsp&nbsp&nbsp
    <a href="https://github.com/jrobertovl">GitHub</a>&nbsp;|&nbsp;
    <a href="www.linkedin.com/in/jrobertovl">LinkedIn</a>&nbsp;|&nbsp;
    <a href="https://www.instagram.com/jrobertovl/">Instagram</a>&nbsp;|&nbsp;
    <a href="https://api.whatsapp.com/send?phone=5591982003052">WhatsApp</a></p>
</p>
<br/><br/>
<p>

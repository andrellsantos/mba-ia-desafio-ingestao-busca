from search import search_prompt


def main():
    chain = search_prompt()

    if not chain:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return

    print("Faça sua pergunta (digite 'sair' para encerrar):\n")

    while True:
        pergunta = input("PERGUNTA: ").strip()

        if not pergunta:
            continue

        if pergunta.lower() in {"sair", "exit", "quit"}:
            break

        resposta = chain.invoke(pergunta)
        print(f"RESPOSTA: {resposta}\n")


if __name__ == "__main__":
    main()

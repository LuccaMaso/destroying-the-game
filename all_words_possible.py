import algorithm

def cria_possibilidades(letras, tam_palavra, file, informacoes=""):
    # tam_palavra = int(input("Qual o tamanho da palavra que queremos descobrir? "))
    # letras = input("Quais letras temos? Digite tudo junto (ex: \"aeiou\"): ")
    # informacoes = input("Se conhecemos alguma letra, coloque aqui no formato \"letra_index\" (ex: \"c1 a2 d3\"). Caso contrário, aperte enter: ").split(" ")
    if informacoes == ['']:
        informacoes = []

    letras = algorithm.retira_letras_conhecidas(letras, informacoes)
    palavra_esqueleto = algorithm.cria_esqueleto(tam_palavra, informacoes)
    letras_permutadas = algorithm.permuta_letras(letras, tam_palavra - len(informacoes))
    lista_palavras = algorithm.cria_palavra(letras_permutadas, palavra_esqueleto)
    lista_palavras_reais = algorithm.checa_existencia(lista_palavras)
    for palavra in lista_palavras_reais:
        file.write(palavra)
        file.write("\n")


def main():
    f = open("palavras.txt", "w")
    letras = input("Quais letras temos? Digite tudo junto (ex: \"aeiou\"): ")
    for i in range(3, len(letras)+1):
        cria_possibilidades(letras=letras, tam_palavra=i, file=f)
    f.close()

if __name__  == "__main__":
    main()

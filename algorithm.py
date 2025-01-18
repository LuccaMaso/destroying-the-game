"""
Ideia:

input:
    recebe quantas letras tem a palavra que queremos descobrir
    recebe quantas letras tem as possiveis letras que formam a palavra
    recebe as informaçoes que ja temos: a letra e o index

Algoritmo:
    cria o esqueleto da possivel palavra: quantos caracteres tem e com a informações que já temos
    permuta as possiveis letras em listas com o tamanho das letras que faltam na palavra
    coloca essas permutações na palavra-esqueleto e testa se ela existe
"""

from itertools import permutations
import enchant

def troca_caracter(palavra, letra, index):
    palavra = list(palavra)
    palavra[index] = letra
    palavra = "".join(palavra)
    return palavra

def cria_esqueleto(tam, info):
    palavra = ""
    for _ in range(tam):
        palavra = palavra + "_"
    if not info:
        return palavra
    for elementos in info:
        letra = str(elementos[0])
        index = int(elementos[1])
        palavra = troca_caracter(palavra, letra, index-1)
    return palavra

def permuta_letras(letras, tam):
    return list(permutations(letras, tam))

def enche_esqueleto(palavra, letras):
    index_letras = 0
    for i in range(len(palavra)):
        if palavra[i] == "_":
            palavra = troca_caracter(palavra, letras[index_letras], i)
            index_letras += 1

    return palavra

def cria_palavra(letras_permutadas, palavra_esqueleto):
    lista_palavras = []
    for tuplas in letras_permutadas:
        palavra = enche_esqueleto(palavra_esqueleto, tuplas)
        if palavra not in lista_palavras:
            lista_palavras.append(palavra)
    return lista_palavras

def checa_existencia(lista_palavras):
    dicionario = enchant.Dict("pt_BR")
    lista_palavras_reais = []
    for palavras in lista_palavras:
        if (dicionario.check(palavras)) and palavras not in lista_palavras_reais:
            lista_palavras_reais.append(palavras)
    return lista_palavras_reais

def retira_letras_conhecidas(letras, informacoes):
    lista_letras = list(letras)
    for elementos in informacoes:
        letra = elementos[0]
        lista_letras.remove(letra)
    return "".join(lista_letras)
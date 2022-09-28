from bs4 import BeautifulSoup
import requests
import os
import textdistance
from unidecode import unidecode
from classes import *


LINK_BASE = "https://www.projetoagathaedu.com.br/"
materia = ""
id_atual = 0
enunciados = []
def get_materia(subject):
    teste = requests.get(f"https://www.projetoagathaedu.com.br/banco-de-questoes/{subject}.php")    
    global materia, enunciados
    materia = subject
    page_content = teste.text
    soup = BeautifulSoup(page_content,"lxml")
    supertopicos = soup.select(".accordion")
    pode = 1
    Questoes = []
    for supertopico in supertopicos:#topicos
        titulo_topicos = supertopico.select(".accordion__content")[0].select('h3')#nomes dos topicos
        questoes_topicos = supertopico.select(".accordion__content")[0].select(".painel")#lista de topicos
        titulo_supertopico = supertopico.select(".accordion__label")[0].text
        if "Temas" in titulo_supertopico:
            continue
        print("Supertópico: " + titulo_supertopico)
        if pode:
            questoes_supertopico = get_topicos(titulo_topicos,titulo_supertopico,questoes_topicos)
            Questoes.extend(questoes_supertopico)
    return Questoes
        
def get_topicos(titulos, titulo_supertopico, topicos):
    Questoes = []
    indice_titulo = 0 
    flag = 0
    for topico in topicos:
        #processa topico, associa todos os topicos com o titulo deles (titulos[indice_titulo])
        subtopico = topico.select(".opcao")
        titulo_topico = "Outros"
        if (flag==0 and len(titulos)==len(topicos)) or flag==1:
            print("     -Tópico: " + titulos[indice_titulo].text)
            titulo_topico = titulos[indice_titulo].text
            indice_titulo += 1
        flag = 1
        questoes_topico = get_subtopicos(subtopico,titulo_supertopico, titulo_topico)
        Questoes.extend(questoes_topico)
    return Questoes
        

def get_subtopicos(subtopicos,titulo_supertopico, titulo_topico):
    Questoes = []
    for subtopico in subtopicos:
        #processa as questoes do subtopico
        try:
            link = subtopico.find('a').get('href')
        except AttributeError:
            continue
        titulo_subtopico = subtopico.find("div", class_ = "lista-tema").text
        print("         +Subtópico: "+titulo_subtopico)
        link = link.replace("../",'')
        link = link.replace("./",'')
        questoes_subtopico = get_questoes(LINK_BASE+link,titulo_supertopico,titulo_topico,titulo_subtopico)
        Questoes.extend(questoes_subtopico)
    return Questoes
         
def validar_nome(nome):
    invalido = "\/:*?\"<>| "
    for c in invalido:
        nome = nome.replace(c,'')
    nome = unidecode(nome).lstrip().rstrip()
    return nome

def processa_imagem(imagem_html,link):
    #tratamento dos titulos
    tipo = ""
    if imagem_html.has_attr('src'):
        tipo = 'src'
    elif imagem_html.has_attr('data-src'):
        tipo = 'data-src'
    else:
        return 1
    imagem_html[tipo].replace('../',link)
    extension = imagem_html[tipo].split('.')[-1]
    if '/' in extension:
        return 2
    if "https" not in imagem_html[tipo]:
        if '../' in imagem_html[tipo]:
            response = requests.get(
                f"{link+imagem_html[tipo].replace('../','')}"
            )
        else:
            response = requests.get(
                f"{link+materia+'/'+imagem_html[tipo].replace('../','')}"
            )    
    else:
        response = requests.get(
            f"{imagem_html[tipo]}"
        )
    if response.status_code != 200:
        return 3
    return 0


def processa_enunciado(questao,iterador,link):
    imagens = questao.select("img")
    iterador2 = 0
    status = 1
    for imagem in imagens:
        status = processa_imagem(imagem,link)
        if status!=0:#algo deu errado com o processamento das imagens, cancelar o processamento da questao
            print(f"            Erro de codigo {status} no processamento das imagens da questao {iterador}")
            return TypeError
        iterador2 += 1
    enunciado = ""
    origem = ""
    texto_enunciado = ""
    flag = 0 #nao pegar o primeiro paragrafo (ele nao tem nada)
    for child in questao.findChildren(recursive=False):
        if (child.name == 'p'  or child.name == 'img' or child.name=='div') and flag:
            if child.name=='div':
                for child2 in child.findChildren(recursive=False):
                    if flag==1:#pega a origem da questao, tira o indice e origem do enunciado
                        if child2.name=='img':
                            enunciado += str(child2)
                            continue
                        x = child2.text
                        l = x.find('(')
                        r = x.find(')')
                        origem = x[l+1:r]
                        x = x[r+1:]
                        list(child2.strings)[0].replace_with(x)
                    enunciado += str(child2)
                    flag += 1
            if flag==1:#pega a origem da questao, tira o indice e origem do enunciado
                if child.name=='img' or (child.find('img') and child.text==''):
                    enunciado += str(child)
                    continue
                x = child.text
                l = x.find('(')
                r = x.find(')')
                origem = x[l+1:r]
                x = x[r+1:]
                list(child.strings)[0].replace_with(x)
            texto_enunciado += child.text
            enunciado += str(child)
        flag += 1
    texto_enunciado = texto_enunciado.strip()
    texto_enunciado = texto_enunciado[0:100]
    return enunciado, texto_enunciado, origem

def processa_gabarito(respostas,questao,iterador):#atencao! algumas questoes tem IMAGENS como alternativas
    try:
        alternativas_html = questao.select("ol li")
        if len(alternativas_html)<4: 
            return 
        alternativas = "" 
        for alternativa in alternativas_html:
            imagem = alternativa.select("img")
            if len(imagem): 
                alternativas += str(imagem[0])
            else:
                alternativas += str(alternativa)
        gabarito = respostas[iterador].split('.')[1]
        return alternativas, gabarito
    except AttributeError:
        return

def verifica_duplicacao(atual):
    for quest in enunciados:
        if textdistance.levenshtein.normalized_similarity(atual, quest)>=0.8:
            return 0
    return 1


def get_questoes(link,titulo_supertopico,titulo_topico,titulo_subtopico):
    global id_atual, enunciados
    enunciados = []
    siteQuestoes = requests.get(link)
    page_content = siteQuestoes.text
    soup = BeautifulSoup(page_content,"lxml")
    Questoes = [] #array com questoes do subtopico
    questoes = soup.select(".questoes-enem-vestibular")
    respostas = []
    gabarito_html = soup.select("#gabarito td")
    for resposta in gabarito_html:
        if resposta.text.find(".")==-1:
            continue
        respostas.append(resposta.text)
    if len(respostas)!=len(questoes):
        print("             Organizacao de questoes invalida!")
        return []
    iterador = 0
    LINK_ATUAL = ''.join(temp+'/' for temp in link.split('/')[3:-2])#isso pode quebrar pra outras materias
    for questao in questoes:
        if len(questao.select(".questoes-enem-vestibular")):
            continue
        try:
            alternativas, gabarito = processa_gabarito(respostas,questao,iterador)
            enunciado, texto_enunciado, origem = processa_enunciado(questao,iterador,LINK_BASE+LINK_ATUAL)
            alternativas, gabarito = processa_gabarito(respostas,questao,iterador)
            if verifica_duplicacao(texto_enunciado)==0:
                print(f"             Questao {iterador} duplicada!")
                raise TypeError()
            iterador += 1
            Questoes.append(Questao(id_atual,origem,enunciado,alternativas,gabarito,materia,titulo_supertopico,titulo_topico,titulo_subtopico))
            id_atual += 1
            enunciados.append(texto_enunciado)
        except TypeError:#se alternativas sao imagens, para de processar a questao e segue em frente
            iterador += 1
    return Questoes
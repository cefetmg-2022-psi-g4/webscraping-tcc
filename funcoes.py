from bs4 import BeautifulSoup
import requests
import os
from unidecode import unidecode
from classes import *

LINK_BASE = "https://www.projetoagathaedu.com.br/"

def get_materia(subject):
    teste = requests.get(f"https://www.projetoagathaedu.com.br/banco-de-questoes/{subject}.php")    
    page_content = teste.text
    soup = BeautifulSoup(page_content,"lxml")
    supertopicos = soup.select(".accordion")
    for supertopico in supertopicos:#topicos
        titulo_topicos = supertopico.select(".accordion__content")[0].select('h3')#nomes dos topicos
        questoes_topicos = supertopico.select(".accordion__content")[0].select(".painel")#lista de topicos
        titulo_supertopico = supertopico.select(".accordion__label")[0].text
        if "Temas" in titulo_supertopico:
            continue
        # if "Vest" not in titulo_supertopico:
            # continue
        print("Supertópico: " + titulo_supertopico)
        get_topicos(titulo_topicos,titulo_supertopico,questoes_topicos)
        #SupertopicosObj.add(Supertopico(titulo_supertopico,topicos))

        
def get_topicos(titulos, titulo_supertopico, topicos):
    indice_titulo = 0 
    flag = 0
    # topicosobj = []
    for topico in topicos:
        #processa topico, associa todos os topicos com o titulo deles (titulos[indice_titulo])
        subtopico = topico.select(".opcao")
        titulo_topico = "Outros"
        if (flag==0 and len(titulos)==len(topicos)) or flag==1:
            print("     -Tópico: " + titulos[indice_titulo].text)
            titulo_topico = titulos[indice_titulo].text
            indice_titulo += 1
        flag = 1
        get_subtopicos(subtopico,titulo_supertopico, titulo_topico)
        #topicosobj.add(Topico(titulos[indice_titulo],subtopicos))
        

def get_subtopicos(subtopicos,titulo_supertopico, titulo_topico):
    # subtopicobj = []
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
        get_questoes(LINK_BASE+link,titulo_supertopico,titulo_topico,titulo_subtopico)
        
         
def validar_nome(nome):
    invalido = "\/:*?\"<>| "
    for c in invalido:
        nome = nome.replace(c,'')
    nome = unidecode(nome)
    return nome

def processa_imagem(imagem_html,titulo_supertopico,titulo_topico,titulo_subtopico,it1,it2,link):
    #tratamento dos titulos
    titulo_supertopico = validar_nome(titulo_supertopico) 
    titulo_topico = validar_nome(titulo_topico)
    titulo_subtopico = validar_nome(titulo_subtopico)
    tipo = ""
    if imagem_html.has_attr('src'):
        tipo = 'src'
    else:
        tipo = 'data-src'
    imagem_html[tipo].replace('../',link)
    extension = imagem_html[tipo].split('.')[-1]
    if '/' in extension:
        return
    # print(f"{imagem_html[tipo].replace('../',link)}")
    filename = f"imagens/{titulo_supertopico}/{titulo_topico}/{titulo_subtopico}/{it1}_{it2}."+extension
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as arquivo:
        response = requests.get(
            f"{imagem_html[tipo].replace('../',link)}"
        )
        arquivo.write(response.content)
    imagem_html[tipo] = filename
    # print(imagem_html[tipo])


def processa_enunciado(questao,titulo_supertopico,titulo_topico,titulo_subtopico,iterador,link):
    imagens = questao.select("img")
    iterador2 = 0
    # for imagem in imagens:
        # processa_imagem(imagem,titulo_supertopico,titulo_topico,titulo_subtopico,iterador,iterador2,link)
        # iterador2 += 1
    enunciado = ""
    flag = 0 #nao pegar o primeiro paragrafo (ele nao tem nada)
    for child in questao.findChildren(recursive=False):
        if (child.name == 'p'  or child.name == 'img') and flag:
            if flag==1:#pega a origem da questao, tira o indice e origem do enunciado
                x = child.text
                l = x.find('(')
                r = x.find(')')
                origem = x[l+1:r]
                x = x[r+1:]
                # print(x)
                # print(len(child.select('img')))
                child.string.replace_with(x)
            enunciado += str(child)
        flag += 1
    print("fim")
    return enunciado, origem

def processa_gabarito(respostas,questao,iterador):#atencao! algumas questoes tem IMAGENS como alternativas
    try:
        alternativas_html = questao.select("ol li")
        if len(alternativas_html)!=5: 
            return 
        alternativas = [] 
        for alternativa in alternativas_html:
            imagem = alternativa.select("img")
            if len(imagem): 
                alternativas.append(imagem[0])
                # print(imagem[0])
            else:
                alternativas.append(alternativa.text)

        gabarito = respostas[iterador].split('.')[1]
        return alternativas, gabarito
    except AttributeError:
        return

def get_questoes(link,titulo_supertopico,titulo_topico,titulo_subtopico):
    siteQuestoes = requests.get(link)
    page_content = siteQuestoes.text
    soup = BeautifulSoup(page_content,"lxml")
    questoes_array = []
    questoes = soup.select(".questoes-enem-vestibular")
    respostas = []
    gabarito_html = soup.select("#gabarito td")
    for resposta in gabarito_html:
        if resposta.text.find(".")==-1:
            continue
        respostas.append(resposta.text)

    iterador = 0
    LINK_ATUAL = link.split('/')[3]

    for questao in questoes:
        if len(questao.select(".questoes-enem-vestibular")):
            continue
        try:
            alternativas, gabarito = processa_gabarito(respostas,questao,iterador)
            enunciado, origem = processa_enunciado(questao,titulo_supertopico,titulo_topico,titulo_subtopico,iterador,LINK_BASE+LINK_ATUAL+'/')
            alternativas, gabarito = processa_gabarito(respostas,questao,iterador)
            iterador += 1
            questoes_array.append(Questao(origem,enunciado,alternativas,gabarito))
        except TypeError:#se alternativas sao imagens, para de processar a questao e segue em frente
            print(iterador)
            iterador += 1

    return questoes_array
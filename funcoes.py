from bs4 import BeautifulSoup
import requests
import base64

LINK_BASE = "https://www.projetoagathaedu.com.br/"

def get_materia(subject):
    teste = requests.get(f"https://www.projetoagathaedu.com.br/banco-de-questoes/{subject}.php")    
    page_content = teste.text
    soup = BeautifulSoup(page_content,"html.parser")
    supertopicos = soup.select(".accordion")
    for supertopico in supertopicos:#topicos
        titulo_topicos = supertopico.select(".accordion__content")[0].select('h3')#nomes dos topicos
        questoes_topicos = supertopico.select(".accordion__content")[0].select(".painel")#lista de topicos
        titulo_supertopico = supertopico.select(".accordion__label")[0].text
        print("Supertópico: " + titulo_supertopico)
        get_topicos(titulo_topicos,questoes_topicos)
        #SupertopicosObj.add(Supertopico(titulo_supertopico,topicos))

        
def get_topicos(titulos, topicos):
    indice_titulo = 0 
    flag = 0
    topicosobj = []
    for topico in topicos:
        #processa topico, associa todos os topicos com o titulo deles (titulos[indice_titulo])
        subtopico = topico.select(".opcao")
        titulo_topico = "Outros"
        if (flag==0 and len(titulos)==len(topicos)) or flag==1:
            print("     -Tópico: " + titulos[indice_titulo].text)
            indice_titulo += 1
            titulo_topico = titulos[indice_titulo].text
        flag = 1

        get_subtopicos(subtopico, titulo_topico)
        #topicosobj.add(Topico(titulos[indice_titulo],subtopicos))
        

def get_subtopicos(subtopicos, titulo_topico):
    subtopicobj = []
    for subtopico in subtopicos:
        #processa as questoes do subtopico
        try:
            link = subtopico.find('a').get('href')
        except AttributeError:
            continue
        titulo_subtopico = subtopico.find("div", class_ = "lista-tema").text
        print("         +Subtópico: "+titulo_subtopico)
        #  subtopicobj.add(Subtopico(titulo_subtopico,link))
        print(link)
        get_questoes(LINK_BASE+link[1:], titulo_subtopico, titulo_topico)
        break
         
def processa_imagem(imagem_html):
    stringDaImagem = ''
    with open("temp.jpg", "wb") as arquivo:
        response = requests.get(imagem_html.get('src'))
        arquivo.write(response.content)
        stringDaImagem = base64.b64encode(arquivo.read())
        return stringDaImagem 
        

def processa_enunciado(questao):
    enunciado_html = questao.find_all(recursive=False)
    enunciado = ""
    paragrafos = 0
    for child in enunciado_html:
        if child.name == 'p':
            paragrafos += 1
            imagens = child.select("img")
            for imagem in imagens:
                processa_imagem(imagem)
        if child.name == 'img':
            processa_imagem(child)

def processa_gabarito(respostas,questao,iterador):
    try:
        alternativas_html = questao.select("ol li")
        if len(alternativas_html)==1: 
            return 
        alternativas = [] 
        for alternativa in alternativas_html:
            alternativas.append(alternativa.text)
            print(alternativa)
        gabarito = respostas[iterador].split('.')[1]
        print("resposta: " + gabarito)
        return alternativas, gabarito
    except AttributeError:
        return    

def get_questoes(link):
    siteQuestoes = requests.get(link)
    page_content = siteQuestoes.text
    soup = BeautifulSoup(page_content,"html.parser")
    #ignorar quando as alternativas forem imagens

    questoes = soup.select(".questoes-enem-vestibular")
    respostas = []
    gabarito_html = soup.select("#gabarito td")

    for resposta in gabarito_html:
        if len(resposta.text)==0:
            continue
        respostas.append(resposta.text)

    iterador = 0
    for questao in questoes:
        enuinciado = processa_enunciado(questao)
        alternativas, gabarito = processa_gabarito(respostas)
        iterador += 1
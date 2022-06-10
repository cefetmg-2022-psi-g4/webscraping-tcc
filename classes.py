
# class Supertopico:

#     def __init__(self,nome,topicos):
#         self.nome = nome
#         self.topicos = topicos

#     def __str__(self):
#         return '-Supertópico : ' + self.nome +'\n'+ self.topicos.__str__

# class Topico:
#     def __init__(self,nome,subtopicos):
#         self.nome = nome
#         self.subtopicos = subtopicos

#     def __str__(self):
#         return '  +Topico:' + self.nome +'\n'+ self.subtopicos.__str__

# class Subtopico:
#     def __init__(self,nome,link):
#         self.nome = nome
#         self.link = link

#     def __str__(self):
#         return '   =Subtopico:' + self.nome + self.link


class Questao:
    def __init__(self,origem,enunciado,alternativas,gabarito):
        self.origem = origem
        self.enunciado = enunciado
        self.alternativas = alternativas
        self.gabarito = gabarito
    
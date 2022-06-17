class Questao:
    def __init__(self,identifcador,origem,enunciado,alternativas,gabarito,materia,supertopico,topico,subtopico):
        self.id = identifcador
        self.origem = origem
        self.enunciado = enunciado
        self.alternativas = alternativas
        self.gabarito = gabarito
        self.materia = materia
        self.supertopico = supertopico
        self.topico = topico
        self.subtopico = subtopico
    
    def as_dict(self):
        return {"id": self.id,"origem": self.origem, "enunciado": self.enunciado, "alternativas": self.alternativas,
        "gabarito": self.gabarito, "materia": self.materia, "supertopico": self.supertopico,
        "topico": self.topico, "subtopico": self.subtopico
        }
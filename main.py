from classes import *
from funcoes import *  
import pandas as pd

Questoes = []

materias = ["matematica","biologia","quimica","fisica","historia","linguagens","geografia-sociologia-e-filosofia"]

for materia in materias:
    print(f"Extraindo questoes de {materia}:\n")
    questoes_materia = get_materia(materia)
    print(f"{len(questoes_materia)} questoes de {materia} encontradas.\n")
    Questoes.extend(questoes_materia)

df = pd.DataFrame([x.as_dict() for x in Questoes])

df.to_csv("questoes.csv")

html = df.to_html()

text_file = open("index.html", "w", encoding="utf-8")
text_file.write(html)
text_file.close()

print(df)

print(f"{len(Questoes)} questoes encontradas.")



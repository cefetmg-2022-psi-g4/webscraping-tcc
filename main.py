from classes import *
from funcoes import * 
import pandas as pd
import sqlite3 as sql

Questoes = []

materias = ["matematica","biologia","quimica","fisica","historia","linguagens","geografia-sociologia-e-filosofia"]

for materia in materias:
    print(f"Extraindo questoes de {materia}:\n")
    questoes_materia = get_materia(materia)
    print(f"{len(questoes_materia)} questoes de {materia} encontradas.\n")
    Questoes.extend(questoes_materia)

df = pd.DataFrame([x.as_dict() for x in Questoes])

coneccao = sql.connect('questoes.db')
cursor_sql = coneccao.cursor() 

cursor_sql.execute('CREATE TABLE IF NOT EXISTS questoes(id number PRIMARY KEY, origem text, enunciado text, alternativas text, gabarito char(1), materia text, supertopico text, topico text, subtopico text)')
coneccao.commit()


df.to_csv("questoes.csv")
df.to_sql('questoes',coneccao,if_exists='replace',index = False)

html = df.to_html()

text_file = open("index.html", "w", encoding="utf-8")
text_file.write(html)
text_file.close()

print(df)

print(f"{len(Questoes)} questoes encontradas.")



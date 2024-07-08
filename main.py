import pandas as pd
from geopy.distance import geodesic

#Lê o arquivo CSV

# Pandas lê o arquivo CSV
csv_file_path = "LocalizaçõesEstações.csv"
df = pd.read_csv(csv_file_path)

# Define os dados das estações
numeros_estação = []
nomes_estação = []
coordenadas_Estação = []

# Baseado nas linhas do arquivo, armazena os dados do numero, nome e coordenadas da estação.
for index, row in df.iterrows():
    numero = row['_id']
    nome = row['nome'].split(' - ')[1]  
    coordenada = (row['latitude'], row['longitude'])

    numeros_estação.append(numero)
    nomes_estação.append(nome)
    coordenadas_Estação.append(coordenada)



print(f"{numeros_estação[1]}, {nomes_estação[1]}, {coordenadas_Estação[1]}")


# TESTE DE DISTÂNCIA

def verificaDistância(number1, number2):

    testeDistância = geodesic(coordenadas_Estação[number1], coordenadas_Estação[number2]).kilometers

    print(f"A distância em linha reta entre as estações {nomes_estação[number1]} e {nomes_estação[number2]} é {testeDistância:.2f} km") #:2f é para limitar a a 2 casas decimais a distância

verificaDistância(34, 76)
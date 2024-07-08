import pandas as pd
from geopy.distance import geodesic
import networkx as nx
import matplotlib.pyplot as plt

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

#verificaDistância(34, 76)

# TESTE GRÁFO

class Grafo:
    def __init__(self):
        self.grafo = {} #Dicionario vazio que representa o grafo, a chave são os vertices e os valores são as listas de tuplas representando aresta e peso

    # Adiciona uma aresta ao grafo
    def adiciona_aresta(self, origem, destino, peso):
        #Se o vertice de origem não estiver no grafo, inicializa a lista de grafos
        if origem not in self.grafo:
            self.grafo[origem] = [] #Aqui, o codigo coloca no dicionario um node no qual o vertice é a origem colocado e seus valores uma lista vazia (visto que ele ainda não tem conexões)
        self.grafo[origem].append((destino, peso))
        # Adiciona a tupla (Destino, peso) na lista de adjacencias do vertice de origem
        if destino not in self.grafo:
            self.grafo[destino] = []

    # Imprime o grafo
    def imprime_grafo(self):
        for vertice in self.grafo:
            print(f"{vertice} -> {self.grafo[vertice]}")

    # Teste da representação visual do grafo
    def visualizar_grafo(self):
        grafoNX = nx.Graph()

        # Para cada vertice de origem no dicionario de vertices, desenha um vertice e sua conexão
        for origem in self.grafo:
            for destino, peso in self.grafo[origem]:
                if grafoNX.has_edge(origem,destino):
                    continue #isso verifica se na visualização grafica do grafo, já foi desenhado essa aresta, pois caso já tenha, não se deve duplicar a mesma.
                grafoNX.add_edge(origem,destino, weight=peso) #Adiciona o vertice

        weights = [d['weight'] for u, v, d in grafoNX.edges(data=True)]
        k = sum(weights) / len(weights) #Parametro de distânciamento
        
        layout_Escolhido = nx.spring_layout(grafoNX, k=k, scale=2)
        edges = grafoNX.edges(data=True)
        
        # Desenho do gráfo

        edge_widths = [d['weight'] for u, v, d in edges]
        nx.draw(grafoNX, layout_Escolhido, with_labels=True, node_color='skyblue', node_size= 1500, font_size=10, font_weight='bold', edge_color='gray', width=edge_widths)
        nx.draw_networkx_edge_labels(grafoNX, layout_Escolhido, edge_labels={(u, v): d['weight'] for u, v, d in edges}, font_color='red')

        plt.title("Vizualização do Gráfo")
        plt.show()



        

grafo = Grafo()
grafo.adiciona_aresta("riomar", "recife", 5)
grafo.adiciona_aresta("plaza", "recife", 10)
grafo.adiciona_aresta("tacaruna", "riomar", 15)
grafo.adiciona_aresta("tacaruna", "plaza", 15)
grafo.adiciona_aresta("recife", "plaza", 15)
grafo.imprime_grafo()
grafo.visualizar_grafo()
import pandas as pd
from geopy.distance import geodesic
import networkx as nx
import matplotlib.pyplot as plt

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

#print(f"{numeros_estação[1]}, {nomes_estação[1]}, {coordenadas_Estação[1]}")

# TESTE DE DISTÂNCIA
#def verificaDistância(number1, number2):

    #testeDistância = geodesic(coordenadas_Estação[number1], coordenadas_Estação[number2]).kilometers

    #print(f"A distância em linha reta entre as estações {nomes_estação[number1]} e {nomes_estação[number2]} é {testeDistância:.2f} km") #:2f é para limitar a a 2 casas decimais a distância

#verificaDistância(60, 76)

# TESTE GRÁFO
class Grafo:
    def __init__(self):
        self.grafo = {}  # Dicionario vazio que representa o grafo, a chave são os vértices e os valores são as listas de tuplas representando aresta e peso

    # Adiciona uma aresta ao grafo
    def adiciona_aresta(self, origem, destino, peso):
        #Se o vértice de origem não estiver no grafo, inicializa a lista de grafos
        if origem not in self.grafo:
            self.grafo[origem] = []  # Aqui, o código coloca no dicionário um nó no qual o vértice é a origem colocado e seus valores uma lista vazia (visto que ele ainda não tem conexões)
        self.grafo[origem].append((destino, peso))
        #Adiciona a tupla (Destino, peso) na lista de adjacências do vértice de origem
        if destino not in self.grafo:
            self.grafo[destino] = []
        self.grafo[destino].append((origem, peso))  # Adiciona a aresta no sentido contrário para grafos não-direcionados

    # Imprime o grafo
    def imprime_grafo(self):
        for vertice in self.grafo:
            print(f"{vertice} -> {self.grafo[vertice]}")

    #Teste da representação visual do grafo
    def visualizar_grafo(self):
        grafoNX = nx.Graph()

        # Para cada vértice de origem no dicionário de vértices, desenha um vértice e sua conexão
        for origem in self.grafo:
            for destino, peso in self.grafo[origem]:
                if grafoNX.has_edge(origem, destino):
                    continue  #Isso verifica se na visualização gráfica do grafo, já foi desenhada essa aresta, pois caso já tenha, não se deve duplicar a mesma.
                grafoNX.add_edge(origem, destino, weight=peso)  #Adiciona o vértice

        weights = [d['weight'] for u, v, d in grafoNX.edges(data=True)]
        k = sum(weights) / len(weights)  #Parâmetro de distanciamento

        layout_Escolhido = nx.spring_layout(grafoNX, k=k, scale=20)
        edges = grafoNX.edges(data=True)

        #Desenho do grafo
        edge_widths = [d['weight'] for u, v, d in edges]
        nx.draw(grafoNX, layout_Escolhido, with_labels=True, node_color='orange', node_size=800, font_size=5, font_weight='bold', edge_color='black', width=edge_widths)
        nx.draw_networkx_edge_labels(grafoNX, layout_Escolhido, edge_labels={(u, v): d['weight'] for u, v, d in edges}, font_color='red')

        plt.title("Visualização do Grafo")
        plt.show()

    def Bellman_ford(self, vertice_origem, vertice_destino):
        # Define as distâncias do vértice de origem como infinito
        distancias = {vertice: float("inf") for vertice in self.grafo}
        distancias[vertice_origem] = 0

        # Relaxa todas as arestas |V| - 1 vezes
        for _ in range(len(self.grafo) - 1):
            for vertice in self.grafo:
                for vertice_vizinho, peso_aresta in self.grafo[vertice]:
                    if distancias[vertice] + peso_aresta < distancias[vertice_vizinho]:
                        distancias[vertice_vizinho] = distancias[vertice] + peso_aresta

        # Verifica a existência de ciclos de peso negativo
        for vertice in self.grafo:
            for vertice_vizinho, peso_aresta in self.grafo[vertice]:
                if distancias[vertice] + peso_aresta < distancias[vertice_vizinho]:
                    print("ciclo de peso negativo")
                    return

        # Caso não tenha ligação entre eles
        if distancias[vertice_destino] == float("inf"):
            print(f"Não há um caminho do vértice {vertice_origem} para {vertice_destino}")
            return None

        # Printa a distância requerida
        print(f"Menor distância de {vertice_origem} para {vertice_destino} é: {distancias[vertice_destino]}")
        return distancias[vertice_destino]

def main():
    grafoEstações = Grafo()
    listapeso = []
    #Loop que conecta todos os vertices entre si seguindo a logica da proximidade minima de distância
    for i in range(len(coordenadas_Estação)):
        for j in range(i+1, len(coordenadas_Estação)):
            peso = geodesic(coordenadas_Estação[i], coordenadas_Estação[j]).kilometers
            listapeso.append(round(peso, 2))
            if peso < 0.75:
                grafoEstações.adiciona_aresta(nomes_estação[i], nomes_estação[j], round(peso, 2))

    grafoEstações.visualizar_grafo()
main()
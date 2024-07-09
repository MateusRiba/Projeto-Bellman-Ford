import pandas as pd
from geopy.distance import geodesic
import networkx as nx
import matplotlib.pyplot as plt
import random

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

#Classe que define grafo e o algoritmo de Bellman-Ford
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

    #Verifica se o grafo é completamente conexo
    def é_conexo(self):
        visitados = set()
        def dfs(vértice):
            visitados.add(vértice)
            for vizinho, _ in self.grafo[vértice]:
                if vizinho not in visitados:
                    dfs(vizinho)
        
         #1Inicia a DFS a partir do primeiro vértice do grafo
        dfs(next(iter(self.grafo)))
        return len(visitados) == len(self.grafo)

    # Imprime o grafo
    def imprime_grafo(self):
        for vertice in self.grafo:
            print(f"{vertice} -> {self.grafo[vertice]}")

    #Teste da representação visual do grafo
    def visualizar_grafo(self):
        grafoNX = nx.DiGraph()

        # Para cada vértice de origem no dicionário de vértices, desenha um vértice e sua conexão
        for origem in self.grafo:
            for destino, peso in self.grafo[origem]:
                if grafoNX.has_edge(origem, destino):
                    continue  #Isso verifica se na visualização gráfica do grafo, já foi desenhada essa aresta, pois caso já tenha, não se deve duplicar a mesma.
                grafoNX.add_edge(origem, destino, weight=peso)  #Adiciona o vértice

        layout_Escolhido = nx.spring_layout(grafoNX)
        edges = grafoNX.edges(data=True)

        #Desenho do grafo
        edge_widths = [d['weight'] for u, v, d in edges]
        nx.draw_networkx(grafoNX, layout_Escolhido, with_labels= True, node_color='orange', node_size=500, font_size=5, font_weight='bold', edge_color='blue', width=edge_widths, arrows= True)

        plt.title("Visualização do Grafo")
        plt.show()

    def Bellman_ford(self, vertice_origem, vertice_destino):
        # Define as distâncias do vértice de origem como infinito
        distancias = {vertice: float("inf") for vertice in self.grafo}
        distancias[vertice_origem] = 0

        # Rastreia o predecessor de cada vértice para reconstruir o caminho
        predecessores = {vertice: None for vertice in self.grafo}

        # Relaxa todas as arestas |V| - 1 vezes
        for _ in range(len(self.grafo) - 1):
            for vertice in self.grafo:
                for vertice_vizinho, peso_aresta in self.grafo[vertice]:
                    if distancias[vertice] + peso_aresta < distancias[vertice_vizinho]:
                        distancias[vertice_vizinho] = distancias[vertice] + peso_aresta
                        predecessores[vertice_vizinho] = vertice

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
        print(f"Menor distância de {vertice_origem} para {vertice_destino} é: {distancias[vertice_destino]} Kilometros")

        # Reconstrói o caminho
        caminho = []
        passo = vertice_destino
        while passo is not None:
            caminho.append(passo)
            passo = predecessores[passo]
        caminho = caminho[::-1]  # Inverte o caminho

        print(f"Caminho: {' -> '.join(caminho)}")
        return distancias[vertice_destino], caminho

def main():
    grafoEstações = Grafo()
    listaDistâncias = []
    # Loop que conecta todos os vértices entre si seguindo a lógica da proximidade mínima de distância
    for i in range(len(coordenadas_Estação)):
        for j in range(i+1, len(coordenadas_Estação)):
            peso = geodesic(coordenadas_Estação[i], coordenadas_Estação[j]).kilometers #Biblioteca geodesic pega a tupla de coordenadas e compara, transformando em uma distância em KM
            listaDistâncias.append((nomes_estação[i], nomes_estação[j], round(peso, 2)))
    
    # Dicionario que armazena as arestas de cada vertice
    arestas = {nome: [] for nome in nomes_estação}

    # Coloca as distâncias calculadas no dicionario
    for origem, destino, peso in listaDistâncias:
        arestas[origem].append((destino, peso))
        arestas[destino].append((origem, peso))

    # ordena e adiciona as 2 menores arestas de cada vertice no grafo1
    for origem in arestas:
        arestas[origem].sort(key=lambda x: x[1])  # Ordena para pegar as menores distâncias
        i = 0
        for destino, peso in arestas[origem][:8]:  # Pega as 2 menores
                grafoEstações.adiciona_aresta(origem, destino, round(peso, 2))

    # Impede que o grafo fique desconexo
    listaDistâncias.append((nomes_estação[69], nomes_estação[89], round(peso, 2)))
    grafoEstações.adiciona_aresta("Mercado do Cordeiro", "CCS UFPE", round(geodesic(coordenadas_Estação[69], coordenadas_Estação[89]).kilometers, 2))
    grafoEstações.adiciona_aresta("R. Verdes Mares", "Praça Massangana", round(geodesic(coordenadas_Estação[56], coordenadas_Estação[60]).kilometers, 2))
    grafoEstações.adiciona_aresta("Casa da Cultura", "Pina", round(geodesic(coordenadas_Estação[9], coordenadas_Estação[51]).kilometers, 2))
    grafoEstações.adiciona_aresta("Mercado Novo Água Fria", "Praia da Casa Caiada", round(geodesic(coordenadas_Estação[74], coordenadas_Estação[68]).kilometers, 2))
    grafoEstações.adiciona_aresta("Faculdade Damas", "R. Adalberto Camargo", round(geodesic(coordenadas_Estação[41], coordenadas_Estação[40]).kilometers, 2))
    grafoEstações.adiciona_aresta("Plaza Casa Forte", "Praça da Torre", round(geodesic(coordenadas_Estação[84], coordenadas_Estação[88]).kilometers, 2))

    #Loop de interação com o usuario
    while True:
        pergunta1 = input("Digite '1' caso queira ver uma distância minima aleatoria entre 2 estações de Bike \nDigite '2' caso queira escolher quais estações comparar\n")
        
        if pergunta1 == "1":
            origem_random = random.choice(nomes_estação)
            destino_random = random.choice(nomes_estação)
            while destino_random == origem_random:
                destino_random = random.choice(nomes_estação)
            print(f"Estação de origem: {origem_random}, Estação de destino: {destino_random}")
            grafoEstações.Bellman_ford(origem_random, destino_random)
            grafoEstações.visualizar_grafo() #AQUI DEVE TER MODIFICAÇÔES
            break
        
        elif pergunta1 == '2':
            estaçãoOrigem = input("Você Digitou 2!\nEscreva qual a estação de origem: ")
            estaçãoDestino = input("Agora escreva qual a estação destino: ")
            
            if estaçãoOrigem not in nomes_estação or estaçãoDestino not in nomes_estação:
                print("Ops! Digite 2 estações existentes! Você pode verificar seus nomes aqui:\n")
                print(f"{nomes_estação}\n")
            else:
                grafoEstações.Bellman_ford(estaçãoOrigem, estaçãoDestino)
                grafoEstações.visualizar_grafo() #AQUI DEVE TER MODIFICAÇÕES
                break
                
        elif pergunta1 != '2' or pergunta1 != '1': 
            print("Digite uma opção valida")
   
main()

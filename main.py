import pandas as pd
from geopy.distance import geodesic
import networkx as nx
import matplotlib.pyplot as plt
import random
import tkinter as tk
from tkinter import ttk, messagebox

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
        # Se o vértice de origem não estiver no grafo, inicializa a lista de grafos
        if origem not in self.grafo:
            self.grafo[origem] = []  # Aqui, o código coloca no dicionário um nó no qual o vértice é a origem colocado e seus valores uma lista vazia (visto que ele ainda não tem conexões)
        self.grafo[origem].append((destino, peso))
        # Adiciona a tupla (Destino, peso) na lista de adjacências do vértice de origem
        if destino not in self.grafo:
            self.grafo[destino] = []
        self.grafo[destino].append((origem, peso))  # Adiciona a aresta no sentido contrário para grafos não-direcionados

    # Verifica se o grafo é completamente conexo
    def é_conexo(self):
        visitados = set()
        def dfs(vértice):
            visitados.add(vértice)
            for vizinho, _ in self.grafo[vértice]:
                if vizinho not in visitados:
                    dfs(vizinho)

        # Inicia a DFS a partir do primeiro vértice do grafo
        dfs(next(iter(self.grafo)))
        return len(visitados) == len(self.grafo)

    # Imprime o grafo
    def imprime_grafo(self):
        for vertice in self.grafo:
            print(f"{vertice} -> {self.grafo[vertice]}")

    # Teste da representação visual do grafo
    def visualizar_grafo(self, caminho=None):
        grafoNX = nx.DiGraph()

        # Para cada vértice de origem no dicionário de vértices, desenha um vértice e sua conexão
        for origem in self.grafo:
            for destino, peso in self.grafo[origem]:
                if grafoNX.has_edge(origem, destino):
                    continue  # Isso verifica se na visualização gráfica do grafo, já foi desenhada essa aresta, pois caso já tenha, não se deve duplicar a mesma.

                # Escolhe a cor da aresta com base na existência do caminho e se a aresta está no caminho
                edge_color = 'blue'
                if caminho and (origem, destino) in caminho:
                    edge_color = 'red'  # Aresta no caminho é vermelha

                grafoNX.add_edge(origem, destino, weight=peso, color=edge_color)  # Adiciona a aresta com a cor escolhida

        layout_Escolhido = nx.spring_layout(grafoNX)
        edges = grafoNX.edges(data=True)

        # Desenho do grafo
        edge_widths = [d['weight'] for u, v, d in edges]
        edge_colors = [d['color'] for u, v, d in edges]
        nx.draw_networkx(grafoNX, layout_Escolhido, with_labels=True, node_color='orange', node_size=500, font_size=5, font_weight='bold', edge_color=edge_colors, width=edge_widths, arrows=True)

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
        distancias[vertice_destino] = round(distancias[vertice_destino], 2)
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
        for destino, peso in arestas[origem][:2]:  # Pega as 2 menores
                grafoEstações.adiciona_aresta(origem, destino, round(peso, 2))

    # Impede que o grafo fique desconexo
    listaDistâncias.append((nomes_estação[69], nomes_estação[89], round(peso, 2)))
    grafoEstações.adiciona_aresta("Mercado do Cordeiro", "CCS UFPE", round(geodesic(coordenadas_Estação[69], coordenadas_Estação[89]).kilometers, 2))
    grafoEstações.adiciona_aresta("R. Verdes Mares", "Praça Massangana", round(geodesic(coordenadas_Estação[56], coordenadas_Estação[60]).kilometers, 2))
    grafoEstações.adiciona_aresta("Casa da Cultura", "Pina", round(geodesic(coordenadas_Estação[9], coordenadas_Estação[51]).kilometers, 2))
    grafoEstações.adiciona_aresta("Mercado Novo Água Fria", "Praia da Casa Caiada", round(geodesic(coordenadas_Estação[74], coordenadas_Estação[68]).kilometers, 2))
    grafoEstações.adiciona_aresta("Faculdade Damas", "R. Adalberto Camargo", round(geodesic(coordenadas_Estação[41], coordenadas_Estação[40]).kilometers, 2))
    grafoEstações.adiciona_aresta("Plaza Casa Forte", "Praça da Torre", round(geodesic(coordenadas_Estação[84], coordenadas_Estação[88]).kilometers, 2))

    
    Aplicativo(grafoEstações)
    #Fim da main
#Classe da interface gráfica
class Aplicativo():
    def __init__(self, estações):
        self.grafoEstações = estações
        self.root = tk.Tk()
        self.tela()
        self.frames_tela()
        self.widgets_frame_1()
        self.lista_frame_2()
        self.root.mainloop()
    
    def tela(self):
        self.root.title("Sistemas de Estações de Bike")
        self.root.configure(background='#4682B4')
        self.root.geometry("640x480")
        self.root.resizable(False, False)
    
    def frames_tela(self):
        self.frame_1 = tk.Frame(self.root, bd=4, bg='#B0C4DE', highlightbackground='#708090', highlightthickness=3)
        self.frame_1.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.46)
        
        self.frame_2 = tk.Frame(self.root, bd=4, bg='#B0C4DE', highlightbackground='#708090', highlightthickness=3)
        self.frame_2.place(relx=0.02, rely=0.5, relwidth=0.96, relheight=0.46)
    
    def widgets_frame_1(self):
        self.bt_estacao_aleatoria = tk.Button(self.frame_1, text="Estações Aleatórias", background='#C0C0C0', bd=2, command=self.estacoes_aleatorias)
        self.bt_estacao_aleatoria.place(relx=0.04, rely=0.62, relwidth=0.18, relheight=0.08)
        
        self.bt_escolhe_estacao = tk.Button(self.frame_1, text="Escolher Estações", background='#C0C0C0', bd=2, command=self.escolher_estacoes)
        self.bt_escolhe_estacao.place(relx=0.04, rely=0.48, relwidth=0.18, relheight=0.08)
        
        self.lb_titulo = tk.Label(self.frame_1, text='Sistema de Estações de Bike do Recife', background='#B0C4DE', font=('bold'))
        self.lb_titulo.place(relx=0.04, rely=0.05)
        
        self.lb_inicial = tk.Label(self.frame_1, text='Estação inicial', background='#B0C4DE')
        self.lb_inicial.place(relx=0.04, rely=0.2)
        
        self.entry_inicial = tk.Entry(self.frame_1)
        self.entry_inicial.place(relx=0.18, rely=0.2, relwidth=0.28)
        
        self.lb_final = tk.Label(self.frame_1, text='Estação final', background='#B0C4DE')
        self.lb_final.place(relx=0.04, rely=0.34)
        
        self.entry_final = tk.Entry(self.frame_1)
        self.entry_final.place(relx=0.18, rely=0.34, relwidth=0.28)
    
    def lista_frame_2(self):
        self.lista_estacoes = ttk.Treeview(self.frame_2, height=3, column=('col1'))
        self.lista_estacoes.heading('#0', text='')
        self.lista_estacoes.heading('#1', text='Nome')
        
        self.lista_estacoes.column('#0', width=1)
        self.lista_estacoes.column('#1', width=599)
        self.lista_estacoes.place(relx=0.01, rely=0.1, relwidth=0.95, relheight=0.85)
        
        self.scrollLista = ttk.Scrollbar(self.frame_2, orient='vertical')
        self.lista_estacoes.configure(yscrollcommand=self.scrollLista.set)
        self.scrollLista.place(relx=0.96, rely=0.1, relwidth=0.04, relheight=0.85)
    
    def estacoes_aleatorias(self):
        self.fechar_janela_atual()
        origem_random = random.choice(nomes_estação)
        destino_random = random.choice(nomes_estação)
        while destino_random == origem_random:
            destino_random = random.choice(nomes_estação)

        resultado, caminho = self.grafoEstações.Bellman_ford(origem_random, destino_random)
        if resultado is not None:
            self.abrir_janela_resultados(resultado, caminho)
            self.grafoEstações.visualizar_grafo(caminho)  # Passa o caminho encontrado para visualização
    
    def escolher_estacoes(self):
        origem = self.entry_inicial.get()
        destino = self.entry_final.get()
        if origem != "" and destino != "":
            if origem in nomes_estação and destino in nomes_estação:
                self.fechar_janela_atual()
                resultado, caminho = self.grafoEstações.Bellman_ford(origem, destino)
                if resultado is not None:
                    self.abrir_janela_resultados(resultado, caminho)
                    self.grafoEstações.visualizar_grafo(caminho)  # Passa o caminho encontrado para visualização
            else:
                messagebox.showerror("Erro", "Por favor, escolha estações válidas.")
        else:
            messagebox.showerror("Erro", "Por favor, preencha ambos os campos.")

    
    def fechar_janela_atual(self):
        self.root.destroy()
    
    def abrir_janela_resultados(self, resultado, caminho):
        nova_janela = tk.Tk()
        nova_janela.title("Resultados")
        nova_janela.configure(background='#4682B4')
        nova_janela.geometry("640x480")
        
        frame_resultados = tk.Frame(nova_janela, bd=4, bg='#B0C4DE', highlightbackground='#708090', highlightthickness=3)
        frame_resultados.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.96)
        
        resultado_texto = f"Menor distância: {resultado} km\nCaminho: {' -> '.join(caminho)}"
        resultado_label = tk.Text(frame_resultados, wrap=tk.WORD, background='#B0C4DE')
        resultado_label.insert(tk.END, resultado_texto)
        resultado_label.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)
        
        nova_janela.mainloop()

   
main()
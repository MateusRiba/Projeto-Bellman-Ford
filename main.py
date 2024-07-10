import pandas as pd
from geopy.distance import geodesic
import networkx as nx
import matplotlib.pyplot as plt
import random
import tkinter as tk
from tkinter import ttk


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
    @staticmethod
    def calculo_random():
        origem_random = random.choice(nomes_estação)
        destino_random = random.choice(nomes_estação)
        while destino_random == origem_random:
            destino_random = random.choice(nomes_estação)

        resultado, caminho = grafoEstações.Bellman_ford(origem_random, destino_random)
        if resultado is not None:
            grafoEstações.visualizar_grafo()
            tk.resultado_label.config(text=f"Menor distância: {resultado} km\nCaminho: {' -> '.join(caminho)}")
    def calculo_escolhido(origem, destino):
        resultado, caminho = grafoEstações.Bellman_ford(origem, destino)
        if resultado is not None:
            grafoEstações.visualizar_grafo()
            tk.resultado_label.config(text=f"Menor distância: {resultado} km\nCaminho: {' -> '.join(caminho)}")

    def abrir_janela_random():
        calculo_random()
    def abrir_janela_escolhido():
        def calcular():
            origem = origem_entry.get()
            destino = destino_entry.get()
            if origem != "" and destino != "":
                if origem in nomes_estação and destino in nomes_estação:
                    calculo_escolhido(origem, destino)
                    window.destroy()
                else:
                    tk.messagebox.showerror("Erro", "Por favor, escolha estações válidas.")
            else:
                tk.messagebox.showerror("Erro", "Por favor, preencha ambos os campos.")

        window = tk.Toplevel(tk.root)
        window.title("Escolher Estações")
        window.geometry("300x150")

        origem_label = tk.ttk.Label(window, text="Estação de Origem:")
        origem_label.pack(pady=5)
        origem_entry = tk.ttk.Entry(window)
        origem_entry.pack()

        destino_label = tk.ttk.Label(window, text="Estação de Destino:")
        destino_label.pack(pady=5)
        destino_entry = tk.ttk.Entry(window)
        destino_entry.pack()

        calcular_button = tk.ttk.Button(window, text="Calcular", command=calcular)
        calcular_button.pack(pady=10)
    Aplicativo()
    # Função para iniciar a interface gráfica
class Aplicativo():
    def __init__(self):
        root = tk.Tk()
        self.root = root
        self.tela()
        self.frames_tela()
        self.widgets_frame_1()
        self.lista_frame_2()
        root.mainloop()
    
    def tela(self): #janela do aplicativo
        self.root.title("Sistemas de Estações de Bike")
        self.root.configure(background='#4682B4')
        self.root.geometry("640x480")
        self.root.resizable(False, False)
    def frames_tela(self): #cria os quadros na janela onde vão aparecer a informação 
        self.frame_1 = tk.Frame(self.root, bd=4, bg='#B0C4DE', highlightbackground='#708090', highlightthickness=3)
        self.frame_1.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.46)
        
        self.frame_2 = tk.Frame(self.root, bd=4, bg='#B0C4DE', highlightbackground='#708090', highlightthickness=3)
        self.frame_2.place(relx=0.02, rely=0.5, relwidth=0.96, relheight=0.46)
    def widgets_frame_1(self):
        #criação botão de estações aleatórias
        self.bt_estacao_aleatoria = tk.Button(self.frame_1, text="Estações Aleatórias",background='#C0C0C0', bd=2)
        self.bt_estacao_aleatoria.place(relx=0.04, rely=0.82, relwidth=0.18, relheight=0.08)
        #criação botão usuário escolhe as estações
        self.bt_escolhe_estacao = tk.Button(self.frame_1, text="Escolher Estações",background='#C0C0C0', bd=2)
        self.bt_escolhe_estacao.place(relx=0.04, rely=0.68, relwidth=0.18, relheight=0.08)
        
        #criando label sistema de estações de bike Recife
        self.lb_titulo = tk.Label(self.frame_1, text='Sistema de Estações de Bike do Recife', background='#B0C4DE', font=('bold'))
        self.lb_titulo.place(relx=0.04, rely=0.1)
        
        
        #criando label estação inicial e entrada da estação
        self.lb_inicial = tk.Label(self.frame_1, text='Estação inicial', background='#B0C4DE')
        self.lb_inicial.place(relx=0.04, rely=0.4)
        
        self.entry_inicial = tk.Entry(self.frame_1)
        self.entry_inicial.place(relx=0.18, rely=0.4, relwidth=0.28)
        #criando label estação final e entrada da estação
        self.lb_final = tk.Label(self.frame_1, text='Estação final', background='#B0C4DE')
        self.lb_final.place(relx=0.04, rely=0.54)
        
        self.entry_final = tk.Entry(self.frame_1)
        self.entry_final.place(relx=0.18, rely=0.54, relwidth=0.28)
    def lista_frame_2(self):
        self.lista_estacoes = ttk.Treeview(self.frame_2, height=3, column=('col1'))
        self.lista_estacoes.heading('#0',text='')
        self.lista_estacoes.heading('#1',text='Nome')
        
        self.lista_estacoes.column('#0', width=1)
        self.lista_estacoes.column('#1', width=599)
        self.lista_estacoes.place(relx=0.01, rely=0.1, relwidth=0.95, relheight=0.85)
        
        self.scrollLista = ttk.Scrollbar(self.frame_2, orient='vertical')
        self.lista_estacoes.configure(yscrollcommand=self.scrollLista.set)
        self.scrollLista.place(relx=0.96, rely=0.1, relwidth=0.04, relheight=0.85)
    
    """root = tk.Tk()
    root.title("Sistema de Estações de Bike")
    root.geometry("480x320")
    root.configure(background='#4682B4')

    titulo_label = ttk.Label(root, text="Escolha uma opção:")
    titulo_label.pack(pady=10)

    random_button = ttk.Button(root, text="Distância entre Estações Aleatórias", command=abrir_janela_random)
    random_button.pack(pady=5)

    escolher_button = ttk.Button(root, text="Escolher Estações", command=abrir_janela_escolhido)
    escolher_button.pack(pady=5)

    resultado_label = ttk.Label(root, text="")
    resultado_label.pack(pady=10)

    root.mainloop()"""
   
main()
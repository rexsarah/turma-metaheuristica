import time
import random
import numpy as np

class BuscaTabu:
    def __init__(self, matriz_custos, tamanho_tabu=10, max_iter=100):
        """
        Inicializa o algoritmo de Busca Tabu para o problema de atribuição

        Args:
            matriz_custos: matriz de custos empresa x projeto
            tamanho_tabu: tamanho da lista tabu
            max_iter: número máximo de iterações
        """
        self.matriz_custos = np.array(matriz_custos)
        self.n = len(matriz_custos)  # número de empresas/projetos
        self.tamanho_tabu = tamanho_tabu
        self.max_iter = max_iter
        self.lista_tabu = []  # Lista que armazena movimentos proibidos

    def calcular_custo(self, solucao):
        """
        Calcula o custo total de uma solução

        Args:
            solucao: lista onde o índice é a empresa e o valor é o projeto atribuído

        Returns:
            Custo total da solução
        """
        custo_total = 0
        for empresa, projeto in enumerate(solucao):
            custo_total += self.matriz_custos[empresa, projeto]
        return custo_total

    def gerar_solucao_inicial(self):
        """
        Gera uma solução inicial válida aleatória

        Returns:
            Uma solução inicial onde cada empresa está atribuída a um projeto distinto
        """
        # Atribuição aleatória: cada empresa a um projeto diferente
        projetos = list(range(self.n))
        random.shuffle(projetos)
        return projetos

    def gerar_vizinhanca(self, solucao_atual):
        """
        Gera vizinhança por trocas de projetos entre duas empresas

        Args:
            solucao_atual: solução atual

        Returns:
            Lista de vizinhos (movimentos possíveis)
        """
        vizinhos = []
        for i in range(self.n):
            for j in range(i+1, self.n):
                # Troca de projetos entre duas empresas
                novo_vizinho = solucao_atual.copy()
                novo_vizinho[i], novo_vizinho[j] = novo_vizinho[j], novo_vizinho[i]

                # O movimento é representado pelo par de empresas que trocam projetos
                movimento = (i, j)
                vizinhos.append((novo_vizinho, movimento))
        return vizinhos

    def busca_tabu(self):
        """
        Implementa o algoritmo de Busca Tabu

        Returns:
            melhor_solucao: a melhor solução encontrada
            melhor_custo: o custo da melhor solução
        """
        tempo_inicio = time.time()

        # Gerar solução inicial
        solucao_atual = self.gerar_solucao_inicial()
        melhor_solucao = solucao_atual.copy()

        custo_atual = self.calcular_custo(solucao_atual)
        melhor_custo = custo_atual

        iter_sem_melhorias = 0

        for iteracao in range(self.max_iter):
            # Verificar tempo de execução
            if time.time() - tempo_inicio > 15:  # Limite de 15 segundos
                break

            # Gerar vizinhança
            vizinhos = self.gerar_vizinhanca(solucao_atual)

            # Encontrar o melhor vizinho que não está na lista tabu
            # ou que satisfaz o critério de aspiração
            melhor_vizinho = None
            melhor_movimento = None
            melhor_custo_vizinho = float('inf')

            for vizinho, movimento in vizinhos:
                custo_vizinho = self.calcular_custo(vizinho)

                # Verifica se o movimento não está na lista tabu ou se satisfaz o critério de aspiração
                if movimento not in self.lista_tabu or custo_vizinho < melhor_custo:
                    if custo_vizinho < melhor_custo_vizinho:
                        melhor_vizinho = vizinho
                        melhor_movimento = movimento
                        melhor_custo_vizinho = custo_vizinho

            # Atualizar solução atual
            if melhor_vizinho:
                solucao_atual = melhor_vizinho
                custo_atual = melhor_custo_vizinho

                # Adicionar movimento à lista tabu
                self.lista_tabu.append(melhor_movimento)
                if len(self.lista_tabu) > self.tamanho_tabu:
                    self.lista_tabu.pop(0)  # Remove o movimento mais antigo

                # Atualizar melhor solução global
                if custo_atual < melhor_custo:
                    melhor_solucao = solucao_atual.copy()
                    melhor_custo = custo_atual
                    iter_sem_melhorias = 0
                else:
                    iter_sem_melhorias += 1

            # Critério de parada por estagnação
            if iter_sem_melhorias > 20:
                # Intensificação/Diversificação: reiniciar com nova solução
                if random.random() < 0.3:  # 30% de chance de reiniciar
                    solucao_atual = self.gerar_solucao_inicial()
                    custo_atual = self.calcular_custo(solucao_atual)
                    iter_sem_melhorias = 0

        # Convertendo para o formato de saída desejado (empresa -> projeto)
        resultado = melhor_solucao.copy()

        return resultado, melhor_custo

def main():
    # Matriz de custos do problema (empresa x projeto)
    matriz_custos = [
        [12, 18, 15, 22, 9, 14, 20, 11, 17],
        [19, 8, 13, 25, 16, 10, 7, 21, 24],
        [6, 14, 27, 10, 12, 19, 23, 16, 8],
        [17, 11, 20, 9, 18, 13, 25, 14, 22],
        [10, 23, 16, 14, 7, 21, 12, 19, 15],
        [13, 25, 9, 17, 11, 8, 16, 22, 20],
        [21, 16, 24, 12, 20, 15, 9, 18, 10],
        [8, 19, 11, 16, 22, 17, 14, 10, 13],
        [15, 10, 18, 21, 13, 12, 22, 9, 16]
    ]

    # Inicializar e executar a busca tabu
    busca = BuscaTabu(matriz_custos, tamanho_tabu=15, max_iter=200)
    tempo_inicio = time.time()
    melhor_solucao, melhor_custo = busca.busca_tabu()
    tempo_total = time.time() - tempo_inicio

    # Output dos resultados
    print(f"Tempo de execução: {tempo_total:.4f} segundos")
    print(f"Melhor custo encontrado: {melhor_custo}")
    print("Atribuição de empresas a projetos:")
    for empresa, projeto in enumerate(melhor_solucao):
        print(f"Empresa {empresa+1} -> Projeto {projeto+1} (Custo: {matriz_custos[empresa][projeto]})")

    # Verificar se a solução é válida (cada projeto atribuído a exatamente uma empresa)
    projetos_atribuidos = melhor_solucao.copy()
    if len(set(projetos_atribuidos)) == len(projetos_atribuidos):
        print("Solução válida: cada projeto está atribuído a exatamente uma empresa.")
    else:
        print("Solução inválida: há projetos duplicados.")

if __name__ == "__main__":
    main()
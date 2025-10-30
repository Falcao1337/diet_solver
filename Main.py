import pandas as pd
from ortools.linear_solver import pywraplp

#Ler CSV
nutrientes = pd.read_csv('nutrientes.csv')
data = pd.read_csv('data.csv')

#Normalização
nutrientes['nome'] = nutrientes['nome'].str.strip().str.lower()
data.columns = [c.strip().lower() for c in data.columns]

#Criando Solver
solver = pywraplp.Solver.CreateSolver('GLOP')
if not solver:
    raise Exception("Erro ao criar solver. Verifique se o OR-Tools está instalado.")

#Dicionário
alimentos = {
    row['ingrediente']: solver.NumVar(0, solver.infinity(), row['ingrediente'])
    for _, row in data.iterrows()
}

#Restrição
for _, nutriente in nutrientes.iterrows():
    nome = nutriente['nome']
    minimo = nutriente['minimo']

    solver.Add(
        sum(data.loc[i, nome] * alimentos[data.loc[i, 'ingrediente']] for i in range(len(data))) >= minimo
    )

#Função Objetivo
solver.Minimize(
    sum(data.loc[i, 'preco'] * alimentos[data.loc[i, 'ingrediente']] for i in range(len(data)))
)

status = solver.Solve()

if status == pywraplp.Solver.OPTIMAL:
    print("\n✅ Solução ótima encontrada!\n")
    print(f"Custo total mínimo: R$ {solver.Objective().Value():.2f}\n")

    print("Quantidade ideal de cada alimento:")
    for ingrediente, var in alimentos.items():
        quantidade = var.solution_value()
        if quantidade > 0:
            print(f"- {ingrediente}: {quantidade:.3f} porções")

else:
    print("❌ Nenhuma solução ótima encontrada.")

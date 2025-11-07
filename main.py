import sqlite3
from datetime import date, datetime
import matplotlib.pyplot as plt
import csv

DB_PATH = "fittrack.db"


# Conexão com o banco

def conectar():
    return sqlite3.connect(DB_PATH)


# Inicializar tabelas

def init_db():
    con = conectar()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        idade INTEGER,
        altura_cm REAL,
        peso_inicial_kg REAL,
        objetivo TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS treinos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        data TEXT NOT NULL,
        exercicio TEXT NOT NULL,
        duracao_min INTEGER,
        calorias INTEGER,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS progresso (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT NOT NULL,
        peso REAL NOT NULL,
        meta REAL NOT NULL,
        dieta TEXT,
        frequencia INTEGER
    )
    """)

    con.commit()
    con.close()


# Gerar treino

def gerar_treino(objetivo, local, dias):
    treino_base = {
        "A": ["Peito e tríceps", "Supino reto 4x10", "Crucifixo 3x12", "Tríceps corda 4x10", "Tríceps banco 3x12"],
        "B": ["Costas e bíceps", "Puxada frontal 4x10", "Remada curvada 4x10", "Rosca direta 3x12", "Rosca alternada 3x12"],
        "C": ["Pernas", "Agachamento 4x10", "Leg press 4x10", "Cadeira extensora 3x12", "Cadeira flexora 3x12"],
        "D": ["Ombros e abdômen", "Desenvolvimento 4x10", "Elevação lateral 3x12", "Prancha 3x30s", "Abdominal infra 3x20"],
        "E": ["Cardio e Core", "Corrida 20min", "Prancha 3x30s", "Abdominal supra 3x20"]
    }

    chaves = list(treino_base.keys())
    treino_final = {}
    for i in range(dias):
        letra = chaves[i % len(chaves)]
        treino_final[f"Dia {i+1}"] = treino_base[letra]
    return treino_final


# Exportar treino para CSV

def exportar_treino_para_csv(nome_usuario, plano, objetivo):
    arquivo = "treino_{}.csv".format(nome_usuario.lower().replace(" ", "_"))

    with open(arquivo, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Usuario", "Objetivo", "Dia", "Grupo", "Exercicio"])
        for dia, lista in plano.items():
            grupo = lista[0]
            for exercicio in lista[1:]:
                writer.writerow([nome_usuario, objetivo, dia, grupo, exercicio])

    print(f"\n📂 Dados exportados com sucesso para {arquivo}")


# Gerar treino para usuário

def gerar_treino_para_usuario():
    nome = input("Nome: ")
    objetivo = input("Objetivo (ganhar massa / perder gordura / manter forma): ").lower()
    local = input("Local (casa / academia): ").lower()
    dias = int(input("Quantos dias por semana quer treinar? (1-6): "))

    print("\nGerando treino personalizado...\n")
    plano = gerar_treino(objetivo, local, dias)

    print(f"Treino gerado automaticamente para {nome} ({objetivo}):\n")
    for dia, lista in plano.items():
        print(f"{dia}: {lista[0]}")
        for exercicio in lista[1:]:
            print(f" - {exercicio}")
        print()

    exportar_treino_para_csv(nome, plano, objetivo)


# Progresso e previsão com gráfico

def registrar_progresso():
    print("\n=== Acompanhamento e Previsão ===\n")

    peso_inicial = float(input("Peso inicial (kg): "))
    peso_atual = float(input("Peso atual (kg): "))
    meta = float(input("Meta de peso (kg): "))
    frequencia = int(input("Dias de treino por semana (1-7): "))
    dieta = input("Qualidade da dieta (ruim / media / boa / excelente): ").lower()

    progresso = (peso_atual - peso_inicial) / (meta - peso_inicial)
    progresso = max(0, min(progresso, 1))

    if dieta == "ruim":
        taxa_dieta = 0.4
    elif dieta == "media":
        taxa_dieta = 0.7
    elif dieta == "boa":
        taxa_dieta = 1.0
    else:
        taxa_dieta = 1.2

    taxa_treino = frequencia / 7
    taxa_semanal = taxa_dieta * taxa_treino * 0.12
    faltante = 1 - progresso
    semanas_restantes = faltante / taxa_semanal if taxa_semanal > 0 else 0

    data_prevista = date.today()
    if semanas_restantes > 0:
        dias_estimados = int(semanas_restantes * 7)
        data_prevista = date.today().fromordinal(date.today().toordinal() + dias_estimados)

    print("\n📊 RESULTADO DA ANÁLISE")
    print(f"Progresso atual: {progresso*100:.1f}% da meta atingida.")
    if semanas_restantes > 0:
        print(f"⏱️ Estimativa: {semanas_restantes:.1f} semanas (~{dias_estimados} dias) para atingir a meta.")
        print(f"📅 Data aproximada de alcance: {data_prevista.strftime('%d/%m/%Y')}")
    else:
        print("🎯 Meta atingida! Parabéns!")

    # salvar no banco
    con = conectar()
    cur = con.cursor()
    cur.execute("INSERT INTO progresso (data, peso, meta, dieta, frequencia) VALUES (?, ?, ?, ?, ?)",
                (str(date.today()), peso_atual, meta, dieta, frequencia))
    con.commit()
    con.close()

    # gerar gráfico
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT data, peso, meta FROM progresso ORDER BY data")
    dados = cur.fetchall()
    con.close()

    if len(dados) < 2:
        print("\n📉 Registre mais de um dia para gerar o gráfico de progresso.")
        return

    datas = [datetime.strptime(d[0], "%Y-%m-%d") for d in dados]
    pesos = [d[1] for d in dados]
    metas = [d[2] for d in dados]

    # projeção (corrigida)
    ultima_data = datas[-1]
    dias_proj = (data_prevista - ultima_data.date()).days  # corrigido
    peso_proj = [pesos[-1], meta]
    datas_proj = [ultima_data, datetime.combine(data_prevista, datetime.min.time())]

    plt.figure(figsize=(8, 5))
    plt.plot(datas, pesos, marker='o', label="Peso Atual", color="dodgerblue")
    plt.plot(datas, metas, linestyle="--", label="Meta", color="limegreen")
    plt.plot(datas_proj, peso_proj, linestyle="--", color="orange", label="Projeção de Tendência")
    plt.title("Evolução e Projeção do Peso — FitTrack")
    plt.xlabel("Data")
    plt.ylabel("Peso (kg)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# Menu principal

def menu():
    while True:
        print("\n=== FitTrack AI Trainer ===")
        print("1) Inicializar banco")
        print("2) Gerar treino automático")
        print("6) Acompanhar progresso e previsão")
        print("0) Sair")
        op = input("Escolha: ")

        if op == "1":
            init_db()
            print("✅ Banco inicializado com sucesso!")
        elif op == "2":
            gerar_treino_para_usuario()
        elif op == "6":
            registrar_progresso()
        elif op == "0":
            print("Saindo... até mais!")
            break
        else:
            print("Opção inválida. Tente novamente.")


# Execução principal

if __name__ == "__main__":
    try:
        init_db()  # garante que o banco exista
    except Exception as e:
        print(f"⚠️ Erro ao inicializar banco: {e}")
    menu()

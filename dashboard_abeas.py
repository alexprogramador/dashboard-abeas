import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np

st.set_page_config(page_title="Dashboard ABEAS 2025-2026", layout="wide")

# =========================================================
# FUNÇÃO PARA ALIMENTAR O BANCO COM OS NOVOS DADOS
# =========================================================
def inicializar_banco():
    conn = sqlite3.connect("abeas.db")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS indicadores")
    cursor.execute("""
        CREATE TABLE indicadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            indicador TEXT,
            valor REAL,
            ano INTEGER,
            tipo TEXT
        )
    """)
    
    # Dados extraídos das suas tabelas [Source 1 e 2]
    dados = [
        # REALIZADO 2025
        ("Impacto Direto Total", 1028, 2025, "Geral"),
        ("Impacto Indireto Total", 3321, 2025, "Geral"),
        ("Famílias Beneficiadas", 1028, 2025, "Geral"),
        ("Voluntários Totais", 30, 2025, "Recursos Humanos"),
        ("Atendidos Diretos SCFV", 99, 2025, "SCFV"),
        ("Idosos SCFV", 52, 2025, "SCFV"),
        ("Adultos SCFV", 47, 2025, "SCFV"),
        ("Horas de Oficina SCFV", 1032, 2025, "SCFV"),
        ("Atendimentos Serviço Social", 907, 2025, "Social"),
        ("Cestas Básicas Doadas", 1310, 2025, "Alimentação"),
        ("Quilos de Alimento", 19650, 2025, "Alimentação"),
        ("Jiu-Jitsu (Crianças/Adol)", 77, 2025, "Esporte"),
        ("Atendimentos Psicologia", 2208, 2025, "Saúde"),
        
        # METAS 2026
        ("Impacto Direto Total", 1051, 2026, "Geral"),
        ("Impacto Indireto Total", 3000, 2026, "Geral"),
        ("Famílias Beneficiadas", 1000, 2026, "Geral"),
        ("Voluntários Totais", 100, 2026, "Recursos Humanos"),
        ("Atendidos Diretos SCFV", 99, 2026, "SCFV"),
        ("Idosos SCFV", 90, 2026, "SCFV"),
        ("Adultos SCFV", 30, 2026, "SCFV"),
        ("Horas de Oficina SCFV", 1032, 2026, "SCFV"),
        ("Atendimentos Serviço Social", 2000, 2026, "Social"),
        ("Cestas Básicas Doadas", 1310, 2026, "Alimentação"),
        ("Quilos de Alimento", 20000, 2026, "Alimentação"),
        ("Jiu-Jitsu (Crianças/Adol)", 100, 2026, "Esporte"),
        ("Atendimentos Psicologia", 2208, 2026, "Saúde"),
    ]
    
    cursor.executemany("INSERT INTO indicadores (indicador, valor, ano, tipo) VALUES (?, ?, ?, ?)", dados)
    conn.commit()
    conn.close()

# Inicializa o banco (pode comentar após a primeira execução se preferir)
inicializar_banco()

# =========================
# CONEXÃO E CARREGAMENTO
# =========================
conn = sqlite3.connect("abeas.db")
df = pd.read_sql("SELECT * FROM indicadores", conn)
df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

# =========================
# TÍTULO E LAYOUT
# =========================
st.title("📊 Dashboard Estratégico ABEAS")
st.markdown("### Acompanhamento de Resultados 2025 vs Metas 2026")

# =========================
# FILTROS LATERAIS
# =========================
st.sidebar.header("🔎 Parâmetros de Análise")
anos = st.sidebar.multiselect("Selecione os Anos", sorted(df["ano"].unique()), default=[2025, 2026])
categorias = st.sidebar.multiselect("Categorias", df["tipo"].unique(), default=df["tipo"].unique())

df_filtrado = df[(df["ano"].isin(anos)) & (df["tipo"].isin(categorias))]

# =========================
# MÉTRICAS PRINCIPAIS
# =========================
st.subheader("📌 Indicadores Chave de Impacto")
c1, c2, c3, c4 = st.columns(4)

def get_val(ind, ano):
    val = df[(df["indicador"] == ind) & (df["ano"] == ano)]["valor"].values
    return val[0] if len(val) > 0 else 0

# Exemplo de delta comparando meta 2026 vs realizado 2025
direto_25 = get_val("Impacto Direto Total", 2025)
direto_26 = get_val("Impacto Direto Total", 2026)
volunt_25 = get_val("Voluntários Totais", 2025)
volunt_26 = get_val("Voluntários Totais", 2026)

c1.metric("Pessoas Impactadas (2025)", f"{int(direto_25)}")
c2.metric("Meta Impacto (2026)", f"{int(direto_26)}", f"{round(((direto_26/direto_25)-1)*100,1)}%")
c3.metric("Voluntários (2025)", f"{int(volunt_25)}")
c4.metric("Meta Voluntários (2026)", f"{int(volunt_26)}", f"{int(volunt_26 - volunt_25)} pessoas")

# =========================
# GRÁFICOS COMPARATIVOS
# =========================
st.divider()
col_esq, col_dir = st.columns(2)

st.subheader("📊 Comparativo Detalhado: Realizado 2025 vs Meta 2026")

# Criando a tabela dinâmica
pivot_df = df_filtrado.pivot_table(
    index="indicador", 
    columns="ano", 
    values="valor", 
    aggfunc="sum"
).dropna()

if not pivot_df.empty:
    # Para diminuir o 'pulo' da escala e torná-la mais precisa:
    # Usamos o st.bar_chart com configurações de eixo
    st.bar_chart(
        pivot_df, 
        height=500, 
        use_container_width=True,
        # O parâmetro x_label e y_label ajudam na clareza
        x_label="Indicadores",
        y_label="Quantidade / Valor Absoluto",
    )
    
    st.info("💡 Dica: Passe o mouse sobre as barras para ver o valor exato com precisão decimal.")
else:
    st.info("Selecione os indicadores nos filtros para visualizar.")

with col_dir:
   st.subheader("🎯 Metas Planejadas para 2026")

# 1. Filtrar apenas os dados de 2026
df_metas = df[df["ano"] == 2026]

# 2. Preparar os dados (ordenar do maior para o menor)
resumo_metas = df_metas.groupby("indicador")["valor"].sum().sort_values(ascending=True)

if not resumo_metas.empty:
    # 3. Criar a figura com TAMANHO REDUZIDO (8 de largura, 6 de altura)
    fig_meta, ax_meta = plt.subplots(figsize=(8, 6)) 
    
    # 4. Gerar as barras (Verde suave)
    bars = ax_meta.barh(resumo_metas.index, resumo_metas.values, color='#52BE80')
    
    # 5. Adicionar os rótulos com os valores das metas
    for bar in bars:
        width = bar.get_width()
        ax_meta.text(
            width + (resumo_metas.max() * 0.01), 
            bar.get_y() + bar.get_height()/2, 
            f'{int(width)}', 
            va='center', 
            fontsize=9, # Fonte levemente menor
            weight='bold'
        )

    # 6. Estilização Compacta
    ax_meta.set_title("Metas por Indicador - 2026", fontsize=11, pad=15)
    ax_meta.tick_params(axis='y', labelsize=8) # Nomes dos indicadores menores
    
    # Limpeza visual (remover bordas)
    ax_meta.spines['right'].set_visible(False)
    ax_meta.spines['top'].set_visible(False)
    ax_meta.spines['bottom'].set_visible(False)
    ax_meta.set_xticks([]) # Remove o eixo X para ganhar espaço, já que o valor está na ponta da barra
    
    plt.tight_layout()
    
    # Exibir no Streamlit (pode usar o parâmetro use_container_width=False para forçar o tamanho fixo)
    st.pyplot(fig_meta)
else:
    st.warning("Sem dados de metas para 2026.")

# =========================
# ANÁLISE DE DESEMPENHO (LOGICA DE METAS)
# =========================
st.subheader("🎯 Status das Metas 2026")

for ind in df["indicador"].unique():
    v25 = get_val(ind, 2025)
    v26 = get_val(ind, 2026)
    
    # Cálculo da porcentagem de variação
    if v25 > 0:
        variacao = ((v26 - v25) / v25) * 100
        texto_porcentagem = f"{variacao:+.1f}%" # Exibe com sinal de + ou -
    else:
        texto_porcentagem = "Novo Indicador"

    # Lógica de exibição com as cores e ícones
    if v26 > v25:
        st.info(f"**{ind}**: Objetivo de crescer de {int(v25)} para {int(v26)} (**{texto_porcentagem}**) 📈")
    
    elif v26 == v25:
        st.success(f"**{ind}**: Manter a excelência de {int(v25)} (**0.0% de variação**) ✅")
    
    else:
        # Para casos de redução planejada (como Impacto Indireto ou Adultos no SCFV)
        st.warning(f"**{ind}**: Ajuste planejado de {int(v25)} para {int(v26)} (**{texto_porcentagem}**) ⚠️")

# =========================
# MACHINE LEARNING & PREVISÃO
# =========================
st.divider()
st.subheader("🤖 Projeção de Tendência")
indicador_sel = st.selectbox("Selecione um indicador para ver a tendência:", df["indicador"].unique())

dados_ml = df[df["indicador"] == indicador_sel].sort_values("ano")
if len(dados_ml) >= 2:
    X = dados_ml["ano"].values.reshape(-1, 1)
    y = dados_ml["valor"].values
    modelo = LinearRegression().fit(X, y)
    
    ano_futuro = np.array([[2027]])
    predicao = modelo.predict(ano_futuro)[0]
    
    st.write(f"Baseado na evolução 2025-2026, a estimativa para **2027** é de: **{round(predicao, 2)}**")
else:
    st.write("Dados insuficientes para calcular tendência linear.")

# =========================
# TABELA E EXPORTAÇÃO
# =========================
with st.expander("🔎 Ver Base de Dados Completa"):
    st.dataframe(df_filtrado, use_container_width=True)
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button("Baixar Dados (CSV)", csv, "indicadores_abeas.csv", "text/csv")

conn.close()
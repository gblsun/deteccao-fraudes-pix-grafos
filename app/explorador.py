"""Explorador interativo da pesquisa (Streamlit).

Rodar na raiz do repositório:
    streamlit run app/explorador.py

Abas:
    Rede inteira       todas as contas, com filtros, busca e linha do tempo (pixfraud.explorer)
    Conta              ficha da conta, trilha do dinheiro (comum ou temporal)
    Padrões de fraude  gera e desenha os padrões de pixfraud.patterns
    Fluxo e bloqueio   fluxo máximo, corte mínimo e contas a bloquear (pixfraud.flow)
    Resultados         métricas dos detectores e testes estatísticos

Os dados vêm de data/synthetic (gerados na primeira execução, se não existirem).
Outra pasta pode ser usada com a variável de ambiente PIXFRAUD_DADOS.
"""

import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx  # noqa: E402
import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402
import streamlit.components.v1 as components  # noqa: E402

from pixfraud.anomaly import DETECTORS  # noqa: E402
from pixfraud.experiment import load_experiment_config, prepare, run_detectors  # noqa: E402
from pixfraud.explorer import network_explorer_html  # noqa: E402
from pixfraud.features import FEATURE_SETS  # noqa: E402
from pixfraud.flow import blocking_accounts, blocking_cut, max_money_flow  # noqa: E402
from pixfraud.graph import describe, money_trail  # noqa: E402
from pixfraud.patterns import PATTERNS  # noqa: E402
from pixfraud.simulation import generate_dataset, load_config, load_dataset, save_dataset  # noqa: E402
from pixfraud.stats import compare_groups  # noqa: E402
from pixfraud.temporal import temporal_trail  # noqa: E402
from pixfraud.visualization import draw_graph, explain_account, graph_html  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "experimento.yaml"
DATA_DIR = Path(os.environ.get("PIXFRAUD_DADOS", ROOT / "data" / "synthetic"))
DIRECTIONS = {"para frente (para onde foi)": "forward", "para trás (de onde veio)": "backward", "os dois": "both"}

st.set_page_config(page_title="Explorador Pix", layout="wide")


@st.cache_data(show_spinner="Carregando o dataset...")
def load(data_dir: str):
    """Contas e Pix da pasta; gera o dataset sintético se ela ainda estiver vazia."""
    path = Path(data_dir)
    if not (path / "transactions.csv").exists():
        save_dataset(*generate_dataset(load_config(CONFIG)), path)
    return load_dataset(path)


@st.cache_resource(show_spinner="Montando o grafo e calculando os atributos...")
def prepared(data_dir: str):
    """Grafo, atributos e rótulos, calculados uma vez e guardados entre as interações."""
    accounts, transactions = load(data_dir)
    return prepare(accounts, transactions, load_experiment_config(CONFIG))


@st.cache_data(show_spinner="Rodando o detector...")
def risk_scores(data_dir: str, model: str, feature_set: str) -> pd.Series:
    """Escore de risco de cada conta para o detector e o conjunto escolhidos na barra lateral."""
    data = prepared(data_dir)
    config = load_experiment_config(CONFIG)
    return DETECTORS[model](data.features[FEATURE_SETS[feature_set]], **config["modelos"][model]).scores


@st.cache_data(show_spinner="Desenhando a rede inteira...")
def explorer_page(data_dir: str, model: str, feature_set: str) -> str:
    """HTML da aba "Rede inteira" (ver ``pixfraud.explorer``)."""
    accounts, transactions = load(data_dir)
    info = accounts.set_index("account_id")
    return network_explorer_html(
        prepared(data_dir).graph, transactions=transactions, roles=roles_with_victims(info),
        risk=risk_scores(data_dir, model, feature_set), title="Rede Pix sintética",
        subtitle=f"Risco: {model} com atributos '{feature_set}'.",
    )


@st.cache_data(show_spinner="Avaliando todos os detectores...")
def all_metrics(data_dir: str) -> pd.DataFrame:
    """Métricas de todos os detectores × conjuntos de atributos, para a aba "Resultados"."""
    data = prepared(data_dir)
    metrics, _ = run_detectors(data.features, data.labels, load_experiment_config(CONFIG)["modelos"])
    return metrics


def roles_with_victims(info: pd.DataFrame) -> pd.Series:
    """Papel de cada conta, com as vítimas de golpe destacadas como ``vitima``."""
    return info["role"].where(~info["is_victim"], "vitima") if "is_victim" in info else info["role"]


def with_roles(graph, roles: pd.Series):
    """Cópia do grafo com o atributo ``role`` em cada vértice (para colorir os desenhos)."""
    graph = graph.copy()
    for v in graph:
        graph.nodes[v]["role"] = roles.get(v, "?")
    return graph


data_dir = str(DATA_DIR)
accounts, transactions = load(data_dir)
data = prepared(data_dir)
info = accounts.set_index("account_id")
roles = roles_with_victims(info)

st.sidebar.title("Explorador Pix")
st.sidebar.caption(f"{len(accounts):,} contas · {len(transactions):,} Pix".replace(",", "."))
model = st.sidebar.selectbox("Detector", sorted(DETECTORS), index=sorted(DETECTORS).index("dbscan"))
feature_set = st.sidebar.selectbox("Conjunto de atributos", list(FEATURE_SETS), index=list(FEATURE_SETS).index("completo"))
risk = risk_scores(data_dir, model, feature_set)

tab_net, tab_account, tab_patterns, tab_flow, tab_results = st.tabs(
    ["Rede inteira", "Conta", "Padrões de fraude", "Fluxo e bloqueio", "Resultados"]
)

with tab_net:
    st.caption("Clique numa conta para ver os vizinhos; use a linha do tempo para ver a rede crescer dia a dia.")
    components.html(explorer_page(data_dir, model, feature_set), height=780, scrolling=False)

with tab_account:
    ranking = risk.sort_values(ascending=False)
    options = list(ranking.index[:50])
    col_pick, col_manual = st.columns([2, 1])
    picked = col_pick.selectbox("Uma das 50 contas mais suspeitas", options,
                                format_func=lambda a: f"{a} ({roles.get(a, '?')})")
    typed = col_manual.text_input("…ou digite uma conta", "")
    account = typed.strip() if typed.strip() in data.graph else picked
    fig = explain_account(with_roles(data.graph, roles), data.features[FEATURE_SETS[feature_set]], risk, account,
                          fraud=data.labels)
    st.pyplot(fig)
    plt.close(fig)

    st.subheader("Trilha do dinheiro")
    c1, c2, c3 = st.columns(3)
    direction = c1.radio("Direção", list(DIRECTIONS), horizontal=False)
    hops = c2.slider("Saltos", 1, 6, 2)
    temporal = c3.checkbox("Respeitar a ordem dos Pix (trilha temporal)", value=False,
                           help="Só segue Pix que acontecem depois de o dinheiro chegar à conta.")
    if temporal and DIRECTIONS[direction] == "both":
        st.info("A trilha temporal é feita numa direção de cada vez; usando 'para frente'.")
    if temporal:
        trail = temporal_trail(transactions, account, direction="backward" if DIRECTIONS[direction] == "backward" else "forward",
                               max_hops=hops)
        trail.add_node(account)
    else:
        trail = money_trail(data.graph, account, max_hops=hops, direction=DIRECTIONS[direction])
    st.write(f"{trail.number_of_nodes()} contas e {trail.number_of_edges()} relações na trilha.")
    if trail.number_of_nodes() > 400:
        st.warning("Trilha grande demais para desenhar com clareza: diminua os saltos.")
    else:
        components.html(graph_html(with_roles(trail, roles), title=f"Trilha de {account}"), height=560)

with tab_patterns:
    c1, c2 = st.columns([1, 2])
    name = c1.selectbox("Padrão", list(PATTERNS))
    size = c1.slider("Tamanho (vítimas, contas na cadeia…)", 2, 12, 4)
    pattern = PATTERNS[name](size)
    fig, ax = plt.subplots(figsize=(8, 5))
    draw_graph(pattern, ax=ax, title=name)
    c2.pyplot(fig)
    plt.close(fig)
    c1.dataframe(describe(pattern).astype(str))

with tab_flow:
    st.caption("Quanto dinheiro pode ter ido das origens ao destino, e o que bloquear para interromper o fluxo "
               "(teorema do fluxo máximo e corte mínimo). O grafo agregado ignora a ordem dos Pix.")
    collectors = list(info.index[info["role"] == "coletor"])
    sink = st.selectbox("Destino (ex.: um coletor)", collectors or list(data.graph)[:1])
    # Sugestão de origens: as vítimas que pagaram alguma conta da quadrilha deste coletor.
    fraud_graph = data.graph.subgraph(info.index[info["is_fraud"]])
    ring = {v for v in fraud_graph if nx.has_path(fraud_graph, v, sink)}
    default_sources = sorted({u for m in ring for u in data.graph.predecessors(m) if roles.get(u) == "vitima"})[:15]
    sources = st.multiselect("Origens (ex.: as vítimas da quadrilha)", sorted(data.graph), default=default_sources)
    if sources:
        value, _ = max_money_flow(data.graph, sources, sink)
        cut_value, cut = blocking_cut(data.graph, sources, sink)
        accounts_to_block = blocking_accounts(data.graph, sources, sink)
        m1, m2, m3 = st.columns(3)
        m1.metric("Fluxo máximo", f"R$ {value:,.0f}".replace(",", "."))
        m2.metric("Valor do corte mínimo", f"R$ {cut_value:,.0f}".replace(",", "."))
        m3.metric("Contas a bloquear", "—" if accounts_to_block is None else len(accounts_to_block))
        st.write("Pix do corte mínimo:")
        st.dataframe(pd.DataFrame(cut, columns=["origem", "destino", "valor"]))
        if accounts_to_block:
            st.write("Menor conjunto de contas a bloquear:",
                     ", ".join(f"{a} ({roles.get(a, '?')})" for a in accounts_to_block))

with tab_results:
    st.subheader("Detectores × conjuntos de atributos")
    st.dataframe(all_metrics(data_dir).round(3))
    robust = ROOT / "reports" / "results" / "robustez_resumo.csv"
    if robust.exists():
        st.subheader("Robustez (várias sementes)")
        st.dataframe(pd.read_csv(robust).round(3))
    st.subheader("Fraude × normal em cada atributo")
    st.caption("Mann-Whitney com correção de Holm; o delta de Cliff mede o tamanho do efeito.")
    st.dataframe(compare_groups(data.features, data.labels).round(4))

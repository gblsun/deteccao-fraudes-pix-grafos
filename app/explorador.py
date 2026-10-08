"""Explorador interativo da pesquisa (Streamlit).

Rodar na raiz do repositório (só neste computador):
    streamlit run app/explorador.py --server.address localhost

Na barra lateral, escolha a **semente** (digitando ou por um atalho) e o
**cenário**, e clique em "Gerar rede": a rede é gerada na hora, com todos os
modelos pontuados (não supervisionados e supervisionados). Depois escolha o
modelo que pinta o risco e quantas contas seriam investigadas (top-k).

Abas:
    Resumo             os números da rede e o desempenho do modelo escolhido
    Rede inteira       todas as contas, com filtros, linha do tempo e o modo "Acertos" (pixfraud.explorer)
    Ranking            as contas mais suspeitas do modelo, com o gabarito
    Modelos            a AP de todos os modelos nesta rede
    Conta              ficha da conta e trilha do dinheiro (comum ou temporal)
    Padrões de fraude  gera e desenha os padrões de pixfraud.patterns
    Fluxo e bloqueio   fluxo máximo, corte mínimo e contas a bloquear (pixfraud.flow)
    Resultados         estudos com várias sementes e testes estatísticos por atributo

Com a variável de ambiente PIXFRAUD_DADOS apontando para uma pasta, o app
também oferece aquele dataset salvo (ex.: o AMLworld importado).
"""

import os
import random
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx  # noqa: E402
import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402
import streamlit.components.v1 as components  # noqa: E402

from pixfraud.experiment import load_experiment_config, load_scenarios, prepare  # noqa: E402
from pixfraud.exploration import (  # noqa: E402
    SUPERVISED,
    UNSUPERVISED,
    all_model_scores,
    generate_network,
    network_summary,
    picker_entries,
    rank_models,
    top_k_outcome,
)
from pixfraud.explorer import network_explorer_html  # noqa: E402
from pixfraud.features import FEATURE_SETS  # noqa: E402
from pixfraud.flow import blocking_accounts, blocking_cut, max_money_flow  # noqa: E402
from pixfraud.graph import describe, money_trail  # noqa: E402
from pixfraud.patterns import PATTERNS  # noqa: E402
from pixfraud.simulation import load_dataset  # noqa: E402
from pixfraud.stats import compare_groups  # noqa: E402
from pixfraud.temporal import temporal_trail  # noqa: E402
from pixfraud.visualization import INK_SECONDARY, draw_graph, explain_account, graph_html  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CONFIGS = {"padrão": ROOT / "configs" / "experimento.yaml",
           "otimizada": ROOT / "configs" / "experimento_otimizado.yaml"}
SCENARIOS = ROOT / "configs" / "cenarios.yaml"
SAVED = os.environ.get("PIXFRAUD_DADOS")
SHORTCUTS = {"42 · a dos resultados do relatório": 42,
             **{f"{s} · semente de teste dos estudos": s for s in range(1, 11)},
             "1001 · rede de validação da otimização": 1001, "1002 · rede de validação da otimização": 1002}
DIRECTIONS = {"para frente (para onde foi)": "forward", "para trás (de onde veio)": "backward", "os dois": "both"}
GROUP_COLORS = {UNSUPERVISED: "#0f766e", SUPERVISED: "#9aa7a4"}
OUTCOME_ICONS = {"achou": "✓ fraude achada", "alarme_falso": "✗ alarme falso", "perdeu": "✗ fraude perdida",
                 "resto": ""}

st.set_page_config(page_title="Explorador Pix", layout="wide")


# ---- dados (em cache: gerar e pontuar uma rede leva ~1 min) ----

@st.cache_resource(show_spinner="Gerando a rede e calculando os atributos...")
def network(source: str, scenario: str, seed: int, config_name: str):
    """Contas, Pix e a rede preparada: gerada (semente + cenário) ou lida do dataset salvo."""
    config = load_experiment_config(CONFIGS[config_name])
    if source == "salvo":
        accounts, transactions = load_dataset(SAVED)
        return accounts, transactions, prepare(accounts, transactions, config)
    return generate_network(scenario, seed, config, CONFIGS[config_name], SCENARIOS)


@st.cache_resource(show_spinner="Rodando todos os modelos (cerca de 1 min na primeira vez)...")
def model_scores(source: str, scenario: str, seed: int, config_name: str, feature_set: str):
    """Escores de todos os modelos e a tabela com a nota de cada um."""
    _, _, prepared = network(source, scenario, seed, config_name)
    scores = all_model_scores(prepared, FEATURE_SETS[feature_set], load_experiment_config(CONFIGS[config_name]), seed)
    return scores, rank_models(scores, prepared.labels)


@st.cache_data(show_spinner="Desenhando a rede inteira...")
def explorer_page(source: str, scenario: str, seed: int, config_name: str, feature_set: str, model: int) -> str:
    """HTML da aba "Rede inteira", com todos os modelos no seletor e o escolhido já selecionado."""
    accounts, transactions, prepared = network(source, scenario, seed, config_name)
    scores, ranking = model_scores(source, scenario, seed, config_name, feature_set)
    risk, groups = picker_entries(scores, ranking)
    return network_explorer_html(
        prepared.graph, transactions=transactions, roles=roles_with_victims(accounts.set_index("account_id")),
        risk=risk, risk_groups=groups, labels=prepared.labels, initial_model=model,
        title="Rede Pix sintética", subtitle=network_title(source, scenario, seed, config_name),
    )


def roles_with_victims(info: pd.DataFrame) -> pd.Series:
    """Papel de cada conta, com as vítimas de golpe destacadas como ``vitima``."""
    return info["role"].where(~info["is_victim"], "vitima") if "is_victim" in info else info["role"]


def with_roles(graph, roles: pd.Series):
    """Cópia do grafo com o atributo ``role`` em cada vértice (para colorir os desenhos)."""
    graph = graph.copy()
    for v in graph:
        graph.nodes[v]["role"] = roles.get(v, "?")
    return graph


def network_title(source: str, scenario: str, seed: int, config_name: str) -> str:
    if source == "salvo":
        return f"Dataset salvo em {SAVED}."
    return f"Semente {seed}, cenário '{scenario}', hiperparâmetros {config_name}s."


def brl(value: float) -> str:
    return f"R$ {value:,.0f}".replace(",", ".")


def br(value: float, digits: int = 0) -> str:
    return f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ---- barra lateral: qual rede ----

scenarios = load_scenarios(SCENARIOS)
st.session_state.setdefault("seed", 42)
st.session_state.setdefault("active", {"source": "salvo" if SAVED else "gerada", "scenario": "base", "seed": 42,
                                       "config": "padrão"})


def use_shortcut():
    st.session_state["seed"] = SHORTCUTS[st.session_state["shortcut"]]


def roll_dice():
    st.session_state["seed"] = random.randint(1, 99_999)


st.sidebar.title("Explorador Pix")
st.sidebar.subheader("Rede")
source = "gerada"
if SAVED:
    source = "salvo" if st.sidebar.radio("Dados", ["dataset salvo", "gerar uma rede"]) == "dataset salvo" else "gerada"
if source == "gerada":
    col_seed, col_dice = st.sidebar.columns([3, 1])
    col_seed.number_input("Semente", min_value=0, max_value=2**31 - 1, step=1, key="seed",
                          help="O número que dá a partida no sorteio da rede: "
                               "a mesma semente gera sempre a mesma rede.")
    col_dice.button("🎲", on_click=roll_dice, help="Sortear uma semente", use_container_width=True)
    st.sidebar.selectbox("…ou um atalho", list(SHORTCUTS), index=None, key="shortcut", on_change=use_shortcut,
                         placeholder="sementes usadas na pesquisa")
    scenario = st.sidebar.selectbox("Cenário", list(scenarios), index=list(scenarios).index("base"),
                                    help="Do mais fácil (base) ao mais realista; ver configs/cenarios.yaml.")
    changes = scenarios[scenario]
    st.sidebar.caption("muda: " + ", ".join(f"{k}={v}" for k, v in changes.items()) if changes
                       else "o gerador como está, com os atalhos ligados")
else:
    scenario = "base"
config_options = [name for name, path in CONFIGS.items() if path.exists()]
config_name = st.sidebar.radio("Hiperparâmetros", config_options, horizontal=True,
                               help="'otimizada' usa configs/experimento_otimizado.yaml, escolhida em redes de "
                                    "validação por scripts/otimizar_hiperparametros.py.")
wanted = {"source": source, "scenario": scenario, "seed": int(st.session_state["seed"]), "config": config_name}
if st.sidebar.button("Gerar rede", type="primary", use_container_width=True):
    st.session_state["active"] = wanted
active = st.session_state["active"]
if wanted != active:
    st.sidebar.info("Clique em **Gerar rede** para ver a rede com essas escolhas.")
key = (active["source"], active["scenario"], active["seed"], active["config"])

accounts, transactions, data = network(*key)
info = accounts.set_index("account_id")
roles = roles_with_victims(info)

# ---- barra lateral: qual modelo ----

st.sidebar.subheader("Modelo")
feature_set = st.sidebar.selectbox("Conjunto de atributos", list(FEATURE_SETS),
                                   index=list(FEATURE_SETS).index("completo"))
scores, ranking = model_scores(*key, feature_set)
labels_text = {i: f"{row.posicao}º {row.nome} · AP {br(row.average_precision, 2)}"
               for i, row in enumerate(ranking.itertuples())}
model_index = st.sidebar.selectbox(
    "Modelo do risco", list(labels_text), format_func=lambda i: f"{labels_text[i]} ({ranking.loc[i, 'grupo']})",
    help="Ordenados pela average precision nesta rede, dentro de cada grupo.")
model = ranking.loc[model_index, "modelo"]
risk = scores[model][1]
n_fraud = int(data.labels.sum())
top_k = st.sidebar.slider("Contas investigadas (top-k)", 1, min(len(risk), max(200, 3 * n_fraud)), max(1, n_fraud),
                          help="A fila que um analista olharia primeiro: as k contas de maior risco.")
outcome = top_k_outcome(risk, data.labels, top_k)
st.sidebar.caption(network_title(*key))

tabs = st.tabs(["Resumo", "Rede inteira", "Ranking", "Modelos", "Conta", "Padrões de fraude", "Fluxo e bloqueio",
                "Resultados"])
tab_summary, tab_net, tab_rank, tab_models, tab_account, tab_patterns, tab_flow, tab_results = tabs

with tab_summary:
    summary = network_summary(accounts, transactions, data.graph)
    st.subheader("A rede")
    c = st.columns(4)
    c[0].metric("Contas", br(summary["contas"]))
    c[1].metric("Pix", br(summary["pix"]), help=f"{br(summary['relacoes'])} pares de contas diferentes")
    c[2].metric("Dias", summary["dias"])
    c[3].metric("Dinheiro movimentado", brl(summary["valor_total"]))
    c = st.columns(4)
    c[0].metric("Quadrilhas", summary["quadrilhas"])
    c[1].metric("Contas fraudulentas", br(summary["contas_fraudulentas"]),
                help="Laranjas, intermediários e coletoras", delta=f"{br(100 * summary['taxa_fraude'], 2)}% das contas",
                delta_color="off")
    c[2].metric("Golpes", br(summary["golpes"]), delta=f"{br(summary['vitimas'])} vítimas", delta_color="off")
    c[3].metric("Dinheiro dos golpes", brl(summary["valor_golpes"]))
    c = st.columns(4)
    c[0].metric("Componente gigante fraca", f"{br(100 * summary['gigante_fraca'], 1)}%",
                help="Contas ligadas entre si ignorando o sentido do Pix.")
    c[1].metric("Componente gigante forte", f"{br(100 * summary['gigante_forte'], 1)}%",
                help="Contas em que o dinheiro vai e volta seguindo o sentido do Pix. As da quadrilha quase nunca "
                     "estão nela: o dinheiro do golpe só passa.")
    st.subheader(f"O modelo: {ranking.loc[model_index, 'nome']}")
    found = int((outcome == "achou").sum())
    chance = n_fraud / len(risk)
    c = st.columns(4)
    c[0].metric("Average precision (AP)", br(ranking.loc[model_index, "average_precision"], 2),
                delta=f"acaso: {br(chance, 3)}", delta_color="off")
    c[1].metric(f"Precisão no top-{top_k}", f"{br(100 * found / top_k, 1)}%")
    c[2].metric("Fraudes achadas", f"{found} de {n_fraud}")
    c[3].metric("Alarmes falsos", int((outcome == "alarme_falso").sum()))
    grupo = ranking.loc[model_index, "grupo"]
    st.info(
        f"Se um analista investigasse as **{top_k}** contas de maior risco deste modelo, acharia **{found}** das "
        f"**{n_fraud}** contas fraudulentas. Um sorteio ao acaso teria AP de {br(chance, 3)}. "
        + ("Este modelo **não viu o gabarito**: só olhou os atributos das contas." if grupo == UNSUPERVISED else
           "Este modelo **aprendeu com o gabarito** (em validação cruzada): é um teto, que o banco não teria.")
    )

with tab_net:
    st.caption("Use **Acertos** para ver o que o modelo achou e errou no top-k; clique numa conta para ver os "
               "vizinhos; a linha do tempo mostra a rede crescendo dia a dia.")
    components.html(explorer_page(*key, feature_set, model_index), height=860, scrolling=False)

with tab_rank:
    st.caption(f"As {top_k} contas mais suspeitas para **{ranking.loc[model_index, 'nome']}**. "
               "Selecione uma linha para abrir a conta na aba **Conta**.")
    table = pd.DataFrame({"conta": risk.index, "risco": risk.to_numpy()}).sort_values("risco", ascending=False)
    table = table.head(top_k).reset_index(drop=True)
    table.insert(0, "posição", range(1, len(table) + 1))
    table["papel"] = table["conta"].map(roles)
    table["resultado"] = table["conta"].map(outcome).map(OUTCOME_ICONS)
    picked = st.dataframe(table, hide_index=True, use_container_width=True, on_select="rerun",
                          selection_mode="single-row", key="ranking_table")
    if picked.selection.rows:
        st.session_state["account"] = table.loc[picked.selection.rows[0], "conta"]
    missed = outcome.index[outcome == "perdeu"]
    if len(missed):
        st.caption(f"Fraudes fora do top-{top_k} ({len(missed)}): "
                   + ", ".join(f"{a} ({roles.get(a, '?')})" for a in missed[:30]))

with tab_models:
    st.caption("Average precision de cada modelo **nesta rede**. Uma rede só varia bastante: para conclusões, "
               "veja os estudos com várias sementes na aba Resultados.")
    order = ranking.iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 0.42 * len(order) + 1))
    ax.barh(order["nome"], order["average_precision"], color=[GROUP_COLORS[g] for g in order["grupo"]])
    ax.axvline(chance, color=INK_SECONDARY, linestyle="--", linewidth=1)
    ax.text(chance, len(order) - 0.4, " acaso", color=INK_SECONDARY, fontsize=8, va="bottom")
    for y, value in enumerate(order["average_precision"]):
        ax.text(value + 0.01, y, br(value, 2), va="center", fontsize=8)
    ax.set_xlim(0, 1.08)
    ax.set_xlabel("average precision")
    ax.spines[["top", "right"]].set_visible(False)
    handles = [plt.Rectangle((0, 0), 1, 1, color=color) for color in GROUP_COLORS.values()]
    ax.legend(handles, list(GROUP_COLORS), loc="lower right", frameon=False, fontsize=8)
    st.pyplot(fig)
    plt.close(fig)
    st.dataframe(ranking[["posicao", "nome", "grupo", "average_precision", "precision_at_k", "roc_auc"]].round(3),
                 hide_index=True, use_container_width=True)

with tab_account:
    options = list(risk.sort_values(ascending=False).index[:50])
    chosen = st.session_state.get("account")
    if chosen in options:
        options.remove(chosen)
    if chosen in data.graph:
        options.insert(0, chosen)
    col_pick, col_manual = st.columns([2, 1])
    picked_account = col_pick.selectbox("Uma das 50 contas mais suspeitas (ou a escolhida no Ranking)", options,
                                        format_func=lambda a: f"{a} ({roles.get(a, '?')})")
    typed = col_manual.text_input("…ou digite uma conta", "")
    account = typed.strip() if typed.strip() in data.graph else picked_account
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
        way = "backward" if DIRECTIONS[direction] == "backward" else "forward"
        trail = temporal_trail(transactions, account, direction=way, max_hops=hops)
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
        m1.metric("Fluxo máximo", brl(value))
        m2.metric("Valor do corte mínimo", brl(cut_value))
        m3.metric("Contas a bloquear", "—" if accounts_to_block is None else len(accounts_to_block))
        st.write("Pix do corte mínimo:")
        st.dataframe(pd.DataFrame(cut, columns=["origem", "destino", "valor"]))
        if accounts_to_block:
            st.write("Menor conjunto de contas a bloquear:",
                     ", ".join(f"{a} ({roles.get(a, '?')})" for a in accounts_to_block))

with tab_results:
    studies = {
        "Todos os modelos, configuração padrão (10 sementes por cenário)":
            ROOT / "reports" / "results" / "modelos_resumo.csv",
        "Todos os modelos, hiperparâmetros otimizados (10 sementes por cenário)":
            ROOT / "reports" / "otimizado" / "results" / "modelos_resumo.csv",
    }
    for title, path in studies.items():
        if path.exists():
            st.subheader(title)
            summary_csv = pd.read_csv(path, index_col=[0, 1, 2, 3])
            ap = summary_csv.loc["average_precision", "mean"].droplevel("atributos").unstack("cenario")
            st.dataframe(ap.sort_values(ap.columns[0], ascending=False).round(3), use_container_width=True)
    robust = ROOT / "reports" / "results" / "robustez_resumo.csv"
    if robust.exists():
        st.subheader("Robustez dos conjuntos de atributos (várias sementes)")
        st.dataframe(pd.read_csv(robust).round(3))
    st.subheader("Fraude × normal em cada atributo, nesta rede")
    st.caption("Mann-Whitney com correção de Holm; o delta de Cliff mede o tamanho do efeito.")
    st.dataframe(compare_groups(data.features, data.labels).round(4))

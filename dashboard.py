import numpy as np
import pandas as pd
import itertools
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# CONFIGURATION PAGE
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ADM — Industtech Maroc",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
# CHARGEMENT DES DONNÉES DEPUIS CSV
# ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    base = Path(__file__).parent / "data"
    df_proj = pd.read_csv(base / "donnees_projets.csv")
    df_crit = pd.read_csv(base / "criteres_poids.csv")
    return df_proj, df_crit

try:
    df_proj, df_crit = load_data()
except FileNotFoundError:
    st.error(
        "⚠️ Data files not found. Please run `notebooks/ahp_calculs.ipynb` first "
        "to generate `data/donnees_projets.csv` and `data/criteres_poids.csv`."
    )
    st.stop()

# Extraction des arrays depuis les DataFrames
PROJECTS      = df_proj['name'].tolist()
COSTS         = df_proj['cost_kmad'].tolist()
DESCRIPTIONS  = df_proj['description'].tolist()
GLOBAL_SCORES = df_proj['global_score'].values
LOCAL_SCORES  = df_proj[['score_C1','score_C2','score_C3','score_C4','score_C5']].values
BASE_WEIGHTS  = df_crit['weight'].values
CRITERIA      = df_crit['name'].tolist()
CRIT_SHORT    = ['C1 Eco.', 'C2 Tech.', 'C3 Sust.', 'C4 Strat.', 'C5 Compl.']
BUDGET        = 1500

COLORS = ["#2563EB", "#16A34A", "#D97706", "#DC2626", "#7C3AED"]

# ─────────────────────────────────────────────────────────────
# FONCTIONS UTILITAIRES
# ─────────────────────────────────────────────────────────────
def compute_global_scores(local_scores, weights):
    return local_scores @ weights

def optimize_selection(scores, costs, budget):
    best_value, best_combo = 0, []
    results = []
    for r in range(1, len(scores) + 1):
        for combo in itertools.combinations(range(len(scores)), r):
            total_cost  = sum(costs[i]  for i in combo)
            total_score = sum(scores[i] for i in combo)
            if total_cost <= budget:
                results.append((total_score, total_cost, list(combo)))
                if total_score > best_value:
                    best_value = total_score
                    best_combo = list(combo)
    results.sort(reverse=True)
    return best_combo, best_value, results[:5]

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/factory.png", width=60)
    st.title("Industtech Maroc")
    st.caption("Tableau de bord ADM — AHP + Optimisation")
    st.divider()

    page = st.radio(
        "Navigation",
        ["🏠 Vue d'ensemble", "⚖️ Analyse AHP", "💰 Optimisation budgétaire", "🔬 Scénarios"],
        label_visibility="collapsed"
    )
    st.divider()
    cr_val = df_crit['CR'].iloc[0]
    st.metric("Consistency Ratio (CR)", f"{cr_val:.3f}", "✅ < 0.10")
    st.divider()
    st.markdown("**Projet ADM**")
    st.caption("KANOHA ELENGA Helmie Naella Jihane")
    st.caption("Méthode : AHP + Integer Programming")
    st.caption("Référence : ISAHP 2022 & 2024")

# ─────────────────────────────────────────────────────────────
# PAGE 1 — VUE D'ENSEMBLE
# ─────────────────────────────────────────────────────────────
if page == "🏠 Vue d'ensemble":
    st.title("🏭 Industtech Maroc — Tableau de bord ADM")
    st.markdown(
        "Système d'aide à la décision multicritère pour la **priorisation et sélection optimale** "
        "de projets de transformation numérique durable. Méthode : **AHP + Optimisation linéaire**."
    )

    opt_combo, opt_value, _ = optimize_selection(GLOBAL_SCORES.tolist(), COSTS, BUDGET)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Projets évalués", len(PROJECTS))
    col2.metric("Critères AHP", len(CRITERIA))
    col3.metric("Budget disponible", f"{BUDGET} kMAD")
    col4.metric("Projets sélectionnés (optimal)", len(opt_combo))

    st.divider()
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("📋 Projets candidats")
        ranks = [int(np.where(np.argsort(GLOBAL_SCORES)[::-1] == i)[0][0]) + 1 for i in range(len(PROJECTS))]
        df_display = pd.DataFrame({
            "Projet":       PROJECTS,
            "Description":  DESCRIPTIONS,
            "Coût (kMAD)":  COSTS,
            "Score AHP":    [f"{s:.4f}" for s in GLOBAL_SCORES],
            "Rang":         ranks,
            "Sélectionné":  ["✅" if i in opt_combo else "—" for i in range(len(PROJECTS))]
        }).sort_values("Rang")
        st.dataframe(df_display, use_container_width=True, hide_index=True)

    with col_right:
        st.subheader("⚖️ Poids des critères")
        fig_weights = go.Figure(go.Bar(
            x=BASE_WEIGHTS * 100,
            y=CRIT_SHORT,
            orientation='h',
            marker_color=COLORS,
            text=[f"{w*100:.1f}%" for w in BASE_WEIGHTS],
            textposition='outside'
        ))
        fig_weights.update_layout(
            height=280, margin=dict(l=10, r=60, t=10, b=10),
            xaxis_title="Poids (%)", yaxis=dict(autorange="reversed"),
            plot_bgcolor="white"
        )
        st.plotly_chart(fig_weights, use_container_width=True)

    st.subheader("🏆 Classement global AHP")
    sorted_idx = np.argsort(GLOBAL_SCORES)[::-1]
    fig_rank = go.Figure()
    for i in sorted_idx:
        fig_rank.add_trace(go.Bar(
            x=[GLOBAL_SCORES[i]], y=[PROJECTS[i]],
            orientation='h',
            marker_color=COLORS[i],
            text=f"{GLOBAL_SCORES[i]:.4f}",
            textposition='outside',
            showlegend=False
        ))
    fig_rank.update_layout(
        height=260, margin=dict(l=10, r=80, t=10, b=10),
        xaxis=dict(range=[0, max(GLOBAL_SCORES) * 1.3], title="Score AHP global"),
        yaxis=dict(autorange="reversed"),
        plot_bgcolor="white"
    )
    st.plotly_chart(fig_rank, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# PAGE 2 — ANALYSE AHP
# ─────────────────────────────────────────────────────────────
elif page == "⚖️ Analyse AHP":
    st.title("⚖️ Analyse AHP — Scores et hiérarchie")

    tab1, tab2, tab3 = st.tabs(["🕸️ Radar des projets", "🔥 Heatmap des scores", "📊 Scores par critère"])

    with tab1:
        st.subheader("Profil multicritère de chaque projet")
        fig_radar = go.Figure()
        for i, (proj, color) in enumerate(zip(PROJECTS, COLORS)):
            values = LOCAL_SCORES[i].tolist() + [LOCAL_SCORES[i][0]]
            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=CRIT_SHORT + [CRIT_SHORT[0]],
                fill='toself', fillcolor=color,
                line_color=color, opacity=0.25, name=proj
            ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 0.6])),
            height=480,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2)
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        st.info("💡 Un projet idéal couvrirait tous les axes. La complémentarité des profils justifie la sélection de plusieurs projets.")

    with tab2:
        st.subheader("Heatmap des scores locaux AHP")
        df_heat = pd.DataFrame(LOCAL_SCORES, index=PROJECTS, columns=CRIT_SHORT)
        fig_heat = px.imshow(df_heat, text_auto=".3f",
                             color_continuous_scale="Blues", aspect="auto")
        fig_heat.update_layout(height=340, margin=dict(t=20))
        st.plotly_chart(fig_heat, use_container_width=True)
        st.caption("Lecture : plus la cellule est foncée, plus le projet excelle sur ce critère.")

    with tab3:
        st.subheader("Scores par critère sélectionné")
        selected_crit = st.selectbox("Choisir un critère", CRITERIA)
        crit_idx = CRITERIA.index(selected_crit)
        scores_crit = LOCAL_SCORES[:, crit_idx]
        sorted_i = np.argsort(scores_crit)[::-1]
        fig_crit = go.Figure(go.Bar(
            x=[PROJECTS[i] for i in sorted_i],
            y=[scores_crit[i] for i in sorted_i],
            marker_color=[COLORS[i] for i in sorted_i],
            text=[f"{scores_crit[i]:.4f}" for i in sorted_i],
            textposition='outside'
        ))
        fig_crit.update_layout(
            height=360, yaxis=dict(range=[0, max(scores_crit) * 1.3]),
            plot_bgcolor="white", yaxis_title="Score local AHP"
        )
        st.plotly_chart(fig_crit, use_container_width=True)
        winner = PROJECTS[sorted_i[0]]
        st.success(f"🏆 **{winner}** est le projet le plus performant sur ce critère "
                   f"(score : **{scores_crit[sorted_i[0]]:.4f}**).")

# ─────────────────────────────────────────────────────────────
# PAGE 3 — OPTIMISATION BUDGÉTAIRE
# ─────────────────────────────────────────────────────────────
elif page == "💰 Optimisation budgétaire":
    st.title("💰 Optimisation budgétaire")
    st.markdown("Sélection optimale de projets selon un **budget donné**, en maximisant le score AHP total.")

    budget = st.slider("💵 Budget disponible (kMAD)",
                       min_value=min(COSTS), max_value=3000, value=BUDGET, step=50)

    best_combo, best_value, top5 = optimize_selection(GLOBAL_SCORES.tolist(), COSTS, budget)

    col1, col2, col3 = st.columns(3)
    col1.metric("Projets sélectionnés", len(best_combo))
    col2.metric("Score total optimal", f"{best_value:.4f}")
    used = sum(COSTS[i] for i in best_combo) if best_combo else 0
    col3.metric("Budget utilisé", f"{used} / {budget} kMAD ({used/budget*100:.0f}%)" if budget > 0 else "—")

    st.divider()
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("✅ Sélection optimale")
        rows = []
        for i in range(len(PROJECTS)):
            rows.append({
                "Projet": PROJECTS[i],
                "Score AHP": f"{GLOBAL_SCORES[i]:.4f}",
                "Coût (kMAD)": COSTS[i],
                "Statut": "✅ Sélectionné" if i in best_combo else "❌ Non retenu"
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with col_right:
        st.subheader("🏆 Top 5 combinaisons")
        if top5:
            labels = [" + ".join([PROJECTS[i] for i in combo]) for _, _, combo in top5]
            vals   = [s for s, _, _ in top5]
            fig_top5 = go.Figure(go.Bar(
                x=vals, y=labels, orientation='h',
                marker_color=["#2563EB" if i == 0 else "#93C5FD" for i in range(len(labels))],
                text=[f"{v:.4f}" for v in vals], textposition='outside'
            ))
            fig_top5.update_layout(
                height=300, margin=dict(l=10, r=80, t=10, b=10),
                xaxis_title="Score AHP total",
                yaxis=dict(autorange="reversed"), plot_bgcolor="white"
            )
            st.plotly_chart(fig_top5, use_container_width=True)
        else:
            st.warning("Aucune combinaison réalisable pour ce budget.")

    st.divider()
    st.subheader("📈 Score optimal en fonction du budget")
    budgets_range = range(min(COSTS), 3001, 50)
    curve_scores, curve_n = [], []
    for b in budgets_range:
        bc, bv, _ = optimize_selection(GLOBAL_SCORES.tolist(), COSTS, b)
        curve_scores.append(bv)
        curve_n.append(len(bc))

    fig_curve = make_subplots(specs=[[{"secondary_y": True}]])
    fig_curve.add_trace(go.Scatter(
        x=list(budgets_range), y=curve_scores, mode='lines',
        name='Score optimal', line=dict(color='#2563EB', width=2.5)
    ), secondary_y=False)
    fig_curve.add_trace(go.Scatter(
        x=list(budgets_range), y=curve_n, mode='lines',
        name='Nb projets', line=dict(color='#16A34A', width=2, dash='dot')
    ), secondary_y=True)
    fig_curve.add_vline(x=budget, line_dash="dash", line_color="#DC2626",
                        annotation_text=f"Budget actuel : {budget} kMAD")
    fig_curve.update_layout(
        height=320, plot_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.3)
    )
    fig_curve.update_yaxes(title_text="Score AHP total", secondary_y=False)
    fig_curve.update_yaxes(title_text="Nombre de projets", secondary_y=True)
    st.plotly_chart(fig_curve, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# PAGE 4 — SCÉNARIOS
# ─────────────────────────────────────────────────────────────
elif page == "🔬 Scénarios":
    st.title("🔬 Simulation de scénarios")
    st.markdown("Modifiez les **poids des critères** et observez l'impact en temps réel.")

    col_sliders, col_results = st.columns([1, 2])

    with col_sliders:
        st.subheader("Ajuster les poids")
        st.caption("Les poids seront normalisés automatiquement.")
        sliders = []
        for i, (name, base_w) in enumerate(zip(CRITERIA, BASE_WEIGHTS)):
            sliders.append(st.slider(name, 0, 100, int(base_w * 100), 5))

        budget_scen = st.slider("Budget (kMAD)", 500, 2500, BUDGET, 50)

        raw = np.array(sliders, dtype=float)
        new_weights = raw / raw.sum() if raw.sum() > 0 else BASE_WEIGHTS.copy()

        st.divider()
        st.subheader("Poids normalisés")
        for c, w in zip(CRIT_SHORT, new_weights):
            st.progress(float(w), text=f"{c} : {w*100:.1f}%")

    with col_results:
        new_scores  = compute_global_scores(LOCAL_SCORES, new_weights)
        base_scores = GLOBAL_SCORES
        sorted_new  = np.argsort(new_scores)[::-1]
        sorted_base = np.argsort(base_scores)[::-1]

        st.subheader("📊 Classement — Scénario vs Référence")
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(
            name="Scénario personnalisé",
            x=PROJECTS, y=new_scores,
            marker_color="#2563EB", opacity=0.85
        ))
        fig_comp.add_trace(go.Bar(
            name="Référence AHP (base)",
            x=PROJECTS, y=base_scores,
            marker_color="#D1D5DB", opacity=0.7
        ))
        fig_comp.update_layout(
            barmode='group', height=320, plot_bgcolor="white",
            yaxis_title="Score global AHP",
            legend=dict(orientation="h", yanchor="bottom", y=-0.3)
        )
        st.plotly_chart(fig_comp, use_container_width=True)

        st.subheader("🔄 Évolution des rangs")
        for i, proj in enumerate(PROJECTS):
            old_rank = int(np.where(sorted_base == i)[0][0]) + 1
            new_rank = int(np.where(sorted_new  == i)[0][0]) + 1
            delta = old_rank - new_rank
            if delta > 0:
                st.success(f"**{proj}** : #{old_rank} → #{new_rank}  ⬆️ +{delta} place(s)")
            elif delta < 0:
                st.error(f"**{proj}** : #{old_rank} → #{new_rank}  ⬇️ {delta} place(s)")
            else:
                st.info(f"**{proj}** : #{old_rank} → #{new_rank}  ↔️ Inchangé")

        st.subheader("💡 Sélection optimale — Scénario")
        bc_s, bv_s, _ = optimize_selection(new_scores.tolist(), COSTS, budget_scen)
        if bc_s:
            names_s = " + ".join([PROJECTS[i] for i in bc_s])
            cost_s  = sum(COSTS[i] for i in bc_s)
            st.success(
                f"**Projets retenus :** {names_s}\n\n"
                f"**Score :** {bv_s:.4f}  |  **Coût :** {cost_s} / {budget_scen} kMAD"
            )
        else:
            st.warning("Aucun projet réalisable pour ce budget.")
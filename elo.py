
import streamlit as st
import pandas as pd
from elo import calculate_elo

st.set_page_config(page_title="FIFA WM Elo Tracker", layout="wide")
st.title("FIFA WM Elo Tracker")
st.caption("Leistungsschonende Streamlit-Version")

if "matches" not in st.session_state:
    st.session_state.matches = pd.DataFrame(columns=["order", "year", "stage", "team_a", "team_b", "goals_a", "goals_b"])

with st.sidebar:
    st.header("Einstellungen")
    base_elo = st.number_input("Start-Elo", value=1500, step=50)
    k_factor = st.number_input("K-Faktor", value=40, step=5)
    goal_bonus = st.number_input("Tordifferenz-Bonus", value=0.15, step=0.05)
    max_goal_factor = st.number_input("Maximaler Torfaktor", value=1.60, step=0.05)

ranking, history = calculate_elo(st.session_state.matches, base_elo, k_factor, goal_bonus, max_goal_factor)

c1, c2, c3 = st.columns(3)
c1.metric("Spiele", len(st.session_state.matches))
c2.metric("Teams", 0 if ranking.empty else len(ranking))
c3.metric("Höchstes Elo", "–" if ranking.empty else f"{ranking.iloc[0]['team']} {ranking.iloc[0]['elo']:.0f}")

st.subheader("Top 20")
if ranking.empty:
    st.info("Noch keine Spiele vorhanden. Importiere eine CSV oder gib Spiele ein.")
else:
    st.dataframe(ranking.head(20), use_container_width=True, hide_index=True)

st.subheader("Letzte Spiele")
if not history.empty:
    st.dataframe(history.sort_values("order", ascending=False).head(20), use_container_width=True, hide_index=True)

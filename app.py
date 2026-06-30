
import streamlit as st
from elo import calculate_elo, world_cup_performance

st.title("WM-Ranking")

if "matches" not in st.session_state:
    st.warning("Noch keine Daten vorhanden.")
    st.stop()

ranking, history = calculate_elo(st.session_state.matches)
perf = world_cup_performance(history)

if perf.empty:
    st.info("Noch keine WM-Leistungen vorhanden.")
    st.stop()

year = st.selectbox("WM filtern", ["Alle"] + sorted(perf["year"].unique().tolist()))
team = st.text_input("Team suchen")

view = perf.copy()
if year != "Alle":
    view = view[view["year"] == year]
if team:
    view = view[view["team"].str.contains(team, case=False, na=False)]

st.subheader("Einzelne WM-Leistungen")
st.dataframe(view, use_container_width=True, hide_index=True)

st.subheader("Gesamtranking nach Ländern")
totals = perf.groupby("team", as_index=False).agg(
    tournaments=("year", "count"),
    games=("games", "sum"),
    wins=("wins", "sum"),
    draws=("draws", "sum"),
    losses=("losses", "sum"),
    goals_for=("goals_for", "sum"),
    goals_against=("goals_against", "sum"),
    total_elo_delta=("elo_delta", "sum"),
)
totals["avg_elo_delta"] = totals["total_elo_delta"] / totals["tournaments"]
totals = totals.sort_values("total_elo_delta", ascending=False).reset_index(drop=True)
totals.insert(0, "rank", totals.index + 1)
st.dataframe(totals, use_container_width=True, hide_index=True)

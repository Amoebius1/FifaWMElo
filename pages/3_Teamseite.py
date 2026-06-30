
import streamlit as st
import pandas as pd
import plotly.express as px
from elo import calculate_elo

st.title("Teamseite")

if "matches" not in st.session_state:
    st.warning("Noch keine Daten vorhanden.")
    st.stop()

ranking, history = calculate_elo(st.session_state.matches)
if ranking.empty:
    st.info("Noch keine Teams vorhanden.")
    st.stop()

team = st.selectbox("Team auswählen", ranking["team"].tolist())
row = ranking[ranking["team"] == team].iloc[0]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Aktuelles Elo", f"{row['elo']:.0f}")
c2.metric("Peak", f"{row['peak']:.0f}")
c3.metric("Spiele", int(row["games"]))
c4.metric("Bilanz", f"{int(row['wins'])}-{int(row['draws'])}-{int(row['losses'])}")

team_games = history[(history["team_a"] == team) | (history["team_b"] == team)].copy()
team_games["team_elo"] = team_games.apply(lambda r: r["after_a"] if r["team_a"] == team else r["after_b"], axis=1)

st.subheader("Elo-Verlauf")
fig = px.line(team_games, x="order", y="team_elo", hover_data=["year", "stage", "team_a", "team_b", "goals_a", "goals_b"])
st.plotly_chart(fig, use_container_width=True)

st.subheader("Alle Spiele")
st.dataframe(team_games, use_container_width=True, hide_index=True)

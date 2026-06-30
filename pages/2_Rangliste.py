
import streamlit as st
from elo import calculate_elo

st.title("Elo-Rangliste")

if "matches" not in st.session_state:
    st.warning("Noch keine Daten vorhanden.")
    st.stop()

ranking, history = calculate_elo(st.session_state.matches)

search = st.text_input("Team suchen")
if search and not ranking.empty:
    ranking = ranking[ranking["team"].str.contains(search, case=False, na=False)]

st.dataframe(ranking, use_container_width=True, hide_index=True)

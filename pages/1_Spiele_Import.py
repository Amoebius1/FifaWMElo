
import streamlit as st
import pandas as pd

st.title("Spiele & Import")

if "matches" not in st.session_state:
    st.session_state.matches = pd.DataFrame(columns=["order", "year", "stage", "team_a", "team_b", "goals_a", "goals_b"])

st.subheader("CSV importieren")
st.caption("Format: Jahr;Phase;TeamA;TeamB;ToreA;ToreB")

uploaded = st.file_uploader("CSV-Datei auswählen", type=["csv", "txt"])

if uploaded:
    try:
        df = pd.read_csv(uploaded, sep=None, engine="python")
        df.columns = [str(c).strip().lower() for c in df.columns]
        mapping = {
            "jahr": "year", "year": "year",
            "phase": "stage", "stage": "stage",
            "teama": "team_a", "team_a": "team_a",
            "teamb": "team_b", "team_b": "team_b",
            "torea": "goals_a", "goals_a": "goals_a",
            "toreb": "goals_b", "goals_b": "goals_b",
        }
        df = df.rename(columns={c: mapping.get(c, c) for c in df.columns})
        needed = ["year", "stage", "team_a", "team_b", "goals_a", "goals_b"]

        if not all(c in df.columns for c in needed):
            st.error("Die CSV braucht diese Spalten: Jahr;Phase;TeamA;TeamB;ToreA;ToreB")
        else:
            clean = df[needed].copy()
            clean["year"] = clean["year"].astype(int)
            clean["goals_a"] = clean["goals_a"].astype(int)
            clean["goals_b"] = clean["goals_b"].astype(int)
            start = 1 if st.session_state.matches.empty else int(st.session_state.matches["order"].max()) + 1
            clean.insert(0, "order", range(start, start + len(clean)))

            if st.button("Import übernehmen"):
                st.session_state.matches = pd.concat([st.session_state.matches, clean], ignore_index=True)
                st.success(f"{len(clean)} Spiele importiert.")
    except Exception as e:
        st.error(f"Import fehlgeschlagen: {e}")

st.divider()
st.subheader("Spiel manuell eintragen")

with st.form("match_form"):
    year = st.number_input("Jahr", min_value=1930, max_value=2100, value=2026)
    stage = st.selectbox("Phase", ["Gruppenphase", "Achtelfinale", "Viertelfinale", "Halbfinale", "Spiel um Platz 3", "Finale", "Andere"])
    team_a = st.text_input("Team A")
    team_b = st.text_input("Team B")
    goals_a = st.number_input("Tore A", min_value=0, value=0)
    goals_b = st.number_input("Tore B", min_value=0, value=0)
    submitted = st.form_submit_button("Spiel speichern")

if submitted:
    if not team_a or not team_b or team_a == team_b:
        st.error("Bitte zwei verschiedene Teams eintragen.")
    else:
        order = 1 if st.session_state.matches.empty else int(st.session_state.matches["order"].max()) + 1
        new = pd.DataFrame([{
            "order": order, "year": int(year), "stage": stage,
            "team_a": team_a, "team_b": team_b,
            "goals_a": int(goals_a), "goals_b": int(goals_b)
        }])
        st.session_state.matches = pd.concat([st.session_state.matches, new], ignore_index=True)
        st.success("Spiel gespeichert.")

st.subheader("Aktuelle Spiele")
st.dataframe(st.session_state.matches, use_container_width=True, hide_index=True)

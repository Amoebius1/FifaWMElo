
from math import pow
import pandas as pd

ALIASES = {
    "westdeutschland": "Deutschland",
    "west germany": "Deutschland",
    "germany": "Deutschland",
    "ussr": "Sowjetunion",
    "soviet union": "Sowjetunion",
    "yugoslavia": "Jugoslawien",
    "czechoslovakia": "Tschechoslowakei",
    "czechia": "Tschechien",
    "czech republic": "Tschechien",
    "south korea": "Südkorea",
    "north korea": "Nordkorea",
    "united states": "USA",
    "united states of america": "USA",
}

def normalize_team(name):
    text = str(name or "").strip()
    return ALIASES.get(text.lower(), text)

def expected_score(ra, rb):
    return 1 / (1 + pow(10, (rb - ra) / 400))

def goal_factor(goals_a, goals_b, bonus=0.15, max_factor=1.6):
    diff = abs(int(goals_a) - int(goals_b))
    if diff <= 1:
        return 1.0
    return min(max_factor, 1 + (diff - 1) * bonus)

def result_a(row):
    if int(row["goals_a"]) > int(row["goals_b"]):
        return 1.0
    if int(row["goals_a"]) < int(row["goals_b"]):
        return 0.0
    return 0.5

def calculate_elo(matches, base_elo=1500, k_factor=40, goal_bonus=0.15, max_goal_factor=1.6):
    if matches is None or matches.empty:
        return pd.DataFrame(), pd.DataFrame()

    df = matches.copy()
    df["team_a"] = df["team_a"].map(normalize_team)
    df["team_b"] = df["team_b"].map(normalize_team)
    df = df.sort_values(["year", "order"]).reset_index(drop=True)

    ratings = {}
    stats = {}
    history = []

    def ensure(team):
        if team not in ratings:
            ratings[team] = float(base_elo)
            stats[team] = {
                "team": team, "start_elo": float(base_elo), "elo": float(base_elo),
                "peak": float(base_elo), "low": float(base_elo),
                "games": 0, "wins": 0, "draws": 0, "losses": 0,
                "goals_for": 0, "goals_against": 0,
            }

    for _, row in df.iterrows():
        a, b = row["team_a"], row["team_b"]
        ensure(a); ensure(b)

        before_a, before_b = ratings[a], ratings[b]
        exp_a = expected_score(before_a, before_b)
        res_a = result_a(row)
        factor = goal_factor(row["goals_a"], row["goals_b"], goal_bonus, max_goal_factor)
        delta_a = k_factor * factor * (res_a - exp_a)
        delta_b = -delta_a

        ratings[a] += delta_a
        ratings[b] += delta_b

        ga, gb = int(row["goals_a"]), int(row["goals_b"])

        for team, gf, gc, delta, before, after in [
            (a, ga, gb, delta_a, before_a, ratings[a]),
            (b, gb, ga, delta_b, before_b, ratings[b]),
        ]:
            s = stats[team]
            s["elo"] = after
            s["peak"] = max(s["peak"], after)
            s["low"] = min(s["low"], after)
            s["games"] += 1
            s["goals_for"] += gf
            s["goals_against"] += gc

        if ga > gb:
            stats[a]["wins"] += 1; stats[b]["losses"] += 1
        elif ga < gb:
            stats[b]["wins"] += 1; stats[a]["losses"] += 1
        else:
            stats[a]["draws"] += 1; stats[b]["draws"] += 1

        history.append({
            "order": int(row["order"]), "year": int(row["year"]), "stage": row["stage"],
            "team_a": a, "team_b": b, "goals_a": ga, "goals_b": gb,
            "before_a": before_a, "before_b": before_b,
            "after_a": ratings[a], "after_b": ratings[b],
            "delta_a": delta_a, "delta_b": delta_b,
        })

    ranking = pd.DataFrame(stats.values()).sort_values("elo", ascending=False).reset_index(drop=True)
    ranking.insert(0, "rank", ranking.index + 1)
    return ranking, pd.DataFrame(history)

def world_cup_performance(history):
    if history is None or history.empty:
        return pd.DataFrame()

    rows = []
    for _, m in history.iterrows():
        for side in ["a", "b"]:
            team = m[f"team_{side}"]
            gf = m["goals_a"] if side == "a" else m["goals_b"]
            ga = m["goals_b"] if side == "a" else m["goals_a"]
            rows.append({
                "year": m["year"], "team": team,
                "games": 1,
                "wins": gf > ga, "draws": gf == ga, "losses": gf < ga,
                "goals_for": gf, "goals_against": ga,
                "start_elo": m[f"before_{side}"],
                "end_elo": m[f"after_{side}"],
                "elo_delta": m[f"delta_{side}"],
            })

    long = pd.DataFrame(rows)
    out = long.groupby(["year", "team"], as_index=False).agg(
        games=("games", "sum"),
        wins=("wins", "sum"),
        draws=("draws", "sum"),
        losses=("losses", "sum"),
        goals_for=("goals_for", "sum"),
        goals_against=("goals_against", "sum"),
        start_elo=("start_elo", "first"),
        end_elo=("end_elo", "last"),
        elo_delta=("elo_delta", "sum"),
    ).sort_values("elo_delta", ascending=False).reset_index(drop=True)
    out.insert(0, "rank", out.index + 1)
    return out

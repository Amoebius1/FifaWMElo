from math import pow
import pandas as pd

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
    df = df.sort_values(["year", "order"]).reset_index(drop=True)

    ratings = {}
    stats = {}
    history = []

    def ensure(team):
        if team not in ratings:
            ratings[team] = float(base_elo)
            stats[team] = {
                "team": team,
                "elo": float(base_elo),
                "peak": float(base_elo),
                "low": float(base_elo),
                "games": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "goals_for": 0,
                "goals_against": 0,
            }

    for _, row in df.iterrows():
        a = row["team_a"]
        b = row["team_b"]

        ensure(a)
        ensure(b)

        before_a = ratings[a]
        before_b = ratings[b]

        expected_a = expected_score(before_a, before_b)
        score_a = result_a(row)
        factor = goal_factor(row["goals_a"], row["goals_b"], goal_bonus, max_goal_factor)

        delta_a = k_factor * factor * (score_a - expected_a)
        delta_b = -delta_a

        ratings[a] += delta_a
        ratings[b] += delta_b

        goals_a = int(row["goals_a"])
        goals_b = int(row["goals_b"])

        stats[a]["elo"] = ratings[a]
        stats[b]["elo"] = ratings[b]

        stats[a]["peak"] = max(stats[a]["peak"], ratings[a])
        stats[b]["peak"] = max(stats[b]["peak"], ratings[b])
        stats[a]["low"] = min(stats[a]["low"], ratings[a])
        stats[b]["low"] = min(stats[b]["low"], ratings[b])

        stats[a]["games"] += 1
        stats[b]["games"] += 1

        stats[a]["goals_for"] += goals_a
        stats[a]["goals_against"] += goals_b
        stats[b]["goals_for"] += goals_b
        stats[b]["goals_against"] += goals_a

        if goals_a > goals_b:
            stats[a]["wins"] += 1
            stats[b]["losses"] += 1
        elif goals_a < goals_b:
            stats[b]["wins"] += 1
            stats[a]["losses"] += 1
        else:
            stats[a]["draws"] += 1
            stats[b]["draws"] += 1

        history.append({
            "order": int(row["order"]),
            "year": int(row["year"]),
            "stage": row["stage"],
            "team_a": a,
            "team_b": b,
            "goals_a": goals_a,
            "goals_b": goals_b,
            "before_a": before_a,
            "before_b": before_b,
            "after_a": ratings[a],
            "after_b": ratings[b],
            "delta_a": delta_a,
            "delta_b": delta_b,
        })

    ranking = pd.DataFrame(stats.values()).sort_values("elo", ascending=False).reset_index(drop=True)
    ranking.insert(0, "rank", ranking.index + 1)

    return ranking, pd.DataFrame(history)

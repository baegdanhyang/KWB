import sys
import os
import contextlib
import json
import traceback
import pandas as pd
import random
import time
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

year_weights = {2025: 0.6, 2024: 0.3, 2023: 0.1}

@contextlib.contextmanager
def suppress_stdout():
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

def init_worker(hitters_fp, pitchers_fp, hitters_type_fp, pitchers_type_fp, team_A_dict, team_B_dict):
    global hitters_df_all, pitchers_df_all
    global hitter_types_df, pitcher_types_df
    global hitters_by_player, pitchers_by_player
    global pitcher_types
    global team_A, team_B

    hitters_df_all = pd.read_csv(hitters_fp, na_values=["N/A", " ", "", "-"])
    for col in ["K%", "BB%"]:
        hitters_df_all[col] = pd.to_numeric(hitters_df_all[col], errors="coerce")
    hitters_df_all[["K%", "BB%"]] /= 100.0

    pitchers_df_all = pd.read_csv(pitchers_fp, na_values=["N/A", " ", "", "-"])
    hitter_types_df = pd.read_csv(hitters_type_fp, index_col="Name")
    pitcher_types_df = pd.read_csv(pitchers_type_fp, index_col="Name")

    hitters_by_player = {p: df for p, df in hitters_df_all.groupby("Player")}
    pitchers_by_player = {p: df for p, df in pitchers_df_all.groupby("Player")}
    pitcher_types = pitcher_types_df["Pitching_Type"].to_dict()

    team_A = dict(team_A_dict)
    team_B = dict(team_B_dict)

def get_weighted_stat(player_data, column, weights):
    if player_data is None or len(player_data) == 0:
        return 0.0
    total = 0
    weight_sum = 0
    for _, row in player_data.iterrows():
        year = row["Year"]
        if year in weights and pd.notna(row[column]):
            total += weights[year] * float(row[column])
            weight_sum += weights[year]
    return total / weight_sum if weight_sum else 0.0

def update_game_state(result, score, outs, bases):
    if result in ["strikeout", "out"]:
        outs += 1
    elif result == "walk":
        if all(bases): score += 1
        if bases[0] and bases[1]: bases[2] = True
        if bases[0]: bases[1] = True
        bases[0] = True
    elif result == "single":
        if bases[2]: score += 1
        bases = [True] + bases[:2]
    elif result == "double":
        if bases[2]: score += 1
        if bases[1]: score += 1
        bases = [False, True, bases[0]]
    elif result == "triple":
        score += sum(bases)
        bases = [False, False, True]
    elif result == "homerun":
        score += 1 + sum(bases)
        bases = [False, False, False]
    return score, outs, bases

def determine_hit_type(hybrid_avg):
    if hybrid_avg > 0.33:
        return random.choices(["single", "double", "triple", "homerun"], weights=[60, 25, 10, 5])[0]
    elif hybrid_avg > 0.25:
        return random.choices(["single", "double", "homerun"], weights=[70, 25, 5])[0]
    else:
        return random.choices(["single", "double"], weights=[80, 20])[0]

def at_bat_result(hybrid_avg, hybrid_obp, k_rate, bb_rate):
    r = random.random()
    if r < k_rate:
        return "strikeout"
    elif r < k_rate + bb_rate:
        return "walk"
    elif r < k_rate + bb_rate + hybrid_obp:
        return determine_hit_type(hybrid_avg)
    else:
        return "out"

def get_matchup_key(pitcher_type):
    if pitcher_type in ["우투", "우언"]:
        return "RAVG", "ROBP"
    elif pitcher_type == "좌투":
        return "LAVG", "LOBP"
    else:
        return "UAVG", "UOBP"

def precompute_hitter_stats(hitter_df, pitcher_type):
    matchup_avg_key, matchup_obp_key = get_matchup_key(pitcher_type)
    avg = get_weighted_stat(hitter_df, "AVG", year_weights)
    obp = get_weighted_stat(hitter_df, "OBP", year_weights)
    babip = get_weighted_stat(hitter_df, "BABIP", year_weights)
    matchup_avg = get_weighted_stat(hitter_df, matchup_avg_key, year_weights)
    matchup_obp = get_weighted_stat(hitter_df, matchup_obp_key, year_weights)
    k_rate = get_weighted_stat(hitter_df, "K%", year_weights)
    bb_rate = get_weighted_stat(hitter_df, "BB%", year_weights)
    hybrid_avg = 0.6 * avg + 0.35 * matchup_avg + 0.05 * babip
    hybrid_obp = 0.6 * obp + 0.4 * matchup_obp
    condition_factor = random.uniform(0.95, 1.05)
    hybrid_avg *= condition_factor
    hybrid_obp *= condition_factor
    k_rate *= 1 / condition_factor
    bb_rate *= condition_factor
    return hybrid_avg, hybrid_obp, k_rate, bb_rate

def simulate_offense(lineup, opposing_pitcher_name, batter_index):
    pitcher_type = pitcher_types.get(opposing_pitcher_name, None)
    score = 0
    outs = 0
    bases = [False, False, False]
    while outs < 3:
        hitter = lineup[batter_index[0] % 9]
        hitter_df = hitters_by_player.get(hitter, pd.DataFrame())
        hybrid_avg, hybrid_obp, k_rate, bb_rate = precompute_hitter_stats(hitter_df, pitcher_type)
        result = at_bat_result(hybrid_avg, hybrid_obp, k_rate, bb_rate)
        score, outs, bases = update_game_state(result, score, outs, bases)
        batter_index[0] += 1
    return score

def simulate_match(_):
    batter_index = [0]
    score_A, score_B = 0, 0

    def calc_starter_round(starter_name):
        pitcher_df = pitchers_by_player.get(starter_name, pd.DataFrame())
        ip = get_weighted_stat(pitcher_df, "IP", year_weights)
        g = get_weighted_stat(pitcher_df, "G", year_weights)
        return int(round(ip / g)) if g > 0 else 6

    starter_A = team_A["starter"]
    starter_B = team_B["starter"]
    starter_round_A = calc_starter_round(starter_A)
    starter_round_B = calc_starter_round(starter_B)

    bullpen_A = team_A["bullpen"]
    bullpen_B = team_B["bullpen"]
    closer_A = bullpen_A[-1] if bullpen_A else starter_A
    middle_A = bullpen_A[:-1] if bullpen_A else []
    closer_B = bullpen_B[-1] if bullpen_B else starter_B
    middle_B = bullpen_B[:-1] if bullpen_B else []

    middle_A_sorted = sorted(
        middle_A,
        key=lambda name: get_weighted_stat(pitchers_by_player.get(name, pd.DataFrame()), "ERA", year_weights)
    ) if middle_A else []
    middle_B_sorted = sorted(
        middle_B,
        key=lambda name: get_weighted_stat(pitchers_by_player.get(name, pd.DataFrame()), "ERA", year_weights)
    ) if middle_B else []

    team_A_pitchers = []
    team_B_pitchers = []
    for inning in range(1, 10):
        if inning <= starter_round_A:
            team_A_pitchers.append(starter_A)
        else:
            team_A_pitchers.append(middle_A_sorted[(inning - starter_round_A) % len(middle_A_sorted)] if middle_A_sorted else closer_A)
    for inning in range(1, 10):
        if inning <= starter_round_B:
            team_B_pitchers.append(starter_B)
        else:
            team_B_pitchers.append(middle_B_sorted[(inning - starter_round_B) % len(middle_B_sorted)] if middle_B_sorted else closer_B)
    for inning in range(1, 10):
        if inning == 9 and score_B > score_A:
            team_B_pitchers[-1] = closer_B
        score_A += simulate_offense(team_A["lineup"], team_B_pitchers[inning-1], batter_index)
        if inning == 9 and score_A > score_B:
            team_A_pitchers[-1] = closer_A
        score_B += simulate_offense(team_B["lineup"], team_A_pitchers[inning-1], batter_index)

    result = {
        "score_A": score_A,
        "score_B": score_B,
        "winner": "A" if score_A > score_B else "B" if score_B > score_A else "draw"
    }
    return result

if __name__ == "__main__":
    try:
        # suppress_stdout()로 불필요한 print 숨기기
        with suppress_stdout():
            if len(sys.argv) > 1:
                with open(sys.argv[1], 'r', encoding='utf-8') as f:
                    args = json.load(f)
            else:
                sys.exit(1)
        # 필요한 메시지만 표준출력
        
        start_time = time.time()
        multiprocessing.set_start_method("spawn", force=True)

        with multiprocessing.Manager() as manager:
            team_A_managed = manager.dict(args["team_A"])
            team_B_managed = manager.dict(args["team_B"])
            matcher_args = (
                "hitters.csv",
                "pitchers.csv",
                "hitters_type.csv",
                "pitchers_type.csv",
                team_A_managed,
                team_B_managed
            )
            with suppress_stdout():
                with ProcessPoolExecutor(
                        max_workers=multiprocessing.cpu_count(),
                        initializer=init_worker,
                        initargs=matcher_args
                    ) as executor:
                    results = list(executor.map(simulate_match, range(args.get("match_count", 1000))))
        end_time = time.time()
        elapsed_time = end_time - start_time
        team_A_wins = sum(1 for r in results if r["winner"] == "A")
        team_B_wins = sum(1 for r in results if r["winner"] == "B")
        draw = sum(1 for r in results if r["winner"] == "draw")
        total_score_A = sum(r["score_A"] for r in results)
        total_score_B = sum(r["score_B"] for r in results)
        output = {
            "team_A_win_count": team_A_wins,
            "team_B_win_count": team_B_wins,
            "draw_count": draw,
            "team_A_avg_score": total_score_A / args.get("match_count", 1000),
            "team_B_avg_score": total_score_B / args.get("match_count", 1000),
            "team_A_win_rate": team_A_wins / args.get("match_count", 1000),
            "team_B_win_rate": team_B_wins / args.get("match_count", 1000),
            "draw_rate": draw / args.get("match_count", 1000),
            "elapsed_time": elapsed_time
        }
        print(json.dumps(output, ensure_ascii=False), flush=True)
    except Exception as e:
        print(json.dumps({"error": str(e), "trace": traceback.format_exc()}), flush=True)

import json, math, os

IN = os.environ.get("MAKEFUN_INPUT_DIR", "/input")
OUT = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def main():
    task = json.load(open(os.path.join(IN, "task.json")))
    last = None
    first_seen = {}
    with open(os.path.join(IN, "history.ndjson")) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                m = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(m, dict) or not m.get("ok"):
                continue
            last = m
    rows = last["rows"] if last else []
    edges = task["size"]["edges"]
    n = len(rows)
    probs = {}
    # place k: mass spread over coins ranked near k (wider than the baseline,
    # since the reads are 7 to 13 hours after the history ends)
    for k in range(1, 6):
        w = {}
        for r in rows[:30]:
            d = r["rank"] - k
            if r["mayhem"] and r["venue"] != "pool":
                continue
            s = math.exp(-abs(d) * 0.9) if d <= 0 else math.exp(-d * 0.7)
            w[r["mint"]] = s
        tot = sum(w.values()) or 1.0
        for mint, s in w.items():
            probs[(mint, k)] = round(0.55 * s / tot, 6)
    plist = [{"mint": m, "place": k, "p": p} for (m, k), p in sorted(probs.items(), key=lambda x: (x[0][1], x[0][0]))]
    sizes = []
    for k in range(1, 6):
        if len(rows) >= k:
            mu = math.log10(max(int(rows[k - 1]["market_cap_lamports"]), 1)) - 9
        else:
            mu = 2.5
        sd = 0.45 + 0.03 * k
        bins = []
        for b in range(82):
            lo = -1e9 if b == 0 else edges[b - 1]
            hi = 1e9 if b == 81 else edges[b]
            cdf = lambda x: 0.5 * (1 + math.erf((x - mu) / (sd * math.sqrt(2))))
            bins.append(max(cdf(hi) - cdf(lo), 0.0))
        t = sum(bins) or 1.0
        for b, v in enumerate(bins):
            p = math.floor(0.9 * v / t * 1e6) / 1e6
            if p > 0:
                sizes.append({"place": k, "bin": b, "p": p})
    top5 = [r["mint"] for r in rows if not (r["mayhem"] and r["venue"] != "pool")][:5]
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "forecast.json"), "w") as f:
        json.dump({"probabilities": plist, "top5": top5, "sizes": sizes}, f, sort_keys=True, separators=(",", ":"))


main()

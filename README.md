# pumpfun-top5-forecast

Deterministic, stdlib-only forecaster for the make.fun `pumpfun-top5-forecast-01` bounty.

## Inputs

Read from `MAKEFUN_INPUT_DIR` (default `/input`):

- `task.json` — competition metadata, including the size-bin `edges`.
- `history.ndjson` — one JSON mark per line. Each mark has `ok`, `at`, and `rows`
  (ranked coins with `mint`, `rank`, `venue`, `mayhem`, `market_cap_lamports`, ...).

Malformed or non-object JSON lines, and marks with `ok` unset/false, are skipped.
The last valid mark supplies the current ranking.

## Output

Written to `MAKEFUN_OUTPUT_DIR` (default `/output`) as `forecast.json`:

- `probabilities`: `{mint, place, p}` entries. For each place `k`, weight each of
  the top 30 coins by a one-sided exponential decay of `rank - k` (decay `0.9`
  for coins ranked at or above `k`, `0.7` below it), drop mayhem coins outside
  the pool venue, normalize, and take `0.55` of the mass. The remainder is left
  unassigned because reads occur 7–13 hours after history ends.
- `top5`: the current top five eligible mints, in rank order.
- `sizes`: per place and size bin, a discretized log-normal CDF. The mean is
  `log10(market_cap_lamports) - 9` of the coin currently at that place (or `2.5`
  if unavailable), with `sd = 0.45 + 0.03 * k`. Bin masses are floored to 6
  decimal places and scaled by `0.9` to leave slack.

## Determinism

No randomness, clocks, network access, or non-stdlib imports. Output uses sorted
keys and compact separators, so identical inputs produce identical bytes.

## Usage

```sh
MAKEFUN_INPUT_DIR=../pumpfun-top5-forecast-01-kit/input \
MAKEFUN_OUTPUT_DIR=/tmp/out \
python3 main.py
```

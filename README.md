# Catalyst Watch

**Live:** https://everweston.github.io/catalyst-watch/

A daily-refreshable, navy/yellow web dashboard of **upcoming, potentially stock-moving catalysts** across your coverage list + watchlist — earnings, investor days, FDA / data readouts, product launches, deal & vote dates, lockups, index changes. Each entry shows **why it matters** and is tagged with a source + confidence and whether the date is confirmed or estimated.

Built for situational awareness. Dates are **web-sourced (no live terminal)** — verify before trading.

## Files
- `index.html` — the site (self-contained: data is embedded, so it opens locally **and** deploys to GitHub Pages unchanged).
- `data/catalysts.json` — the catalyst data (regenerated each refresh).
- `data/universe.json` — `coverage` + `watchlist` tickers. Add watchlist names here, then refresh.
- `build.py` — reads the JSON, writes `index.html`.

## View it locally
Open `index.html` in any browser (double-click), or:
```
cd ~/catalyst-watch && python3 -m http.server 8080   # then open http://localhost:8080
```

## Refresh the catalysts (on demand)
Ask Claude to **"refresh Catalyst Watch"** — it re-runs the research workflow, rewrites `data/catalysts.json`, runs `build.py`, and (if deployed) pushes so GitHub Pages updates.

To add watchlist tickers: edit `data/universe.json` `"watchlist": [...]`, then refresh.

Manual rebuild after editing the JSON:
```
cd ~/catalyst-watch && python3 build.py
```

## Deploy to GitHub Pages
The repo is git-ready. Once a GitHub remote exists and Pages is enabled (Settings → Pages → branch `main` / root), every push updates the live site. See the chat for the exact one-time setup steps (gh CLI or a manual repo + push).

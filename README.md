**Languages:** [English](README.md) | [简体中文](README.zh-CN.md)

After years of trading stocks, I never found a portfolio tracker I was fully happy with, so I built one—and picked up some related skills along the way.

# Screenshots

## Holdings & P/L

![image.png](https://s21.ax1x.com/2025/10/27/pVxFACd.png)

## Analytics

![image.png](https://s21.ax1x.com/2025/10/27/pVxFF4H.png)

## Dividend / rights adjustment

![image.png](https://s21.ax1x.com/2025/10/27/pVxFiUe.png)

## Highlights

- Complete and accurate per-stock and portfolio-level metrics.
- Full trade history per symbol.
- Auto-generated dividend and rights-adjustment records.
- Reliable stock sorting.
- Hong Kong Stock Connect: per-stock HKD display (`$`), portfolio totals in CNY via HKD/CNY spot rate.
- Minimal UI—no ads, no flashy distractions.

# Technical overview

## Backend

There are many ways to ship a simple web API. I had known Django since around 2010 and chose it when I started this project in 2021; any stack that ships fast would work. Python is a good fit for market data and P/L math.

The database is **SQLite**—we store little data, so the lightest, easiest-to-debug option made sense.

## Frontend

The first version used Vue + Element UI; it was later rebuilt with **Umi** + **Ant Design**.

I had not written much frontend before, so I spent time learning the framework and polishing UX. The second phase focused mainly on the UI.

## Data sources

**Live quotes** come from Tencent via [easyquotation](https://github.com/shidenggui/easyquotation)—stocks, on-exchange funds, convertible bonds, etc. Endpoint: `http://qt.gtimg.cn/q=`.

**Historical corporate actions** use [BaoStock](http://baostock.com/baostock/index.php) for dividend and rights-adjustment history (A-shares only; not available for HK). Valuation (PE/PB) and historical highs use Baidu opendata and Tencent gtimg instead of BaoStock.

## AI-assisted development

In 2025 I used AI to refactor code and upgrade dependencies with strong results. Learning has changed: I can often get what I need from prompts instead of long manual debugging and doc hunts. That is a productivity win, though it may not help newcomers who skip the hard parts of learning.

## Metrics (Xueqiu formulas)

All P/L formulas follow [Xueqiu (雪球)](https://xueqiu.com/) rules:

```
1. Cost basis
Shares held = ∑ buys + ∑ bonus shares + ∑ split shares − ∑ sells − ∑ reverse-split shares
Diluted cost = (∑ buy amount − ∑ sell amount − ∑ cash dividends) / shares held
Position cost = ∑ buy amount / (∑ buys + ∑ bonus shares + ∑ split shares − ∑ reverse-split shares)

2. Floating P/L
Floating P/L amount = (current price − position cost) × long shares
Floating P/L rate = floating P/L amount / (position cost × shares held)
Market floating P/L amount = ∑ per-stock floating P/L amounts
Market floating P/L rate = market floating P/L amount / ∑(position cost × shares per stock)

3. Cumulative P/L
Per-stock cumulative P/L = long market value − (∑ buy amount − ∑ sell amount − ∑ cash dividends)

4. Daily P/L
If yesterday’s market value > 0:
  Daily P/L = (today MV − yesterday close MV + today ∑ sells − today ∑ buys)
  Daily P/L rate = daily P/L / (yesterday MV + today ∑ buys + today ∑ short sells)
If yesterday’s market value = 0:
  Daily P/L = (price − position cost) × shares + today ∑ sells − today ∑ buys
  Daily P/L rate = daily P/L / today ∑ buys
Cash = principal + cumulative P/L − market value
```

One subtle rule: **position cost** for a symbol is computed only from the latest holding period after a full exit—many edge cases are handled in code.

## Data migration

You can export trades from your broker or another platform. My broker had no Mac client, so I went to a net café, installed their Windows app amid a room full of gamers, and exported everything—then spent a long time parsing spreadsheets and validating rows. That migration step was the most time-consuming part of the project.

# Local setup

## Manual setup (split dev servers)

1. Install Python (≥3.13), pip, git, and Redis.
2. Install Python deps from `requirements.txt`.
3. Install Node (≥20) and utoo (`npm install -g utoo`).
4. Clone: `https://github.com/gunerguner/stockManager`
5. In `stockManager/front`, run `ut install` (**no** `ut run build` needed for dev).
6. Create `.env` under `stockManager`: `cp stockManager/.env.example stockManager/.env`. Generate `DJANGO_SECRET_KEY` with:
   `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
7. Run `python manage.py makemigrations` and `python manage.py migrate` (or copy an existing SQLite file).
8. Run `python manage.py createsuperuser`.
9. Start Redis: `redis-server`.
10. **Two terminals:**
    - Terminal 1 (`stockManager`): `python manage.py runserver` → API & Admin on **8000**
    - Terminal 2 (`front`): `ut run dev` → app on **8001** (`/api/` proxied to 8000)

- App: http://127.0.0.1:8001
- Admin: http://127.0.0.1:8000/sys/admin/

## Automated setup

Run `./install.sh` (installs dependencies only; does not build frontend assets).

# Deployment

1. **Docker (recommended):** Frontend is built once in the `frontend` image; the backend image has no Umi bundle. See [docker/README.md](docker/README.md).
2. **Traditional:** Nginx serves `front/dist` and proxies the API; backend runs Gunicorn + Django Admin static files only.

# Project history

Work started in 2020; the first major rewrite and cloud deploy was in 2021, followed by many bug fixes through a small bull market in 2020–21 and a long bear market afterward.

Life and work kept me away from the repo for a long time.

At the end of 2025 I had time again for something I enjoy, so development resumed—with a goal of at least one update per year.

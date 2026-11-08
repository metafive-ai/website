# -*- coding: utf-8 -*-
"""Data behind the two trading charts. R only, never USD.

REPLAY_YEARS — book IDXAU-LOW-DD-FINAL, its own enforced replay `lowddfinal_y{2022..2026}_20261029`.
Source: metafive-360 docs/strategy/edge-final-verdict-20261103/by_year.json (key `lowddR`),
maintenance@ee18ab2. R per year = trades x avg_r (rounded); total published: +412.4 R.

DEMO_TRADES — closed trades of template IDXAU-LOW-DD-FINAL on the VPS2 demo account
(ICMarketsEU-Demo). Source: Google Drive MetaFive-Reports/VPS2/weekly/2026-W45/trades_closed.csv
(column r_multiple_price), export of 2026-11-08 11:11 UTC; no closed trade on 6-7 Nov 2026.
Update this list (via a pull request) when a new weekly export arrives.
"""

REPLAY_AS_OF = "2026-10-14"
REPLAY_YEARS = [  # (year, trades, avg_r)
    (2022, 440, 0.075),
    (2023, 541, 0.162),
    (2024, 486, 0.193),
    (2025, 587, 0.208),
    (2026, 383, 0.199),  # to 14 Oct 2026
]

DEMO_AS_OF = "2026-11-07"
DEMO_TRADES = [  # (close time UTC, instrument, direction, R)
    ("2026-11-02T14:39", "XAUUSD", "LONG", 1.474),
    ("2026-11-02T15:25", "STOXX50", "LONG", 1.912),
    ("2026-11-03T07:03", "US500", "LONG", -1.000),
    ("2026-11-04T00:45", "JP225", "SHORT", 2.119),
    ("2026-11-05T01:05", "XAUUSD", "LONG", 1.496),
    ("2026-11-05T16:18", "JP225", "SHORT", 2.595),
]

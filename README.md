# Playmaker Profiles: WC 2022's Hidden Playmakers

## Why
Goals and assists are the stats everyone looks at, but they miss the buildup work that creates chances in the first place. This project applies an Expected Threat (xT) model across the entire World Cup 2022 to find out who actually drove attacking value, not just who finished it.

## What it does
- Scores every pass and carry from all 64 WC2022 matches (122,279 actions) using a 12x8 zone value grid built from historical goal outcomes
- Splits each player's total xT into pass-xT vs carry-xT
- Compares total xT against actual goals + assists to flag undervalued players: high buildup value, low scoreboard credit

## Key findings
| Player | Team | Total xT | Goals + Assists |
|---|---|---|---|
| Antoine Griezmann | France | 8.47 | 3 |
| Lionel Messi | Argentina | 7.64 | 12 |
| Luka Modrić | Croatia | 7.37 | 1 |
| Hakim Ziyech | Morocco | 7.14 | 3 |

- Griezmann generated more attacking value than any player in the tournament, including Messi and Mbappé, despite only 3 goal contributions
- The most undervalued players by this measure: Joshua Kimmich, Kevin De Bruyne, Christian Eriksen, Rodrigo De Paul, Marcos Acuña, all with 0 goals or assists but heavy buildup xT
- Confirms xT measures a different skill than the scoresheet: progression and creation, not finishing

## Visual
`playmaker_profiles.png`: scatter plot of total xT vs goals + assists, with the most undervalued players labeled.

## Tools
Python, pandas, matplotlib

## Data source
StatsBomb open data (via `statsbombpy`), World Cup 2022, all 64 matches, competition_id=43, season_id=106

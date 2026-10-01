<div align="center">
  <img src="eggsauce.png" alt="Eggsauce logo" width="180" height="180">
  <h1>Eggsauce</h1>
  <p><strong>A farming and battling game for Discord, built in Python on a layered, test-backed architecture.</strong></p>

  <p>
    <img alt="Python" src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white">
    <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-18-4169E1?logo=postgresql&logoColor=white">
    <img alt="Docker" src="https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white">
  </p>
</div>

---

## About

Eggsauce is a Discord bot where players build a chicken farm, grow a cornfield, trade with each other and climb a ranked ladder in chicken battles. It has 35+ commands across four modules: Farm, Cornfield, Player economy, and Server config.

This repository is **v2**, a ground-up rewrite of the [original bot](https://github.com/Pedro05Souza/old-eggsauce). The goal was a codebase that can grow without slowing down: explicit layers, typed entities, a write-back cache in front of the database, and CI checks on every pull request.

## Highlights

- **Write-back entity cache** ([`_entity_cache.py`](../tools/services/cache/_entity_cache.py)): a TTL cache in front of PostgreSQL that cuts database traffic during busy sessions.
  - Hits take no lock, and a miss is fetched once per key using a per-key lock.
  - Expiration is sliding, so entities in active use stay in memory.
  - Dirty tracking compares snapshots, so unchanged entities are never written. Failed saves stay in a pending buffer and are retried on the next flush.
  - Keys that don't exist in the database are cached for a short time.
  - A background task flushes periodically, and a `SIGTERM` handler flushes on `docker stop`, so no progress is lost.
- **Ranked matchmaking with Elo** ([`elo_rating_service.py`](../tools/services/elo_rating_service.py), [`match_making_service.py`](../tools/services/match_making_service.py)):
  - Ratings work like chess Elo, with placement matches and a smaller K-factor at the top rank.
  - Players are pooled into MMR buckets, and the search widens to nearby buckets after repeated misses.
  - When no human opponent is found, a bot fills in, and its deck strength scales with the player's MMR.
- **Atomic economy**: balance and bank operations run inside database transactions ([`transaction_service.py`](../tools/services/transaction_service.py)). An action guard keeps players from being involved in two conflicting actions at once (for example, a trade during a battle).
- **Idle progression**: players earn from the time they were away, computed when they come back ([`away_time_earnings_service.py`](../tools/services/away_time_earnings_service.py)).

## Architecture

```
controllers/   Discord cogs: parse commands, call a use case, reply
usecases/      One class per command, holding the game rules
entities/      Plain domain objects (Player, Farm, Chicken, Cornfield)
repositories/  Data access behind Protocol interfaces, with mappers between ORM models and entities
models/        Tortoise ORM models (PostgreSQL), migrations managed by Aerich
tools/         Services (cache, Elo, matchmaking, transactions), constants, decorators
tests/         pytest + pytest-asyncio suites
```

The flow is always `controller → use case → repository → database`. Use cases only depend on repository *protocols*, so the tests can swap in mocks without touching the database.

## Tech stack

| Area | Tools |
|---|---|
| Language | Python 3.12 (fully type-annotated) |
| Bot framework | discord.py 2.7 |
| Database | PostgreSQL, Tortoise ORM, asyncpg, Aerich migrations |
| Caching | cachetools (TTL), custom write-back layer |
| Tooling | uv, Click CLI, Docker Compose, Adminer |
| Quality | pytest, pyright, pylint, black, GitHub Actions |

## Quality and CI

Every pull request runs three GitHub Actions workflows:

- **Tests**: `pytest` covers the battle use case, the Elo rating service, matchmaking and the config use cases.
- **Type checker**: `pyright` in standard mode.
- **Lint**: `pylint`, with formatting enforced by `black`.

## Getting started

### Prerequisites

- [uv](https://astral.sh/uv/) (it installs Python 3.12 if needed)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- A Discord bot token ([Discord Developer Portal](https://discord.com/developers/applications))

### Setup

```bash
git clone https://github.com/Pedro05Souza/eggsaucev2.git
cd eggsaucev2
uv sync --python 3.12          # creates the venv and installs the `eggsauce` CLI
cp .env.template .env          # then fill in your bot token(s)
```

> The bot will not start without valid environment variables.

### Run

```bash
uv run eggsauce run --env dev   # or --env prod
```

This starts the bot, PostgreSQL and Adminer (database UI on `localhost:8080`) through Docker Compose.

### CLI reference

| Command | What it does |
|---|---|
| `uv run eggsauce run --env <dev\|prod>` | Start the bot and its services |
| `uv run eggsauce build` | Build the Docker images |
| `uv run eggsauce migrate -name <name>` | Generate a migration and apply it |
| `uv run eggsauce apply-migrations` | Apply pending migrations |

### Run the checks locally

```bash
uv run pytest
uv run pyright .
uv run pylint .
```

## Commands overview

| Module | Examples |
|---|---|
| Farm | `farm`, `market`, `battle`, `friendlybattle`, `tradechicken`, `evolvechicken`, `ascendancy`, `vault` |
| Cornfield | `cornfield`, `buyplot`, `expandcornfield`, `sellcorn` |
| Player | `balance`, `deposit`, `withdraw`, `steal`, `slots`, `spin`, `upgradebank` |
| Config | `setprefix`, `togglecanstealchickens` |

Use `$help` in Discord for the full list. The default prefix is `$` and can be changed per server.

## Author

**Pedro Henrique Ferreira Souza**: [GitHub](https://github.com/Pedro05Souza) · [LinkedIn](https://www.linkedin.com/in/pedro-henrique-ferreira-souza)

# Contributing to Ayushman Bharat Healthtech Platform

Thank you for your interest in contributing! This project aims to build equitable, AI-assisted healthcare infrastructure aligned with India's ABDM mission.

## Getting Started
1. Fork the repository and clone locally.
2. Copy `.env.example` to `.env` and fill in required secrets.
3. Run `docker-compose up --build` to start all services.
4. Run `pytest tests/ -v` to verify everything works.

## Branching Strategy
- `main` — stable, production-ready code.
- `feature/<name>` — new features, branched from `main`.
- `fix/<name>` — bug fixes.
- `docs/<name>` — documentation improvements.

## Commit Message Convention
Follow [Conventional Commits](https://www.conventionalcommits.org/):
```
feat(scope): short description
fix(scope): short description
docs(scope): short description
```

## Code of Conduct
All contributors must adhere to respectful, inclusive communication. Healthcare data is sensitive — treat every contribution with the gravity it deserves.

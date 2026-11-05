# Contributing to AeroPulse

AeroPulse is an educational engineering portfolio project. Changes should make its data lineage, model evaluation, API behavior, or user-facing explanation clearer.

## Development rules

- Keep raw input data separate from transformed data and generated model artifacts.
- Never label synthetic data as NASA telemetry.
- Keep held-out evaluation targets out of the dashboard's operational records.
- Evaluate by engine identity to avoid trajectory leakage.
- Use historical-only rolling windows; do not use centered windows or future observations.
- Add tests for new feature transformations, endpoints, or classification rules.
- Never commit `.env` files, database files, credentials, downloaded raw datasets, or fitted model artifacts.
- Document assumptions, dataset provenance, and model limitations.

## Before opening a pull request

```bash
cd backend
python -m pytest -q
cd ../frontend
npm install
npm run build
```

Describe the problem, your approach, how you tested it, and any known limitations.

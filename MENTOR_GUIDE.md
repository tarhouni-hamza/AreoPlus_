# AeroPulse — Beginner-to-Builder Mentor Guide

This guide is designed to help you own the project rather than merely run code that an AI generated. Your goal is to become able to explain, modify, test, and defend each layer.

## The rule

AI can accelerate scaffolding, explain unfamiliar APIs, suggest tests, and help debug. It cannot replace your engineering judgment. Never merge code you cannot explain. Keep a `LEARNING_NOTES.md` file in your own working copy and record what you learned, what failed, and what you changed.

## Four-week build-and-understand path

### Week 1 — Data and Python foundations

**Goal:** Understand the raw dataset and create a trustworthy data pipeline.

1. Read the NASA dataset description and the FD001 column layout.
2. Open `backend/app/data/run_nasa_pipeline.py` and trace the three input files.
3. Explain what one row means: one engine, one operating cycle, three settings, and 21 sensor values.
4. Manually calculate RUL for a tiny made-up trajectory. Example: an engine reaches cycle 10; the row at cycle 7 has 3 cycles of RUL before the final training cycle.
5. Change the data-quality logic to reject duplicate engine-cycle pairs and missing sensor values.
6. Write a test for each new rule.

**You should be able to answer:** Why does training data contain a known end-of-life cycle? Why does the test data need a separate RUL target file? Why is raw data kept separate from model features?

### Week 2 — Data engineering and machine learning

**Goal:** Understand how raw measurements become a model estimate.

1. Trace `add_features()` in `backend/app/ml/features.py`.
2. Calculate a five-row rolling mean by hand for one sensor.
3. Explain why rolling windows must use only the current and previous rows.
4. Read `train_and_evaluate()` and identify the exact point where the model is fitted and where it is evaluated.
5. Compare the Random Forest with a naive constant-RUL baseline.
6. Change one feature group, rerun evaluation, and record whether MAE improves or worsens.
7. Explain MAE, RMSE, and R² in ordinary language.

**You should be able to answer:** What is data leakage? Why is a random row split dangerous for time-series engine data? What does an MAE of 5 cycles mean?

### Week 3 — Backend and database

**Goal:** Understand the request path from browser to database.

1. Start FastAPI and open `/docs`.
2. Call `GET /api/overview` and inspect the JSON response.
3. Trace the endpoint in `backend/app/routers/dashboard.py` into `analytics.py` and SQLAlchemy models.
4. Explain the relationship between `Engine` and `EngineObservation`.
5. Add a `GET /api/engines/{id}/observations` endpoint with cycle pagination.
6. Add tests for a valid engine, an unknown engine, and an empty database.

**You should be able to answer:** Why do we persist predictions? Why does the dashboard call an API rather than read a CSV directly? What does a 404 mean?

### Week 4 — Frontend, product thinking, and delivery

**Goal:** Make the project usable and explain its value.

1. Trace `loadData()` in `frontend/src/App.jsx`.
2. Find where the overview cards, risk chart, and table are rendered.
3. Add a sensor selector so a user can choose which channel appears on an engine profile.
4. Add a CSV export test or manual verification checklist.
5. Run the backend tests and frontend production build.
6. Draw the architecture from memory without looking at the README.
7. Record a 90-second walkthrough: problem, data source, pipeline, model evaluation, API, dashboard, limitations.

**You should be able to answer:** Who is the user? What decision does this screen help them make? What happens if the API is unavailable? What would you change before production?

## Interview questions you should prepare

1. Why did you choose a Random Forest as your first model?
2. What baseline would you compare it with?
3. Why do you split by engine rather than by individual row?
4. How do rolling features avoid future-data leakage?
5. Where is the model artifact saved, and how does the API use its output?
6. What is the difference between a predicted RUL and the ground-truth RUL?
7. Why are risk thresholds in a service rather than inside the ML model?
8. What happens when an engine has an incomplete history?
9. How would you monitor data drift?
10. What would you need to validate before deploying this in a real maintenance organization?

## A safe, effective AI workflow

When asking an AI coding assistant for help, use this sequence:

1. **Ask for a design explanation first.** Request assumptions, alternatives, and failure cases before code.
2. **Request one small change.** Avoid asking it to rewrite the whole repository.
3. **Ask for tests.** Require a test that fails before the change and passes afterward.
4. **Inspect the diff.** Check whether the assistant changed unrelated files or silently changed behavior.
5. **Run it yourself.** Run tests, inspect API responses, and check the UI.
6. **Explain it without AI.** If you cannot explain why the code works, do not present it as your own engineering work yet.

## The standard for calling it portfolio-ready

- You can install and run it from a clean clone using the README.
- Backend tests pass and the frontend production build succeeds.
- NASA data provenance and the synthetic demo data are clearly distinguished.
- You can explain the data split, feature engineering, model metrics, API, and schema.
- You have at least three meaningful commits that show incremental work, not one giant generated dump.
- You include a short screen recording or screenshots from a working local run.
- You describe limitations accurately and do not claim live aircraft or production safety use.

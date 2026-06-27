@AGENTS.md



\# Project: HackerRank Orchestrate



\## What this is

Multi-modal damage claim verification system for a hackathon.

Verifies images against user damage claims for cars, laptops, and packages.



\## Stack

\- Python 3.x with asyncio for concurrency

\- Anthropic SDK (claude-sonnet-4-6 with vision)

\- pandas for CSV handling



\## File structure

\- code/main.py — main entry point, reads claims.csv, writes output.csv

\- code/evaluation/main.py — evaluation entry point, runs against sample\_claims.csv

\- dataset/claims.csv — test input (no labels)

\- dataset/sample\_claims.csv — labeled examples for development and eval

\- dataset/user\_history.csv — user risk history

\- dataset/evidence\_requirements.csv — minimum evidence rules per object type

\- dataset/images/ — all images referenced by the CSVs



\## Output schema (14 columns, in order)

user\_id, image\_paths, user\_claim, claim\_object,

evidence\_standard\_met, evidence\_standard\_met\_reason,

risk\_flags, issue\_type, object\_part, claim\_status,

claim\_status\_justification, supporting\_image\_ids,

valid\_image, severity



\## Key rules

\- Images are the primary source of truth

\- Use asyncio.gather for concurrent claim processing

\- Never hardcode labels or file-specific answers

\- Always read evidence\_requirements.csv dynamically



\## gitignore

We use a .venv virtual environment. Always ignore .venv, \_\_pycache\_\_, .env, output.csv from git.


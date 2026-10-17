# Career Navigator & Skill Gap Agent

hackFront India 2026 Pre-Hack Series: Neo4j Graph Builder, Build Sprint Bengaluru

Pick a goal role, tick the skills you already have, and get a learning path plus a colored skill graph.

## How it works

1. Roles and skills come from the ESCO dataset (European Commission), loaded into Neo4j.
2. The app compares the skills a role requires with the skills you have.
3. Missing skills are ordered using `PREREQUISITE_OF` links, so the first item is what to learn next.
4. The graph shows green (you have it), red (missing), amber (prerequisite the role does not list), and blue (your goal).

## Graph model

- (:Role {uri, name, isco})
- (:Skill {uri, name, type})
- (Role)-[:REQUIRES {level}]->(Skill), level is essential or optional
- (Skill)-[:RELATED_TO {level}]->(Skill)
- (Skill)-[:PREREQUISITE_OF]->(Skill), added by hand for the featured roles

## Setup

1. Download the ESCO dataset (English, CSV) from https://esco.ec.europa.eu/en/use-esco/download and unzip it. It is not stored in this repo.
2. Create a free Neo4j Aura instance and copy `.env.example` to `.env`, then fill in your own details. Never commit `.env`.
3. Install and load:

```
pip install -r requirements.txt
python load_esco.py <path to unzipped ESCO folder> --dry-run
python load_esco.py <path to unzipped ESCO folder>
```

4. Run the app:

```
streamlit run app.py
```

## Files

- `load_esco.py` loads ESCO roles, skills, and links into Neo4j
- `pathing.py` orders the learning path (pure Python, no database)
- `app.py` Streamlit screen with the answer and the graph
- `skill_gap.cypher` example skill-gap query

## Data credit

Occupation and skill data: ESCO, European Commission. Check their terms of use before redistributing the data.

## Team

Add team members here.

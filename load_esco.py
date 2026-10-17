"""Load the ESCO English CSV dataset into Neo4j for the Career Navigator.

Graph created:
  (:Role  {uri, name, isco})
  (:Skill {uri, name, type})            type = 'skill/competence' or 'knowledge'
  (Role)-[:REQUIRES {level}]->(Skill)   level = 'essential' or 'optional'
  (Skill)-[:RELATED_TO {level}]->(Skill)

ESCO has no skill prerequisite order. Add (Skill)-[:PREREQUISITE_OF]->(Skill)
yourself for the demo roles (see prerequisites_demo.cypher).

Usage:
  python load_esco.py /path/to/unzipped/esco --dry-run      # only count, no database
  python load_esco.py /path/to/unzipped/esco                # load into Neo4j

Credentials come from environment variables or a .env file:
  NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
"""
import csv
import os
import sys

BATCH = 2000


def read(folder, name):
    with open(os.path.join(folder, name), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def chunks(rows, n=BATCH):
    for i in range(0, len(rows), n):
        yield rows[i:i + n]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    if not args:
        sys.exit(__doc__)
    folder = args[0]

    occs = read(folder, "occupations_en.csv")
    skills = read(folder, "skills_en.csv")
    occ_skill = read(folder, "occupationSkillRelations_en.csv")
    skill_skill = read(folder, "skillSkillRelations_en.csv")

    roles = [{"uri": o["conceptUri"], "name": o["preferredLabel"], "isco": o["iscoGroup"]} for o in occs]
    skill_rows = [{"uri": s["conceptUri"], "name": s["preferredLabel"], "type": s["skillType"]} for s in skills]
    requires = [{"role": r["occupationUri"], "skill": r["skillUri"], "level": r["relationType"]} for r in occ_skill]
    related = [{"a": r["originalSkillUri"], "b": r["relatedSkillUri"], "level": r["relationType"]} for r in skill_skill]

    print(f"roles={len(roles)} skills={len(skill_rows)} requires={len(requires)} related={len(related)}")
    if dry:
        return

    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(
        os.environ["NEO4J_URI"],
        auth=(
            os.environ.get("NEO4J_USERNAME") or os.environ["NEO4J_USER"],
            os.environ["NEO4J_PASSWORD"],
        ),
    )
    with driver, driver.session() as s:
        s.run("CREATE CONSTRAINT role_uri IF NOT EXISTS FOR (r:Role) REQUIRE r.uri IS UNIQUE")
        s.run("CREATE CONSTRAINT skill_uri IF NOT EXISTS FOR (k:Skill) REQUIRE k.uri IS UNIQUE")
        s.run("CREATE INDEX role_name IF NOT EXISTS FOR (r:Role) ON (r.name)")
        s.run("CREATE INDEX skill_name IF NOT EXISTS FOR (k:Skill) ON (k.name)")

        for b in chunks(roles):
            s.run("UNWIND $rows AS r MERGE (n:Role {uri: r.uri}) SET n.name = r.name, n.isco = r.isco", rows=b)
        for b in chunks(skill_rows):
            s.run("UNWIND $rows AS r MERGE (n:Skill {uri: r.uri}) SET n.name = r.name, n.type = r.type", rows=b)
        for b in chunks(requires):
            s.run(
                "UNWIND $rows AS r MATCH (a:Role {uri: r.role}), (k:Skill {uri: r.skill}) "
                "MERGE (a)-[x:REQUIRES]->(k) SET x.level = r.level",
                rows=b,
            )
        for b in chunks(related):
            s.run(
                "UNWIND $rows AS r MATCH (a:Skill {uri: r.a}), (c:Skill {uri: r.b}) "
                "MERGE (a)-[x:RELATED_TO]->(c) SET x.level = r.level",
                rows=b,
            )
    print("Done.")


if __name__ == "__main__":
    main()

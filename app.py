import os
import tempfile

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from neo4j import GraphDatabase
from pyvis.network import Network

from pathing import learning_path

load_dotenv()

COLORS = {
    "have": "#3B6D11",     # green: user knows it
    "missing": "#A32D2D",  # red: needs to learn
    "extra": "#854F0B",    # amber: prerequisite the role does not list
    "goal": "#185FA5",     # blue: the role
}


@st.cache_resource
def driver():
    return GraphDatabase.driver(
        os.environ["NEO4J_URI"],
        auth=(
            os.environ.get("NEO4J_USERNAME") or os.environ["NEO4J_USER"],
            os.environ["NEO4J_PASSWORD"],
        ),
    )


def q(cypher, **params):
    with driver().session() as s:
        return [r.data() for r in s.run(cypher, **params)]


@st.cache_data(show_spinner=False)
def all_roles():
    return [r["name"] for r in q("MATCH (r:Role) RETURN r.name AS name ORDER BY name")]


@st.cache_data(show_spinner=False)
def role_skills(role):
    rows = q(
        "MATCH (r:Role {name:$role})-[x:REQUIRES]->(s:Skill) "
        "RETURN s.name AS name, x.level AS level ORDER BY (x.level='essential') DESC, name",
        role=role,
    )
    return rows


@st.cache_data(show_spinner=False)
def prereq_map():
    rows = q("MATCH (a:Skill)-[:PREREQUISITE_OF]->(b:Skill) RETURN a.name AS a, b.name AS b")
    m = {}
    for r in rows:
        m.setdefault(r["b"], set()).add(r["a"])
    return m


def draw(role, required, known, path, extra, prereqs):
    net = Network(height="520px", width="100%", directed=True, bgcolor="#ffffff", font_color="#222222")
    net.add_node(role, label=role, color=COLORS["goal"], shape="box", font={"color": "#ffffff"})
    shown = set(required) | set(path)
    for s in shown:
        if s in known:
            color = COLORS["have"]
        elif s in extra:
            color = COLORS["extra"]
        else:
            color = COLORS["missing"]
        net.add_node(s, label=s, color=color, font={"color": "#ffffff"}, shape="box")
    for s in required:
        net.add_edge(s, role)
    for s in shown:
        for p in prereqs.get(s, ()):
            if p in shown:
                net.add_edge(p, s, dashes=True)
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        net.save_graph(f.name)
        html = open(f.name, encoding="utf-8").read()
    components.html(html, height=540)


st.set_page_config(page_title="Career Navigator", layout="wide")
st.title("Career Navigator & Skill Gap Agent")

roles = all_roles()
role = st.selectbox("Goal role", roles, index=None, placeholder="Search for a role")
if role:
    rows = role_skills(role)
    required = [r["name"] for r in rows]
    essential = {r["name"] for r in rows if r["level"] == "essential"}
    st.caption(f"{len(required)} skills listed for this role ({len(essential)} essential)")

    known = set(st.multiselect("Skills you already have", required))
    prereqs = prereq_map()
    path, extra = learning_path(essential or set(required), known, prereqs)

    left, right = st.columns([2, 3])
    with left:
        if not path:
            st.success("You already have every essential skill for this role.")
        else:
            st.subheader(f"Next: learn {path[0]}")
            st.write("Learning order:")
            for i, s in enumerate(path, 1):
                tag = " (prerequisite)" if s in extra else ""
                st.write(f"{i}. {s}{tag}")
        st.markdown(
            "<small>Green = you have it. Red = missing. Amber = prerequisite the role does not list. "
            "Blue = your goal. Dashed arrows = learn first.</small>",
            unsafe_allow_html=True,
        )
    with right:
        shown_required = list(essential or required)
        draw(role, shown_required, known, path, set(extra), prereqs)

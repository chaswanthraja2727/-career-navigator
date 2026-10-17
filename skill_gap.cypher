// Skill gap for one user and one role. Replace the two parameters.
// :param role => 'web developer'
// :param known => ['HTML', 'CSS', 'python']
//
// Green = user has it, red = missing, gray = known but not needed.
MATCH (r:Role) WHERE toLower(r.name) = toLower($role)
MATCH (r)-[q:REQUIRES]->(s:Skill)
WITH r, s, q,
     any(k IN $known WHERE toLower(k) = toLower(s.name)) AS has
RETURN s.name AS skill, q.level AS level,
       CASE WHEN has THEN 'green' ELSE 'red' END AS color
ORDER BY (q.level = 'essential') DESC, has, s.name;

// Demo prerequisites. ESCO does not include these, so add them by hand
// for the roles you demo. Names must match skills that exist in your graph.
// MATCH (a:Skill {name: 'HTML'}), (b:Skill {name: 'CSS'})
// MERGE (a)-[:PREREQUISITE_OF]->(b);

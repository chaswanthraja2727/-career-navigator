"""Learning-path logic, kept free of any database code so it is easy to test."""


def learning_path(required, known, prereqs):
    """Order the skills a user still has to learn.

    required: set of skill names the role needs
    known:    set of skill names the user already has
    prereqs:  dict skill -> set of skills that must be learned first

    Returns (path, extra) where path is the learning order (list of names) and
    extra is the subset of path that is a prerequisite but not required by the role.
    Skills the user already knows are never in the path.
    """
    known = set(known)
    needed = set(required) - known

    # pull in missing prerequisites of anything we need (walk up the chain)
    stack = list(needed)
    while stack:
        s = stack.pop()
        for p in prereqs.get(s, ()):
            if p not in known and p not in needed:
                needed.add(p)
                stack.append(p)

    # Kahn's algorithm: a skill is ready once all its needed prerequisites are done
    remaining = {s: {p for p in prereqs.get(s, ()) if p in needed} for s in needed}
    path = []
    while remaining:
        ready = sorted(s for s, deps in remaining.items() if not deps)
        if not ready:  # cycle in the data: add the rest alphabetically instead of looping
            ready = sorted(remaining)
        for s in ready:
            path.append(s)
            del remaining[s]
        for deps in remaining.values():
            deps.difference_update(ready)

    extra = [s for s in path if s not in set(required)]
    return path, extra

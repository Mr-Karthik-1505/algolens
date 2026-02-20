import re

def analyze_c(code: str):

    issues = []
    recursive_functions = []
    loop_depth = 0
    max_depth = 0

    lines = code.splitlines()
    brace_stack = 0

    # -------- LOOP DEPTH --------
    for line in lines:
        stripped = line.strip()

        if re.search(r'\b(for|while)\b', stripped):
            brace_stack += 1
            max_depth = max(max_depth, brace_stack)

        if "}" in stripped and brace_stack > 0:
            brace_stack -= 1

    loop_depth = max_depth

    # -------- RECURSION --------
    functions = re.findall(r'\b(int|void|float|double|char)\s+(\w+)\s*\(', code)

    for _, fname in functions:
        body = code.split(fname, 1)[-1]
        if re.search(r'\b' + fname + r'\s*\(', body):
            recursive_functions.append(fname)

    # -------- CYCLOMATIC COMPLEXITY --------
    complexity = 1
    complexity += len(re.findall(r'\bif\b', code))
    complexity += len(re.findall(r'\bfor\b', code))
    complexity += len(re.findall(r'\bwhile\b', code))
    complexity += len(re.findall(r'\bcase\b', code))
    complexity += len(re.findall(r'&&|\|\|', code))

    # -------- ISSUES --------
    if loop_depth > 3:
        issues.append("Deep nested loops")

    if complexity > 15:
        issues.append("High cyclomatic complexity")

    quality_score = max(
        0,
        100 - (complexity * 2) - (loop_depth * 5) - (len(issues) * 5)
    )

    # -------- SIMPLE CFG GENERATION --------
    nodes = []
    edges = []

    node_id = 1
    prev_node = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped:
            nodes.append({
                "id": node_id,
                "label": stripped,
                "lineno": i + 1
            })

            if prev_node is not None:
                edges.append({
                    "source": prev_node,
                    "target": node_id
                })

            prev_node = node_id
            node_id += 1

    cfg = {
        "nodes": nodes,
        "edges": edges
    }

    return {
        "loop_depth": loop_depth,
        "recursive_functions": recursive_functions,
        "estimated_complexity": f"O(n^{loop_depth})" if loop_depth > 0 else "O(1)",
        "cyclomatic_complexity": complexity,
        "quality_score": quality_score,
        "issues": issues,
        "suggestions": ["Consider refactoring"] if issues else [],
        "cfg": cfg
    }
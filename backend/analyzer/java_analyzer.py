import re

def analyze_java(code: str):

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
    functions = re.findall(r'\b(public|private|protected)?\s*(static)?\s*(void|int|double|float|String)\s+(\w+)\s*\(', code)

    for match in functions:
        fname = match[-1]
        body = code.split(fname, 1)[-1]
        if re.search(r'\b' + fname + r'\s*\(', body):
            recursive_functions.append(fname)

    # -------- COMPLEXITY --------
    complexity = 1
    complexity += len(re.findall(r'\bif\b', code))
    complexity += len(re.findall(r'\bfor\b', code))
    complexity += len(re.findall(r'\bwhile\b', code))
    complexity += len(re.findall(r'\bcase\b', code))
    complexity += len(re.findall(r'&&|\|\|', code))

    if loop_depth > 3:
        issues.append("Deep nested loops")

    if complexity > 15:
        issues.append("High cyclomatic complexity")

    quality_score = max(
        0,
        100 - (complexity * 2) - (loop_depth * 5) - (len(issues) * 5)
    )

# -------- STRUCTURED CFG WITH LOOP BACK EDGES --------

    nodes = []
    edges = []

    node_id = 1
    prev_node = None
    loop_stack = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        if stripped and not stripped.startswith("//"):

            nodes.append({
                "id": node_id,
                "label": stripped,
                "lineno": i + 1
            })

            # Normal forward edge
            if prev_node is not None:
                edges.append({
                    "source": prev_node,
                    "target": node_id
                })

            # Detect loop start
            if re.search(r'\b(for|while)\b', stripped):
                loop_stack.append(node_id)

            # Detect loop end
            if "}" in stripped and loop_stack:
                loop_start = loop_stack.pop()

                # Add back edge (loop back)
                edges.append({
                    "source": node_id,
                    "target": loop_start
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
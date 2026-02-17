import ast

class PatternDetector(ast.NodeVisitor):
    def __init__(self):
        self.issues = []

    def visit_For(self, node):
        # nested loop detection
        for child in ast.walk(node):
            if isinstance(child, ast.For):
                self.issues.append("Nested loop detected — may cause O(n²) complexity.")
        self.generic_visit(node)

    def visit_Call(self, node):
        # inefficient list search
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == "append":
                pass
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        # long function warning
        if len(node.body) > 20:
            self.issues.append(f"Function '{node.name}' is too long. Consider breaking it into smaller functions.")
        self.generic_visit(node)

    def detect(self, tree):
        self.visit(tree)
        return self.issues

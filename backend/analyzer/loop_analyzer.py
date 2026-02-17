import ast

class LoopAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.loop_depth = 0
        self.max_depth = 0

    def visit_For(self, node):
        self.loop_depth += 1
        self.max_depth = max(self.max_depth, self.loop_depth)
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_While(self, node):
        self.loop_depth += 1
        self.max_depth = max(self.max_depth, self.loop_depth)
        self.generic_visit(node)
        self.loop_depth -= 1
1
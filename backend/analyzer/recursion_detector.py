import ast

class RecursionDetector(ast.NodeVisitor):
    def __init__(self):
        self.recursive_functions = set()
        self.current_function = None

    def visit_FunctionDef(self, node):
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = None

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id == self.current_function:
                self.recursive_functions.add(self.current_function)
        self.generic_visit(node)

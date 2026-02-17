import ast

class ASTParser:
    def __init__(self, code):
        self.code = code
        self.tree = ast.parse(code)

    def get_tree(self):
        return self.tree

import ast
import networkx as nx


class CFGGenerator(ast.NodeVisitor):
    def __init__(self, source_code):
        self.graph = nx.DiGraph()
        self.node_count = 0
        self.previous_node = None
        self.source_lines = source_code.split("\n")

    # ---- Helper to add nodes ----
    def add_node(self, label, lineno=None):
        node_id = f"node_{self.node_count}"

        self.graph.add_node(
            node_id,
            label=label,
            lineno=lineno
        )

        if self.previous_node:
            self.graph.add_edge(self.previous_node, node_id)

        self.previous_node = node_id
        self.node_count += 1

    # ---- Visitors ----

    def visit_FunctionDef(self, node):
        self.add_node(f"def {node.name}(...)", node.lineno)
        self.generic_visit(node)

    def visit_For(self, node):
        self.add_node("for loop", node.lineno)
        self.generic_visit(node)

    def visit_While(self, node):
        self.add_node("while loop", node.lineno)
        self.generic_visit(node)

    def visit_If(self, node):
        self.add_node("if condition", node.lineno)
        self.generic_visit(node)

    def visit_Return(self, node):
        self.add_node("return statement", node.lineno)
        self.generic_visit(node)

    def visit_Expr(self, node):
        self.add_node("expression", node.lineno)
        self.generic_visit(node)

    # ---- Generate CFG ----

    def generate(self):
        tree = ast.parse("\n".join(self.source_lines))
        self.visit(tree)
        return self.graph

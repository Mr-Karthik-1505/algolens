import subprocess
import tempfile
import time

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from analyzer.ast_parser import ASTParser
from analyzer.loop_analyzer import LoopAnalyzer
from analyzer.recursion_detector import RecursionDetector
from analyzer.complexity_engine import ComplexityEngine
from analyzer.optimizer import Optimizer
from analyzer.cfg_generator import CFGGenerator
from analyzer.cyclomatic import CyclomaticComplexity
from analyzer.pattern_detector import PatternDetector
from analyzer.quality_score import QualityScorer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeInput(BaseModel):
    code: str
    language: str
    user_input: str = ""

@app.get("/")
def root():
    return {"message": "Server is working perfectly"}


# ---------------- ANALYZE ENDPOINT ----------------
@app.post("/analyze")
async def analyze_code(input_data: CodeInput):

    parser = ASTParser(input_data.code)
    tree = parser.get_tree()

    # Loop analysis
    loop_analyzer = LoopAnalyzer()
    loop_analyzer.visit(tree)

    # Recursion detection
    recursion_detector = RecursionDetector()
    recursion_detector.visit(tree)

    # Complexity estimation
    complexity_engine = ComplexityEngine()
    estimated_complexity = complexity_engine.estimate(
        loop_analyzer.max_depth,
        recursion_detector.recursive_functions
    )

    # Optimization suggestions
    optimizer = Optimizer()
    suggestions = optimizer.suggest(
        loop_analyzer.max_depth,
        recursion_detector.recursive_functions
    )

    # CFG generation
    cfg_generator = CFGGenerator(input_data.code)
    cfg_graph = cfg_generator.generate()

    nodes = [
        {
            "id": node,
            "label": data["label"],
            "lineno": data.get("lineno")
        }
        for node, data in cfg_graph.nodes(data=True)
    ]

    edges = [
        {
            "source": source,
            "target": target
        }
        for source, target in cfg_graph.edges()
    ]

    # Cyclomatic complexity
    cyclomatic = CyclomaticComplexity()
    cyclomatic_complexity = cyclomatic.calculate(tree)

    # Pattern detection
    pattern_detector = PatternDetector()
    issues = pattern_detector.detect(tree)

    # Quality score
    quality_scorer = QualityScorer()
    quality_score = quality_scorer.score(
        cyclomatic_complexity,
        loop_analyzer.max_depth,
        recursion_detector.recursive_functions,
        issues
)


    return {
        "loop_depth": loop_analyzer.max_depth,
        "recursive_functions": list(recursion_detector.recursive_functions),
        "estimated_complexity": estimated_complexity,
        "suggestions": suggestions,
        "cyclomatic_complexity": cyclomatic_complexity,
        "quality_score": quality_score,
        "issues": issues,
        "cfg": {
            "nodes": nodes,
            "edges": edges
        }
    }


# ---------------- RUN ENDPOINT ----------------
import subprocess
import tempfile
import time
import os
import psutil

@app.post("/run")
async def run_code(input_data: CodeInput):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w") as temp_file:
            temp_file.write(input_data.code)
            temp_file_path = temp_file.name

        start_time = time.time()

        process = subprocess.Popen(
            ["python", temp_file_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        try:
            stdout, stderr = process.communicate(
                input=input_data.user_input,
                timeout=5
            )
        except subprocess.TimeoutExpired:
            process.kill()
            return {
                "stdout": "",
                "stderr": "Execution timed out.",
                "execution_time": None,
                "memory_usage_kb": None,
                "runtime_hint": "Possible infinite loop"
            }

        end_time = time.time()
        execution_time = round(end_time - start_time, 6)

        # SAFE MEMORY ESTIMATION
        try:
            import psutil
            current_process = psutil.Process()
            memory_usage = current_process.memory_info().rss // 1024
        except:
            memory_usage = 0

        os.remove(temp_file_path)

        return {
            "stdout": stdout,
            "stderr": stderr,
            "execution_time": execution_time,
            "memory_usage_kb": memory_usage,
            "runtime_hint": (
                "Very Fast" if execution_time < 0.05
                else "Fast" if execution_time < 0.2
                else "Moderate" if execution_time < 1
                else "Slow"
            )
        }

    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "execution_time": None,
            "memory_usage_kb": None,
            "runtime_hint": "Error"
        }


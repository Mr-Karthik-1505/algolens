import os
import subprocess
import tempfile
import time
import psutil

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Python analyzers
from analyzer.ast_parser import ASTParser
from analyzer.loop_analyzer import LoopAnalyzer
from analyzer.recursion_detector import RecursionDetector
from analyzer.complexity_engine import ComplexityEngine
from analyzer.optimizer import Optimizer
from analyzer.cfg_generator import CFGGenerator
from analyzer.cyclomatic import CyclomaticComplexity
from analyzer.pattern_detector import PatternDetector
from analyzer.quality_score import QualityScorer

# Other language analyzers
from analyzer.c_analyzer import analyze_c
from analyzer.cpp_analyzer import analyze_cpp
from analyzer.java_analyzer import analyze_java


# ============================================================
# FastAPI Setup
# ============================================================

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
    return {"message": "AlgoLens Server Running 🚀"}


# ============================================================
# PYTHON ANALYSIS LOGIC
# ============================================================

def analyze_python_logic(code: str):

    parser = ASTParser(code)
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
    cfg_generator = CFGGenerator(code)
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


# ============================================================
# ANALYZE ENDPOINT
# ============================================================

@app.post("/analyze")
async def analyze_code(input_data: CodeInput):

    language = input_data.language.lower()

    if language == "python":
        return analyze_python_logic(input_data.code)

    elif language == "c":
        return analyze_c(input_data.code)

    elif language == "cpp":
        return analyze_cpp(input_data.code)

    elif language == "java":
        return analyze_java(input_data.code)

    else:
        return {"error": "Unsupported language"}


# ============================================================
# RUN ENDPOINT (Multi-Language Execution)
# ============================================================

@app.post("/run")
async def run_code(input_data: CodeInput):

    language = input_data.language.lower()
    code = input_data.code
    user_input = input_data.user_input

    try:
        with tempfile.TemporaryDirectory() as temp_dir:

            # ====================================================
            # PYTHON
            # ====================================================
            if language == "python":

                file_path = os.path.join(temp_dir, "main.py")

                with open(file_path, "w") as f:
                    f.write(code)

                command = ["python", file_path]

            # ====================================================
            # C
            # ====================================================
            elif language == "c":

                file_path = os.path.join(temp_dir, "main.c")
                exe_path = os.path.join(temp_dir, "main")

                with open(file_path, "w") as f:
                    f.write(code)

                compile_process = subprocess.run(
                    ["gcc", file_path, "-o", exe_path],
                    capture_output=True,
                    text=True
                )

                if compile_process.returncode != 0:
                    return {"stderr": compile_process.stderr}

                command = [exe_path]

            # ====================================================
            # C++
            # ====================================================
            elif language == "cpp":

                file_path = os.path.join(temp_dir, "main.cpp")
                exe_path = os.path.join(temp_dir, "main")

                with open(file_path, "w") as f:
                    f.write(code)

                compile_process = subprocess.run(
                    ["g++", file_path, "-o", exe_path],
                    capture_output=True,
                    text=True
                )

                if compile_process.returncode != 0:
                    return {"stderr": compile_process.stderr}

                command = [exe_path]

            # ====================================================
            # JAVA
            # ====================================================
            elif language == "java":

                file_path = os.path.join(temp_dir, "Main.java")

                with open(file_path, "w") as f:
                    f.write(code)

                compile_process = subprocess.run(
                    ["javac", file_path],
                    capture_output=True,
                    text=True,
                    cwd=temp_dir
                )

                if compile_process.returncode != 0:
                    return {"stderr": compile_process.stderr}

                command = ["java", "Main"]

            else:
                return {"stderr": "Unsupported language"}

            # ====================================================
            # EXECUTION
            # ====================================================

            start_time = time.time()

            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=temp_dir
            )

            try:
                stdout, stderr = process.communicate(
                    input=user_input,
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

            # Safe memory usage
            try:
                memory_usage = psutil.Process(process.pid).memory_info().rss // 1024
            except:
                memory_usage = 0

            runtime_hint = (
                "Very Fast" if execution_time < 0.05 else
                "Fast" if execution_time < 0.2 else
                "Moderate" if execution_time < 1 else
                "Slow"
            )

            return {
                "stdout": stdout,
                "stderr": stderr,
                "execution_time": execution_time,
                "memory_usage_kb": memory_usage,
                "runtime_hint": runtime_hint
            }

    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "execution_time": None,
            "memory_usage_kb": None,
            "runtime_hint": "Error"
        }

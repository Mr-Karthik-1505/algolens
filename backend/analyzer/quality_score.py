class QualityScorer:

    def score(self, cyclomatic_complexity, loop_depth, recursive_functions, issues):
        score = 100

        # Penalize high cyclomatic complexity
        score -= cyclomatic_complexity * 2

        # Penalize deep nesting
        score -= loop_depth * 5

        # Penalize recursion
        score -= len(recursive_functions) * 5

        # Penalize detected issues
        score -= len(issues) * 5

        return max(score, 0)

class ComplexityEngine:
    def estimate(self, loop_depth, recursive_functions):
        
        # If recursion exists
        if recursive_functions:
            if loop_depth > 0:
                return "O(n * recursive complexity)"
            return "O(2^n) (recursive growth detected)"

        # No recursion → loop-based estimation
        if loop_depth == 0:
            return "O(1)"
        elif loop_depth == 1:
            return "O(n)"
        elif loop_depth == 2:
            return "O(n^2)"
        else:
            return f"O(n^{loop_depth})"

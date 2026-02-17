class Optimizer:
    def suggest(self, loop_depth, recursive_functions):
        suggestions = []

        # Nested loop suggestion
        if loop_depth >= 2:
            suggestions.append(
                "Nested loops detected. Consider using HashMap, Two-Pointer technique, or reducing time complexity."
            )

        # Deep nesting warning
        if loop_depth >= 3:
            suggestions.append(
                "High loop nesting detected. Algorithm may be inefficient for large inputs."
            )

        # Recursion suggestion
        if recursive_functions:
            suggestions.append(
                "Recursive function detected. Consider memoization or dynamic programming to optimize."
            )

        # No major issues
        if not suggestions:
            suggestions.append("Code structure looks efficient based on static analysis.")

        return suggestions

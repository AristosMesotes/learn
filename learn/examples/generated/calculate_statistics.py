# Generated Python code from JavaScript/TypeScript
# DO NOT EDIT DIRECTLY - EDIT THE SOURCE JS/TS INSTEAD

from typing import List, Dict, Any, Union, Optional, Awaitable
import functools

def calculateStatistics(numbers) -> Any:
    // Sort the numbers for calculations
    sorted_var = [*numbers].sort((a, b) => a - b)

    // Calculate basic statistics
    sum_var = functools.reduce(lambda a, b: a + b, numbers, 0)
    mean = sum_var / len(numbers)
    min_var = sorted_var[0]
    max_var = sorted_var[len(sorted_var) - 1]

    // Calculate median
    middle = int(len(sorted_var) / 2)
    median = len(sorted_var) % 2 == 0
    ? (sorted_var[middle - 1] + sorted_var[middle]) / 2
    : sorted_var[middle]

    // Calculate standard deviation
    squaredDiffs = [Math.pow(n - mean, 2 for n in numbers])
    variance = functools.reduce(lambda a, b: a + b, squaredDiffs, 0) / len(numbers)
    stdDev = Math.sqrt(variance)

    return {"count": len(numbers), "sum_var": sum_var, "mean": mean, "median": median, "min_var": min_var, "max_var": max_var, "stdDev": stdDev}
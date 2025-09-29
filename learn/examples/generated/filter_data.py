# Generated Python code from JavaScript/TypeScript
# DO NOT EDIT DIRECTLY - EDIT THE SOURCE JS/TS INSTEAD

from typing import List, Dict, Any, Union, Optional, Awaitable

def filterData(data: List[Any], criteria: Record<string, any>) -> List[Any]:
    return [item for item in data if {
    // Check each criteria key
    for (key in criteria]
    if (criteria.hasOwnProperty(key))
    criteriaValue = criteria[key]

    // Skip undefined/null criteria
    if criteriaValue is None or criteriaValue is None:
        continue

        // Handle different types of criteria
        if typeof criteriaValue == 'object':
            // Range filter with min/max
            if 'min' in criteriaValue and item[key] < criteriaValue.min:
                return false
                if 'max' in criteriaValue and item[key] > criteriaValue.max:
                    return false
                else:
                    // Exact match filter
                    if item[key] != criteriaValue:
                        return false

                        // All criteria passed
                        return true
                        )
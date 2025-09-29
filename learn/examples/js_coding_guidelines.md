# JavaScript/TypeScript Coding Guidelines for Python Conversion

When writing JavaScript/TypeScript code that will be automatically converted to Python for NodeAI, follow these guidelines to ensure clean conversion and avoid syntax errors.

## 1. Function Structure

### ✅ DO: Use simple, flat control flow
```javascript
function goodFunction(input) {
  // Simple, sequential statements
  const value = processInput(input);
  
  // Early returns for conditions
  if (value < 0) {
    return "Value too low";
  }
  
  if (value > 100) {
    return "Value too high";
  }
  
  return "Value is acceptable";
}
```

### ❌ DON'T: Use deeply nested if/else structures
```javascript
function badFunction(input) {
  const value = processInput(input);
  if (value >= 0) {
    if (value <= 100) {
      return "Value is acceptable";
    } else {
      return "Value too high";
    }
  } else {
    return "Value too low";
  }
}
```

## 2. Object Literals

### ✅ DO: Format objects with consistent indentation
```javascript
const planetInfo = {
  "Earth": {
    resources: ["water", "oxygen"],
    description: "Home planet"
  },
  "Mars": {
    resources: ["iron", "silicon"],
    description: "Red planet"
  }
};
```

### ❌ DON'T: Use inconsistent or complex object formatting
```javascript
const planetInfo = {"Earth": 
  {resources: ["water", "oxygen"],
description: "Home planet"}, "Mars": {
  resources: ["iron", 
  "silicon"], description: "Red planet"}
};
```

## 3. Array Methods

### ✅ DO: Use simple arrow functions
```javascript
// Simple, single-line arrow functions
const doubled = numbers.map(x => x * 2);
const positives = numbers.filter(x => x > 0);

// For complex operations, use intermediate variables
const processed = data.map(item => {
  const transformed = transform(item);
  return transformed.value;
});
```

### ❌ DON'T: Use nested arrow functions or complex chains
```javascript
const result = data
  .filter(x => x.active)
  .map(x => x.values.filter(v => v > threshold).map(v => v * 2))
  .reduce((acc, vals) => [...acc, ...vals], []);
```

## 4. Comments

### ✅ DO: Use line comments with consistent spacing
```javascript
// This is a good comment
function calculate(a, b) {
  // Calculate sum
  const sum = a + b;
  return sum;
}
```

### ❌ DON'T: Use block comments or inconsistent spacing
```javascript
/* This is a block comment that won't convert well */
function calculate(a, b) {
  //This comment has no space
  const sum = a + b;
  return sum;
}
```

## 5. Type Annotations (TypeScript)

### ✅ DO: Use simple, explicit type annotations
```typescript
function processUser(user: Record<string, any>, age: number): boolean {
  // Function body
  return user.age > age;
}

interface SimpleData {
  id: number;
  name: string;
  values: number[];
}
```

### ❌ DON'T: Use complex generic types or unions
```typescript
function processData<T extends Record<K, V>, K extends string, V>(data: T): T | null {
  // Complex function body
}
```

## 6. Class Structure

### ✅ DO: Keep classes simple with clear methods
```typescript
class Planet {
  name: string;
  radius: number;
  
  constructor(name: string, radius: number) {
    this.name = name;
    this.radius = radius;
  }
  
  getSurfaceArea() {
    return 4 * Math.PI * this.radius * this.radius;
  }
}
```

### ❌ DON'T: Use complex inheritance or nested methods
```typescript
class BasePlanet {
  protected calculateDensity() { /* ... */ }
}

class Planet extends BasePlanet {
  compute() {
    return this.calculateDensity().then(density => {
      // Complex computation
    });
  }
}
```

## 7. JavaScript Features to Avoid

- **Destructuring assignments**: `const { a, b } = obj;`
- **Spread operators** in complex expressions: `{...obj1, ...obj2, newProp: value}`
- **Optional chaining**: `user?.profile?.settings`
- **Nullish coalescing**: `value ?? defaultValue`
- **Complex template literals** with expressions: `` `Result: ${a ? b() : c()}` ``
- **Dynamic property access**: `obj[computedProp]`
- **Closures** that capture variables from outer scope

## 8. Testing Your Code

Before deploying, you can test how your JavaScript code will convert to Python:

```python
from learn.js_to_python_converter import js_to_python

# Test a JavaScript snippet
js_code = """
function calculateTotal(items) {
  return items.reduce((sum, item) => sum + item.price, 0);
}
"""

python_code = js_to_python(js_code)
print(python_code)

# Check if valid Python
try:
  import ast
  ast.parse(python_code)
  print("✅ Valid Python")
except SyntaxError as e:
  print(f"❌ Invalid Python: {e}")
```

## 9. Example Tool Pattern

```javascript
// Good pattern for a NodeAI tool
function planetAnalyzer(planetName) {
  // Get required data
  const data = this.unbox("planet_data");
  
  // Early validation
  if (!data.hasOwnProperty(planetName)) {
    return `Planet ${planetName} not found`;
  }
  
  // Process data
  const planet = data[planetName];
  const result = {
    name: planetName,
    radius: planet.radius,
    habitable: planet.temperature > -20 && planet.temperature < 50
  };
  
  // Return formatted result
  return `Planet: ${result.name}
Radius: ${result.radius} km
Habitable: ${result.habitable ? "Yes" : "No"}`;
}
```

By following these guidelines, you'll ensure your JavaScript/TypeScript code converts cleanly to Python and works properly with the NodeAI backend.

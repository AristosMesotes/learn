# NodeAI Deployer with JavaScript/TypeScript Support

This library extends the NodeAI deployer to support writing tools, boxes, and brains in JavaScript and TypeScript that automatically get converted to Python for the NodeAI backend.

## Features

- Write NodeAI tools in JavaScript or TypeScript
- Automatic conversion to Python
- Support for TypeScript type annotations
- Array method conversion (.map, .filter, .reduce, etc)
- Object literal support
- Support for common JS/TS idioms

## Getting Started

### Installation

The library is already part of the `learn` package. Ensure you have the required dependencies:

```bash
pip install -r requirements.txt
```

### Basic Usage

Import the necessary components:

```python
from learn.nodeai_js_deployer import NodeAIJSClient, js_tool, js_box, js_brain
```

#### Writing a JavaScript Tool

```python
@js_tool(["MyAgent"])
def process_data(data):
    """
    function processData(data) {
        const filtered = data.filter(x => x > 0);
        const doubled = filtered.map(x => x * 2);
        return {
            count: filtered.length,
            sum: doubled.reduce((a, b) => a + b, 0)
        };
    }
    """
    pass  # The actual implementation is in the docstring
```

#### Writing a TypeScript Tool

```python
@js_tool(["MyAgent"], language="typescript")
def analyze_user(user: Dict[str, Any], threshold: float) -> Dict[str, Any]:
    """
    function analyzeUser(user: Record<string, any>, threshold: number): Record<string, any> {
        if (user.score > threshold) {
            return {
                status: "approved",
                confidence: user.score / 100
            };
        } else {
            return {
                status: "rejected",
                reason: user.score < threshold / 2 ? "low_score" : "below_threshold"
            };
        }
    }
    """
    pass
```

#### Writing a Box

```python
@js_box(["MyAgent"])
class UserProfile:
    """
    interface UserProfile {
        id: string;
        name: string;
        email: string;
        preferences: {
            theme: string;
            notifications: boolean;
        };
        lastLogin?: string;
    }
    """
    pass
```

#### Deploying to NodeAI

```python
client = NodeAIJSClient(
    base_url="http://127.0.0.1:8080",
    account="my_account",
    world="my_world"
)

# Deploy all decorated tools, boxes, and brains
client.deploy()
```

## Examples

Check out the examples in the `examples` directory:

- `finance_agent.py`: A financial analysis agent with tools written in JS/TS

## Supported JavaScript/TypeScript Features

- Function declarations
- Arrow functions
- Classes
- Object literals
- Array methods: map, filter, reduce, forEach, find
- TypeScript type annotations
- Control structures (if/else, loops)
- Template literals
- Spread operators
- Default parameters

## Known Limitations

- Complex nested structures might require manual adjustment
- Some class methods may not convert perfectly
- The Math library is partially supported

## License

This project is licensed under the MIT License - see the LICENSE file for details.

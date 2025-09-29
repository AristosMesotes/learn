# Git Workflow with JS/TS to Python Converter

This guide demonstrates how to use git effectively with the JavaScript/TypeScript to Python converter library.

## Setting Up a Git Repository

```bash
# Initialize a new git repository
git init

# Create a .gitignore file to exclude unnecessary files
cat > .gitignore << EOL
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg
.env
.venv
venv/
ENV/
.idea/
.vscode/
EOL

# Add initial files
git add .
git commit -m "Initial commit"
```

## Development Workflow

When working with the JS/TS to Python converter, here are the recommended git workflows:

### 1. Working with Source JS/TS Code

Store your JavaScript/TypeScript code in docstrings or separate files:

```python
# In your Python file (my_tools.py)
@js_tool(["MyAgent"])
def calculate_metrics(data):
    """
    function calculateMetrics(data) {
        // JavaScript implementation here
    }
    """
    pass
```

Add and commit these files:

```bash
git add my_tools.py
git commit -m "Add calculateMetrics tool in JavaScript"
```

### 2. Tracking Changes to Generated Python Code

If you want to track the generated Python code:

```bash
# Create a 'generated' directory for converted code
mkdir -p generated

# Generate the Python code
python -c "from learn.js_to_python_converter import js_to_python; print(js_to_python('''
function calculateMetrics(data) {
    // Your JS code here
}
'''))" > generated/calculate_metrics.py

# Add and commit
git add generated/calculate_metrics.py
git commit -m "Add generated Python for calculateMetrics"
```

### 3. Branching Strategy

Use feature branches for new tools:

```bash
# Create a branch for a new feature
git checkout -b feature/new-js-tool

# Make changes and commit
# ...

# Merge back to main when ready
git checkout main
git merge feature/new-js-tool
```

## Best Practices

1. **Separate Source from Generated Code**: Keep JS/TS source code in a separate directory from generated Python code.

2. **Consider Using Git Hooks**: Set up pre-commit hooks to automatically generate Python code:

   ```bash
   # Create a pre-commit hook
   cat > .git/hooks/pre-commit << EOL
   #!/bin/bash
   
   # Convert JS/TS files to Python
   python -m learn.tools.generate_python
   
   # Add generated files to the commit
   git add generated/
   EOL
   
   chmod +x .git/hooks/pre-commit
   ```

3. **Semantic Versioning**: Follow semantic versioning for your tools:

   ```bash
   # Tag a release
   git tag -a v1.0.0 -m "Initial release of JS tools"
   git push origin v1.0.0
   ```

4. **Document Tool Changes**: Include clear commit messages:

   ```bash
   git commit -m "Update calculateMetrics to support nested data structures
   
   - Added support for array of objects
   - Fixed edge case with null values
   - Improved performance of calculation loop"
   ```

## Example Git Command Sequence

Here's a complete example of a typical workflow:

```bash
# Clone repo (if not already done)
git clone https://github.com/user/nodeai-js-tools.git
cd nodeai-js-tools

# Create new branch for a feature
git checkout -b feature/stock-analyzer

# Create the JS tool in a Python file
echo '@js_tool(["FinancialAnalyst"])
def analyze_stock(data):
    """
    function analyzeStock(data) {
        const returns = data.map((d, i, arr) => 
            i > 0 ? (d.close - arr[i-1].close) / arr[i-1].close : 0
        );
        
        return {
            volatility: calculateVolatility(returns),
            trend: detectTrend(returns)
        };
    }
    """
    pass' > stock_analyzer.py

# Add and commit
git add stock_analyzer.py
git commit -m "Add stock analyzer tool in JavaScript"

# Generate Python code (optional)
mkdir -p generated
python -c "from learn.js_to_python_converter import js_to_python; \
    with open('stock_analyzer.py', 'r') as f: \
        js_code = f.read().split('\"\"\"')[1]; \
    print(js_to_python(js_code))" > generated/stock_analyzer.py

# Commit generated code
git add generated/stock_analyzer.py
git commit -m "Add generated Python for stock analyzer"

# Merge to main
git checkout main
git merge feature/stock-analyzer

# Tag a release
git tag -a v1.1.0 -m "Add stock analyzer tool"
```

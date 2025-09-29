#!/usr/bin/env python3
"""
Complete Git Workflow Example for JS/TS to Python Converter

This script demonstrates a complete workflow:
1. Creating JavaScript/TypeScript tools
2. Tracking changes with git
3. Showing common git operations with the converter
4. Demonstrating versioning practices
"""

import os
import subprocess
import tempfile
from pathlib import Path
import shutil
import sys
import time
from textwrap import dedent

# Add the parent directory to sys.path
parent_dir = Path(__file__).resolve().parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.append(str(parent_dir))

# Create a temp directory for the git demo
DEMO_DIR = Path(tempfile.mkdtemp())
REPO_DIR = DEMO_DIR / "js-to-py-demo"
REPO_DIR.mkdir(exist_ok=True)

# Function to run git commands and print the output
def run_cmd(cmd, cwd=None, print_output=True):
    """Run a command and optionally print output."""
    if isinstance(cmd, str):
        cmd = cmd.split()
    
    if not cwd:
        cwd = REPO_DIR
    
    print(f"\n> {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if print_output and result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"Error: {result.stderr}")
        return result
    except Exception as e:
        print(f"Command failed: {e}")
        return None

# Function to create a file in the repository
def create_file(filename, content):
    """Create a file in the demo repository."""
    filepath = REPO_DIR / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"Created file: {filename}")

def main():
    """Run the complete git workflow demo."""
    print("🚀 Complete Git Workflow for JS/TS to Python Converter")
    print("=" * 60)
    print(f"Demo directory: {REPO_DIR}")
    
    # Step 1: Initialize Git Repository
    print("\n\n📂 Step 1: Initialize Git Repository")
    print("-" * 40)
    run_cmd("git init")
    
    # Step 2: Create initial project files
    print("\n\n📄 Step 2: Create Initial Project Files")
    print("-" * 40)
    
    # Create .gitignore
    gitignore_content = dedent("""
    # Python
    __pycache__/
    *.py[cod]
    *$py.class
    *.so
    .Python
    venv/
    ENV/
    
    # Editor files
    .vscode/
    .idea/
    """).strip()
    
    create_file(".gitignore", gitignore_content)
    
    # Create README
    readme_content = dedent("""
    # JS/TS to Python Tools
    
    This project contains tools written in JavaScript/TypeScript that are 
    automatically converted to Python.
    """).strip()
    
    create_file("README.md", readme_content)
    
    # Create a simple tool file
    simple_tool = dedent("""
    # data_analyzer.py
    from learn.nodeai_js_deployer import js_tool
    
    @js_tool(["DataAnalyzer"])
    def analyze_numbers(numbers):
        \"\"\"
        function analyzeNumbers(numbers) {
            const sum = numbers.reduce((a, b) => a + b, 0);
            const average = sum / numbers.length;
            return {
                sum: sum,
                average: average,
                count: numbers.length
            };
        }
        \"\"\"
        pass
    """).strip()
    
    create_file("tools/data_analyzer.py", simple_tool)
    
    # Create a directory structure file
    create_file("tools/__init__.py", "# Tools package")
    
    # Add files to git
    run_cmd("git add .")
    run_cmd("git status")
    
    # First commit
    print("\n\n💾 Step 3: Make Initial Commit")
    print("-" * 40)
    run_cmd(["git", "commit", "-m", "Initial project setup"])
    run_cmd("git log --oneline --max-count=1")
    
    # Step 4: Create a feature branch
    print("\n\n🌿 Step 4: Create Feature Branch")
    print("-" * 40)
    run_cmd("git checkout -b feature/advanced-metrics")
    
    # Add new tool file
    advanced_tool = dedent("""
    # advanced_metrics.py
    from learn.nodeai_js_deployer import js_tool
    
    @js_tool(["DataAnalyzer"], language="typescript")
    def calculate_statistics(data: list) -> dict:
        \"\"\"
        function calculateStatistics(data: number[]): Record<string, number> {
            // Sort data for calculations
            const sorted = [...data].sort((a, b) => a - b);
            
            // Basic statistics
            const sum = data.reduce((a, b) => a + b, 0);
            const mean = sum / data.length;
            
            // Variance and standard deviation
            const variance = data.reduce((acc, val) => 
                acc + Math.pow(val - mean, 2), 0) / data.length;
            const stdDev = Math.sqrt(variance);
            
            return {
                mean: mean,
                median: sorted[Math.floor(data.length / 2)],
                stdDev: stdDev,
                min: Math.min(...data),
                max: Math.max(...data)
            };
        }
        \"\"\"
        pass
    """).strip()
    
    create_file("tools/advanced_metrics.py", advanced_tool)
    
    # Generate Python version (simulating conversion)
    generated_py = dedent("""
    # Generated from TypeScript
    # DO NOT EDIT DIRECTLY
    
    from typing import Dict, List, Any
    
    def calculateStatistics(data: List[float]) -> Dict[str, float]:
        # Sort data for calculations
        sorted_data = sorted(data)
        
        # Basic statistics
        sum_val = sum(data)
        mean = sum_val / len(data)
        
        # Variance and standard deviation
        variance = sum((val - mean) ** 2 for val in data) / len(data)
        std_dev = variance ** 0.5
        
        return {
            "mean": mean,
            "median": sorted_data[len(data) // 2],
            "stdDev": std_dev,
            "min": min(data),
            "max": max(data)
        }
    """).strip()
    
    create_file("generated/advanced_metrics.py", generated_py)
    
    # Add and commit
    run_cmd("git add .")
    run_cmd("git status")
    run_cmd(["git", "commit", "-m", "Add advanced metrics with TypeScript"])
    run_cmd("git log --oneline --max-count=2")
    
    # Step 5: Update existing file
    print("\n\n✏️ Step 5: Update Existing File")
    print("-" * 40)
    
    # Update the simple tool
    updated_tool = dedent("""
    # data_analyzer.py
    from learn.nodeai_js_deployer import js_tool
    
    @js_tool(["DataAnalyzer"])
    def analyze_numbers(numbers):
        \"\"\"
        function analyzeNumbers(numbers) {
            const sum = numbers.reduce((a, b) => a + b, 0);
            const average = sum / numbers.length;
            
            // New code to calculate mode
            const counts = {};
            let mode = null;
            let maxCount = 0;
            
            numbers.forEach(num => {
                counts[num] = (counts[num] || 0) + 1;
                if (counts[num] > maxCount) {
                    maxCount = counts[num];
                    mode = num;
                }
            });
            
            return {
                sum: sum,
                average: average,
                count: numbers.length,
                mode: maxCount > 1 ? mode : null
            };
        }
        \"\"\"
        pass
    """).strip()
    
    create_file("tools/data_analyzer.py", updated_tool)
    
    # Update generated file
    updated_generated = dedent("""
    # Generated from JavaScript
    # DO NOT EDIT DIRECTLY
    
    def analyze_numbers(numbers):
        sum_val = sum(numbers)
        average = sum_val / len(numbers)
        
        # Calculate mode
        counts = {}
        mode = None
        max_count = 0
        
        for num in numbers:
            counts[num] = counts.get(num, 0) + 1
            if counts[num] > max_count:
                max_count = counts[num]
                mode = num
        
        return {
            "sum": sum_val,
            "average": average,
            "count": len(numbers),
            "mode": mode if max_count > 1 else None
        }
    """).strip()
    
    create_file("generated/data_analyzer.py", updated_generated)
    
    # Commit changes
    run_cmd("git add .")
    run_cmd("git status")
    run_cmd(["git", "commit", "-m", "Add mode calculation to data analyzer"])
    
    # Step 6: Merge feature branch
    print("\n\n🔄 Step 6: Merge Feature Branch")
    print("-" * 40)
    run_cmd("git checkout master || git checkout main")
    run_cmd("git merge feature/advanced-metrics")
    run_cmd("git log --oneline --max-count=3")
    
    # Step 7: Tagging a release
    print("\n\n🏷️ Step 7: Tag Release Version")
    print("-" * 40)
    run_cmd(["git", "tag", "-a", "v1.0.0", "-m", "First release with JS/TS tools"])
    run_cmd("git tag")
    
    # Final step - show complete log
    print("\n\n📜 Complete Git History")
    print("-" * 40)
    run_cmd("git log --oneline")
    
    # Clean up
    print("\n\n🧹 Cleaning Up Demo Repository")
    print("-" * 40)
    if DEMO_DIR.exists():
        shutil.rmtree(DEMO_DIR)
        print(f"Removed temporary directory: {DEMO_DIR}")
    
    print("\n✅ Git workflow demonstration completed!")
    print("This example showed how to:")
    print("  1. Initialize a git repository")
    print("  2. Create and track JS/TS tools")
    print("  3. Generate and track Python versions")
    print("  4. Use feature branches for development")
    print("  5. Merge changes and tag releases")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
        # Clean up
        if DEMO_DIR.exists():
            shutil.rmtree(DEMO_DIR)
            print(f"Removed temporary directory: {DEMO_DIR}")
        sys.exit(1)

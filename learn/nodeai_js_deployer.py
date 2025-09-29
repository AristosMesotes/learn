# nodeai_js_deployer.py
"""
Extended NodeAI Deployer with JavaScript/TypeScript Support

This module extends the base nodeai_deployer to support JavaScript/TypeScript
code that gets automatically converted to Python for backend execution.
"""

import requests
import json
import inspect
import textwrap
from typing import List, Dict, Any, Callable, Optional, Union, TypeVar
from pathlib import Path
import os
from uuid import uuid4

# Import the base deployer and converter
from learn.nodeai_deployer import NodeAIClient, _RemoteMindProxy
from learn.js_to_python_converter import js_to_python
from learn.thought import IThought, TextThought

# Type variable for decorator preservation
F = TypeVar('F', bound=Callable[..., Any])

# --- Global Registries ---
_JS_REGISTRY = {
    "tools": [],
    "boxes": [],
    "brains": []
}

# --- Language Detection ---
def detect_language(code: str) -> str:
    """Detect if code is JavaScript/TypeScript or Python."""
    js_indicators = [
        'const ', 'let ', 'var ', '=>', 'function ', 
        '===', '!==', '&&', '||', 'console.', 
        '})', ');', '}`', 'async function', 'class.*{',
        'export ', 'import.*from', 'require(',
        ': string', ': number', ': boolean', ': any'  # TypeScript types
    ]
    
    python_indicators = [
        'def ', 'class.*:', 'import ', 'from.*import',
        '    ', 'if.*:', 'for.*:', 'while.*:',
        'print(', 'self.', '__init__', 'return ',
        '==', '!=', 'and ', 'or ', 'not ', 'is ',
        ': str', ': int', ': float', ': bool'  # Python type hints
    ]
    
    # Count indicators
    js_count = sum(1 for indicator in js_indicators if indicator in code)
    py_count = sum(1 for indicator in python_indicators if indicator in code)
    
    # If it has TypeScript type annotations, it's definitely TS
    if any(ts_type in code for ts_type in [': string', ': number', ': boolean', ': any', '<T>', 'interface ', 'type ']):
        return 'typescript'
    
    # Otherwise use indicator counts
    return 'javascript' if js_count > py_count else 'python'

# --- Enhanced Decorators ---
def js_tool(mind_types: List[str], language: Optional[str] = None):
    """
    Decorator to register a function as a tool, with automatic JS/TS to Python conversion.
    
    Args:
        mind_types: List of agent types this tool applies to
        language: Optional language hint ('javascript', 'typescript', or 'python')
                 If not provided, will auto-detect
    """
    def decorator(func: F) -> F:
        # Store the original source
        original_source = inspect.getsource(func)
        
        # Detect or use provided language
        lang = language or detect_language(original_source)
        
        # Store metadata
        _JS_REGISTRY["tools"].append({
            "mind_types": mind_types,
            "func": func,
            "language": lang,
            "original_source": original_source
        })
        
        return func
    return decorator

def js_box(mind_types: List[str], language: Optional[str] = None):
    """
    Decorator to register a class as a box, with automatic JS/TS to Python conversion.
    
    Args:
        mind_types: List of agent types this box applies to
        language: Optional language hint ('javascript', 'typescript', or 'python')
                 If not provided, will auto-detect
    """
    def decorator(cls: type) -> type:
        # Store the original source
        original_source = inspect.getsource(cls)
        
        # Detect or use provided language
        lang = language or detect_language(original_source)
        
        # Store metadata
        _JS_REGISTRY["boxes"].append({
            "mind_types": mind_types,
            "cls": cls,
            "language": lang,
            "original_source": original_source
        })
        
        return cls
    return decorator

def js_brain(mind_types: List[str]):
    """Decorator to register a brain configuration function."""
    def decorator(func: F) -> F:
        _JS_REGISTRY["brains"].append({"mind_types": mind_types, "func": func})
        return func
    return decorator

# --- Extended Client ---
class NodeAIJSClient(NodeAIClient):
    """Extended NodeAI client with JavaScript/TypeScript support."""
    
    def __init__(self, base_url: str, account: str, world: str):
        super().__init__(base_url, account, world)
        self.converter = js_to_python
    
    def _get_source_code(self, item: Dict[str, Any]) -> str:
        """
        Get source code for an item, converting from JS/TS if necessary.
        """
        if item.get("language") in ["javascript", "typescript"]:
            # Get the original JS/TS source
            original = item.get("original_source", "")
            
            # Convert to Python
            try:
                converted = self.converter(original)
                print(f"🔄 Converted {item['language']} to Python")
                return converted
            except Exception as e:
                print(f"⚠️  Failed to convert {item['language']}: {e}")
                print("    Using original source as fallback")
                return super()._get_source_code(item.get("func") or item.get("cls"))
        else:
            # Python code - use the parent method
            return super()._get_source_code(item.get("func") or item.get("cls"))
    
    def _build_box_code(self, item: Dict[str, Any], mind_types: List[str]) -> str:
        """Build the complete box code string with @box decorator."""
        source = self._get_source_code(item)
        mind_types_str = str(mind_types).replace("'", '"')
        return f"@box({mind_types_str})\n{source}"
    
    def deploy(self):
        """
        Collects all decorated items, converts JS/TS to Python, and deploys them.
        """
        self.configure_storage()

        # Group all registered items by their mind_type (agent_key)
        configs_by_agent: Dict[str, Dict[str, Any]] = {}

        for item_type, items in _JS_REGISTRY.items():
            for item in items:
                mind_types = item.get("mind_types", [])
                for agent_key in mind_types:
                    if agent_key not in configs_by_agent:
                        configs_by_agent[agent_key] = {
                            "tools_payload": {"tools": [], "boxes": {}, "boxes_code": []},
                            "brain_payload": {}
                        }
                    
                    if item_type == "tools":
                        code = self._get_source_code(item)
                        configs_by_agent[agent_key]["tools_payload"]["tools"].append({"code": code})
                    
                    elif item_type == "boxes":
                        # Build the complete box code with decorator
                        box_code = self._build_box_code(item, [agent_key])
                        configs_by_agent[agent_key]["tools_payload"]["boxes_code"].append(box_code)

                    elif item_type == "brains":
                        # We execute the brain function to get the BrainConfig object, then serialize it
                        brain_config = item["func"]()
                        # Handle both dict and object returns
                        if hasattr(brain_config, 'dict'):
                            configs_by_agent[agent_key]["brain_payload"] = brain_config.dict()
                        else:
                            configs_by_agent[agent_key]["brain_payload"] = brain_config
        
        # Deploy each agent's configuration
        for agent_key, payloads in configs_by_agent.items():
            print(f"\n📦 Deploying agent type: {agent_key}...")

            # Save main.json for tools and boxes
            if payloads["tools_payload"]["tools"] or payloads["tools_payload"]["boxes_code"]:
                print(f"  📝 Saving Tools/main.json...")
                self._save_json(agent_key, "Tools/main.json", payloads["tools_payload"])
                print(f"  ✅ Tools & Boxes for '{agent_key}' deployed.")
            
            # Save main.json for brain
            if payloads["brain_payload"]:
                print(f"  🧠 Saving Brain/main.json...")
                self._save_json(agent_key, "Brain/main.json", payloads["brain_payload"])
                print(f"  ✅ Brain for '{agent_key}' deployed.")

        print("\n🚀 Deployment complete!")
        print(f"   Deployed {len(configs_by_agent)} agent type(s) to {self.base_url}")
        print(f"   Converted {self._count_converted()} JS/TS items to Python")
    
    def _count_converted(self) -> int:
        """Count how many JS/TS items were converted."""
        count = 0
        for items in _JS_REGISTRY.values():
            for item in items:
                if item.get("language") in ["javascript", "typescript"]:
                    count += 1
        return count
    
    def clear_registry(self):
        """Clear all registered items from the global registry."""
        global _JS_REGISTRY
        _JS_REGISTRY = {
            "tools": [],
            "boxes": [],
            "brains": []
        }
        print("🧹 Registry cleared.")

# --- Utility function to write JS/TS code as Python ---
def js_code(code: str, language: str = "javascript") -> Callable:
    """
    Utility to convert JS/TS code string to a Python function.
    
    Args:
        code: JavaScript or TypeScript code as a string
        language: 'javascript' or 'typescript'
    
    Returns:
        A callable that can be decorated with @js_tool
    """
    # Convert the code
    python_code = js_to_python(code)
    
    # Create a namespace for execution
    namespace = {
        'functools': __import__('functools'),
        'max': max,
        'min': min,
        'len': len,
        'int': int,
        'float': float,
        'str': str,
        'list': list,
        'dict': dict,
        'range': range,
        'sum': sum,
        'abs': abs,
        'round': round,
        'next': next,
    }
    
    # Execute the converted code
    exec(python_code, namespace)
    
    # Find the main function (assumes single function)
    for name, obj in namespace.items():
        if callable(obj) and not name.startswith('_') and name not in ['functools', 'max', 'min', 'len', 'int', 'float', 'str', 'list', 'dict', 'range', 'sum', 'abs', 'round', 'next']:
            # Create a wrapper that stores the metadata
            def wrapper(*args, **kwargs):
                return obj(*args, **kwargs)
            wrapper.__name__ = obj.__name__
            wrapper._js_source = code
            wrapper._js_language = language
            return wrapper
    
    raise ValueError("No function found in converted code")

# Export convenience function
tool = js_tool
box = js_box  
brain = js_brain

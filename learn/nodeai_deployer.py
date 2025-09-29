# nodeai_deployer.py
import requests
import json
import inspect
import textwrap
from typing import List, Dict, Any, Callable, Optional, Union
from pathlib import Path
import os
from uuid import uuid4

# Import necessary thought classes

from learn.thought import IThought, TextThought


# --- Global Registries ---
# These will store the functions and classes decorated by the user.
_REGISTRY = {
    "tools": [],
    "boxes": [],
    "brains": []
}

# --- Decorators ---
# These decorators capture the decorated items without modifying them.

def tool(mind_types: List[str]):
    """Decorator to register a function as a tool for specific mind types."""
    def decorator(func: Callable):
        _REGISTRY["tools"].append({"mind_types": mind_types, "func": func})
        return func
    return decorator

def box(mind_types: List[str]):
    """Decorator to register a Pydantic class as a box for specific mind types."""
    def decorator(cls: type):
        _REGISTRY["boxes"].append({"mind_types": mind_types, "cls": cls})
        return cls
    return decorator

def brain(mind_types: List[str]):
    """Decorator to register a brain configuration function for specific mind types."""
    def decorator(func: Callable):
        _REGISTRY["brains"].append({"mind_types": mind_types, "func": func})
        return func
    return decorator

# --- API Client ---
class NodeAIClient:
    """A client to interact with the NodeAI remote server."""
    
    def __init__(self, base_url: str, account: str, world: str):
        """
        Initialize the NodeAI deployment client.
        
        Args:
            base_url: The base URL of your NodeAI server (e.g., "http://127.0.0.1:8080")
            account: Your account for authentication
            account: The account/namespace for storage (e.g., "MyAccount")
            world: The world this agent belongs to (e.g., "MyWorld")
        """
        self.base_url = base_url.rstrip('/')
        self.account = account
        self.world = world
        self.headers = {"Content-Type": "application/json", "x-auth-user": self.account}

    def configure_storage(self):
        """Sets up the storage configuration for the user on the server."""
        url = f"{self.base_url}/api/storage/config"
        payload = {"storageBackend": "local", "account": self.account}
        print("🔧 Configuring remote storage...")
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        print("✅ Storage configured successfully.")
        return response.json()

    def _save_json(self, agent_key: str, file_name: str, content: Dict[str, Any]):
        """Saves a JSON file to the agent's collective storage."""
        url = f"{self.base_url}/api/storage/agent/{self.account}/{self.world}/{agent_key}/_collective/set"
        
        # Convert content to JSON string before sending - MATCHING FRONTEND BEHAVIOR
        payload = {
            "file_path": file_name, 
            "content": json.dumps(content)  # <-- This is the fix: content must be a string
        }
        
        # Use json=payload for cleaner code
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _get_source_code(obj: Any) -> str:
        """Extracts the clean, dedented source code from a function or class."""
        try:
            source = inspect.getsource(obj)
            # Remove the decorator line if it exists
            lines = source.split('\n')
            # Find the first line that starts with 'def' or 'class'
            start_idx = 0
            for i, line in enumerate(lines):
                if line.strip().startswith(('def ', 'class ')):
                    start_idx = i
                    break
            # Rejoin from the definition line onwards
            source = '\n'.join(lines[start_idx:])
            return textwrap.dedent(source).strip()
        except (TypeError, OSError):
            raise ValueError(f"Could not get source code for {obj}. Is it defined in an interactive session?")

    def _build_box_code(self, cls: type, mind_types: List[str]) -> str:
        """Build the complete box code string with @box decorator."""
        source = self._get_source_code(cls)
        mind_types_str = str(mind_types).replace("'", '"')
        return f"@box({mind_types_str})\n{source}"

    def deploy(self):
        """
        Collects all decorated items, builds the main.json files, and deploys them.
        """
        self.configure_storage()

        # Group all registered items by their mind_type (agent_key)
        configs_by_agent: Dict[str, Dict[str, Any]] = {}

        for item_type, items in _REGISTRY.items():
            for item in items:
                mind_types = item.get("mind_types", [])
                for agent_key in mind_types:
                    if agent_key not in configs_by_agent:
                        configs_by_agent[agent_key] = {
                            "tools_payload": {"tools": [], "boxes": {}, "boxes_code": []},
                            "brain_payload": {}
                        }
                    
                    if item_type == "tools":
                        code = self._get_source_code(item["func"])
                        configs_by_agent[agent_key]["tools_payload"]["tools"].append({"code": code})
                    
                    elif item_type == "boxes":
                        # Build the complete box code with decorator
                        box_code = self._build_box_code(item["cls"], [agent_key])
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

    def clear_registry(self):
        """Clear all registered items from the global registry."""
        global _REGISTRY
        _REGISTRY = {
            "tools": [],
            "boxes": [],
            "brains": []
        }
        print("🧹 Registry cleared.")

    def think(self, mind_type: str, mind_id: str, thought: IThought, wait: str = "first") -> List[IThought]:
        """
        Sends a thought to a remote agent and waits for a response.

        Args:
            mind_type: The type of the agent (e.g., "Human").
            mind_id: The specific ID of the agent (e.g., "aristotle").
            thought: An IThought object containing the message.
            wait: How to wait for the response. 'first' (default) or 'all'.

        Returns:
            A list of IThought objects representing the response(s).
        """
        print(f"🧠 Sending thought to {mind_type}/{mind_id}...")
        url = f"{self.base_url}/nodeai/send?wait={wait}"
        
        # This payload mimics the MessageEnvelope structure the server expects
        payload = {
            "mind_type": mind_type,
            "mind_id": mind_id,
            "thought": thought.to_dict(),
            "correlation_id": str(uuid4()), # Essential for getting a reply
            "metadata": {
                "world": self.world,
                "account": self.account
            }
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        
        response_data = response.json()
        
        if "responses" not in response_data:
            raise ValueError("Invalid response from server: 'responses' key is missing.")
            
        # Deserialize the response thoughts back into IThought objects
        return [IThought.from_dict(item["thought"]) for item in response_data["responses"]]

    def get_mind(self, mind_type: str, mind_id: str) -> '_RemoteMindProxy':
        """
        Gets a proxy object to interact with a specific remote mind.
        
        Args:
            mind_type: The type of the agent.
            mind_id: The ID of the agent.

        Returns:
            A _RemoteMindProxy instance.
        """
        return _RemoteMindProxy(client=self, mind_type=mind_type, mind_id=mind_id)


# --- Remote Mind Proxy ---
class _RemoteMindProxy:
    """A proxy object that makes remote think calls feel local."""
    def __init__(self, client: NodeAIClient, mind_type: str, mind_id: str):
        self._client = client
        self.mind_type = mind_type
        self.mind_id = mind_id

    def think(self, thought: Union[str, IThought]) -> IThought:
        """
        Sends a thought to the remote mind and returns the first response.

        Args:
            thought: A string or an IThought object.

        Returns:
            The first IThought object from the server's response.
        """
        if isinstance(thought, str):
            thought = TextThought(content=thought)
            
        responses = self._client.think(self.mind_type, self.mind_id, thought)
        
        if not responses:
            return TextThought(content="<No response from server>", role="error")
        
        return responses[0]

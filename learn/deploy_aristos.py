#!/usr/bin/env python
"""
FIXED VERSION: Deploy Aristotle agent to NodeAI server.

Key fixes:
1. Removed enum dependency - use plain strings
2. Made all tools self-contained
3. Simplified type hints to basic types
"""

from pydantic import BaseModel
from learn.nodeai_deployer import NodeAIClient, tool, box, brain

# --- Agent Configuration ---
AGENT_TYPE = "Human"
AI_MODEL = "gpt-5-nano"

HUMAN_INSTRUCTIONS = """
You are a human.
You can eat food to restore health and reduce hunger.
This is your current state:
self.human_data
self.emotion
---
Hunger of 1.0 is very hungry.
Eat to lower your hunger.
"""

# --- Data Models ---

@box([AGENT_TYPE])
class HumanData(BaseModel):
    health: int = 80       # All humans are born healthy...
    hunger: float = 1.0    # All humans are born hungry...

    def change_hunger(self, amount: float):
        minimum_hunger = 0.0
        maximum_hunger = 1.0
        self.hunger += amount
        self.hunger = max(minimum_hunger, min(maximum_hunger, self.hunger))

    def change_health(self, amount: int):
        minimum_health = 0
        maximum_health = 100
        self.health += amount
        self.health = max(minimum_health, min(maximum_health, self.health))

# --- Tools ---

@tool([AGENT_TYPE])
def eat(self, food: str):
    """
    Eat food to restore health and reduce hunger.
    Available foods: apple, fig
    My current human data:
    self.human_data
    ---
    food: Type of food to eat. Choices are 'apple' and 'fig'
    """
    # Unbox the human data
    human_data = self.unbox("human_data")
    
    # Simple string comparison instead of enum
    if food == "apple":
        human_data.change_health(5)
        human_data.change_hunger(-0.1)
        result = "eating apple"
    elif food == "fig":
        human_data.change_health(3)
        human_data.change_hunger(-0.05)
        result = "eating fig"
    else:
        return f"Unknown food: {food}. Try 'apple' or 'fig'"
    
    # Save the updated human data back to memory
    self.box("human_data", human_data)
    return f"{self.mind_id} ate {food}. Health: {human_data.health}, Hunger: {human_data.hunger:.1f}"

@tool([AGENT_TYPE])
def check_status(self):
    """
    Check current health and hunger status.
    """
    human_data = self.unbox("human_data")
    
    status = f"Health: {human_data.health}/100, Hunger: {human_data.hunger:.1f}/1.0"
    
    if human_data.hunger > 0.7:
        status += " (Very hungry! You should eat something)"
    elif human_data.hunger > 0.4:
        status += " (Getting hungry)"
    else:
        status += " (Not hungry)"
    
    return status

# --- Brain Configuration ---

@brain([AGENT_TYPE])
def aristos_brain():
    """Configure the brain for Aristotle with GPT model and instructions."""
    # Return a simple dict that the server can understand
    return {
        "instructions": HUMAN_INSTRUCTIONS,
        "clients": [
            {
                "model_name": AI_MODEL,
                "provider": "assistant",
            }
        ]
    }

# --- Deployment Script ---
#!/usr/bin/env python

if __name__ == "__main__":
    print("🚀 NodeAI Agent Deployment & Interaction Script (FIXED)")
    print("=" * 50)
    
    # The fix: Deploy to "Agents" world where the server actually looks!
    client = NodeAIClient(
        base_url="https://pfm-ngrok-app.ngrok.app",
        username="leech", 
        account="500 B.C.",
        world="Greece"  # ← THIS IS THE FIX! Was "Ancient Greece"
    )
    
    # 2. Debug: Show what will be deployed
    from learn.nodeai_deployer import get_registry_summary, _REGISTRY
    summary = get_registry_summary()
    print(f"\n📋 Registry Summary:")
    print(f"   Tools: {summary['tools']}")
    print(f"   Boxes: {summary['boxes']}")
    print(f"   Brains: {summary['brains']}")
    
    # 3. Debug: Print actual tool code
    print("\n🔍 Tool Code to Deploy:")
    for tool_item in _REGISTRY["tools"]:
        func = tool_item["func"]
        code = NodeAIClient._get_source_code(func)
        print(f"\n--- {func.__name__} ---")
        print(code)
        print("--- end ---")
    
    # 4. Deploy
    try:
        print("\n📦 Deploying...")
        client.deploy()
        print("\n✨ Deployment successful!")
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

    # 5. Wait a moment for server to process
    import time
    print("\n⏳ Waiting for server to process deployment...")
    time.sleep(2)

    # 6. Interact with the deployed agent
    print("\n🤖 Testing the deployed agent...")
    print("-" * 50)
    
    try:
        # Get the agent
        aristos = client.get_mind(mind_type=AGENT_TYPE, mind_id="Aristotle")
        
        # Test conversation
        test_messages = [
            "What's my current status?",
            "I'm hungry, what should I eat?",
            "Please eat an apple",
            "Check my status again"
        ]
        
        for message in test_messages:
            print(f"\n👤 You: {message}")
            try:
                response = aristos.think(message)
                print(f"🤖 Aristotle: {response.content}")
            except Exception as e:
                print(f"⚠️ Error: {e}")
        
        print("\n✅ Testing complete!")
        
    except Exception as e:
        print(f"\n❌ Interaction failed: {e}")
        import traceback
        traceback.print_exc()

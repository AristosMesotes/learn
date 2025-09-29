#!/usr/bin/env python
"""
Simplified Space Explorer Agent Example

This is a simplified version of the Space Explorer agent with improved
JavaScript code that avoids the indentation issues when converted to Python.
"""

from learn.nodeai_js_deployer import NodeAIJSClient, js_tool, js_box, js_brain
from learn.thought import TextThought
import time

# --- Agent Configuration ---
AGENT_TYPE = "SpaceExplorer"
AI_MODEL = "gpt-4o"

EXPLORER_INSTRUCTIONS = """
You are a space explorer navigating the universe.
You can visit planets, collect resources, and manage your spacecraft.
This is your current state:
self.explorer_data
self.spacecraft
---
Fuel level is critical below 20.
Collect resources to earn credits.
Use scan to discover information about planets.
"""

# --- Data Models ---

@js_box([AGENT_TYPE])
class SpacecraftData:
    """
    interface SpacecraftData {
        name: string;
        fuelLevel: number;
        cargoCapacity: number;
        cargoUsed: number;
        credits: number;
    }
    """
    pass

@js_box([AGENT_TYPE])
class ExplorerData:
    """
    interface ExplorerData {
        name: string;
        currentPlanet: string;
        resourcesCollected: Record<string, number>;
        visitedPlanets: string[];
    }
    """
    pass

# --- Tools ---

@js_tool([AGENT_TYPE])
def travel_to_planet(planet_name):
    """
    function travelToPlanet(planetName) {
        // Get the explorer data
        const explorerData = this.unbox("explorer_data");
        const spacecraft = this.unbox("spacecraft");
        
        // Planet distances (fuel cost)
        const planetDistances = {
            "Earth": 0,
            "Mars": 10,
            "Venus": 8,
            "Jupiter": 25,
            "Saturn": 35
        };
        
        // Check if planet exists
        if (!planetDistances.hasOwnProperty(planetName)) {
            return `Planet ${planetName} is not in our navigation system.`;
        }
        
        // Check if already on this planet
        if (explorerData.currentPlanet === planetName) {
            return `You are already on ${planetName}.`;
        }
        
        // Calculate fuel cost (distance from current to target)
        const currentDistance = planetDistances[explorerData.currentPlanet] || 0;
        const targetDistance = planetDistances[planetName];
        const fuelCost = Math.abs(targetDistance - currentDistance);
        
        // Check if enough fuel
        if (spacecraft.fuelLevel < fuelCost) {
            return `Not enough fuel! Need ${fuelCost} units but only have ${spacecraft.fuelLevel}.`;
        }
        
        // Travel to the planet
        spacecraft.fuelLevel -= fuelCost;
        explorerData.currentPlanet = planetName;
        
        // Add to visited planets if it's new
        if (!explorerData.visitedPlanets.includes(planetName)) {
            explorerData.visitedPlanets.push(planetName);
        }
        
        // Save updated data
        this.box("explorer_data", explorerData);
        this.box("spacecraft", spacecraft);
        
        return `Successfully traveled to ${planetName}. Fuel remaining: ${spacecraft.fuelLevel}.`;
    }
    """
    pass

@js_tool([AGENT_TYPE])
def check_status():
    """
    function checkStatus() {
        // Get data
        const explorerData = this.unbox("explorer_data");
        const spacecraft = this.unbox("spacecraft");
        
        // Format resources collected
        let resourcesList = "None";
        if (Object.keys(explorerData.resourcesCollected).length > 0) {
            resourcesList = Object.entries(explorerData.resourcesCollected)
                .map(([name, amount]) => `${name}: ${amount}`)
                .join(", ");
        }
        
        // Format visited planets
        const visitedCount = explorerData.visitedPlanets.length;
        
        return `EXPLORER STATUS REPORT
====================
Name: ${explorerData.name}
Current Location: ${explorerData.currentPlanet}
Planets Visited: ${visitedCount} (${explorerData.visitedPlanets.join(", ")})

SPACECRAFT STATUS
====================
Name: ${spacecraft.name}
Fuel Level: ${spacecraft.fuelLevel}/100 ${spacecraft.fuelLevel < 20 ? "⚠️ LOW" : ""}
Cargo: ${spacecraft.cargoUsed}/${spacecraft.cargoCapacity}
Credits: ${spacecraft.credits}

INVENTORY
====================
Resources: ${resourcesList}`;
    }
    """
    pass

# --- Brain Configuration ---

@js_brain([AGENT_TYPE])
def explorer_brain():
    """Configure the brain for the Space Explorer with GPT model and instructions."""
    return {
        "instructions": EXPLORER_INSTRUCTIONS,
        "clients": [
            {
                "model_name": AI_MODEL,
                "provider": "openai",
            }
        ]
    }

# --- Deployment Script ---
def initialize_data():
    """Create initial data for the Space Explorer."""
    explorer_data = {
        "name": "Cosmo",
        "currentPlanet": "Earth",
        "resourcesCollected": {},
        "visitedPlanets": ["Earth"]
    }
    
    spacecraft_data = {
        "name": "Voyager",
        "fuelLevel": 100,
        "cargoCapacity": 10,
        "cargoUsed": 0,
        "credits": 500
    }
    
    return explorer_data, spacecraft_data

def deploy_agent():
    """Deploy the Space Explorer agent to NodeAI server."""
    print("🚀 NodeAI Space Explorer Agent Deployment")
    print("=" * 50)
    
    client = NodeAIJSClient(
        base_url="https://pfm-ngrok-app.ngrok.app",  # Update with your server URL
        account="SpaceAgency",
        world="Universe"
    )
    
    try:
        print("\n📦 Deploying...")
        client.deploy()
        print("\n✨ Deployment successful!")
        return client
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_conversion():
    """Test the JS to Python conversion of our tools."""
    from learn.js_to_python_converter import js_to_python
    
    # Extract JavaScript code from tool
    js_code = travel_to_planet.__doc__.strip()
    
    # Convert to Python
    print("Converting JavaScript to Python:")
    python_code = js_to_python(js_code)
    print(python_code)
    
    # Check if the code is valid Python
    try:
        import ast
        ast.parse(python_code)
        print("\n✅ Successfully converted to valid Python code")
    except SyntaxError as e:
        print(f"\n❌ Conversion produced invalid Python code: {e}")

if __name__ == "__main__":
    # Option 1: Test conversion only
    test_conversion()
    
    # Option 2: Deploy and test (uncomment to use)
    # client = deploy_agent()
    # if client:
    #     print("\n⏳ Waiting for server to process deployment...")
    #     time.sleep(2)
    #     print("\n🤖 Agent deployed successfully and ready for use!")

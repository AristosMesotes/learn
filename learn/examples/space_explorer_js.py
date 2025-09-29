#!/usr/bin/env python
"""
JavaScript NodeAI Agent Example: Space Explorer

This example demonstrates how to create NodeAI agents using JavaScript/TypeScript
with our converter to automatically translate to Python.
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
        resourcesCollected: {
            [key: string]: number;
        };
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
def scan_planet():
    """
    function scanPlanet() {
        // Get the explorer data
        const explorerData = this.unbox("explorer_data");
        const spacecraft = this.unbox("spacecraft");
        
        // Planet information
        const planetInfo = {
            "Earth": {
                resources: ["water", "oxygen"],
                description: "Home planet with abundant life and water."
            },
            "Mars": {
                resources: ["iron", "silicon"],
                description: "Red planet with iron-rich soil and dust storms."
            },
            "Venus": {
                resources: ["carbon", "sulfur"],
                description: "Hot planet with thick atmosphere and volcanic activity."
            },
            "Jupiter": {
                resources: ["hydrogen", "helium"],
                description: "Gas giant with powerful storms and many moons."
            },
            "Saturn": {
                resources: ["helium", "methane"],
                description: "Ringed planet with low density and many moons."
            }
        };
        
        // Check if on a valid planet
        if (!planetInfo.hasOwnProperty(explorerData.currentPlanet)) {
            return "Unable to scan: You're not on a recognized planet.";
        }
        
        // Use 1 fuel unit to perform scan
        if (spacecraft.fuelLevel < 1) {
            return "Not enough fuel to perform scan.";
        }
        
        spacecraft.fuelLevel -= 1;
        this.box("spacecraft", spacecraft);
        
        const planet = planetInfo[explorerData.currentPlanet];
        
        return `Scan of ${explorerData.currentPlanet} complete:
Description: ${planet.description}
Available Resources: ${planet.resources.join(", ")}
Fuel remaining: ${spacecraft.fuelLevel}`;
    }
    """
    pass

@js_tool([AGENT_TYPE])
def collect_resources():
    """
    function collectResources() {
        // Get the explorer data
        const explorerData = this.unbox("explorer_data");
        const spacecraft = this.unbox("spacecraft");
        
        // Planet resources and values
        const planetResources = {
            "Earth": { "water": 5, "oxygen": 8 },
            "Mars": { "iron": 15, "silicon": 10 },
            "Venus": { "carbon": 12, "sulfur": 18 },
            "Jupiter": { "hydrogen": 20, "helium": 25 },
            "Saturn": { "helium": 25, "methane": 22 }
        };
        
        // Check if on a valid planet
        if (!planetResources.hasOwnProperty(explorerData.currentPlanet)) {
            return "Unable to collect: You're not on a recognized planet.";
        }
        
        // Use 2 fuel units to collect resources
        if (spacecraft.fuelLevel < 2) {
            return "Not enough fuel to collect resources.";
        }
        
        spacecraft.fuelLevel -= 2;
        
        // Check cargo capacity
        if (spacecraft.cargoUsed >= spacecraft.cargoCapacity) {
            return "Cargo hold is full! Cannot collect more resources.";
        }
        
        // Get available resources on current planet
        const availableResources = planetResources[explorerData.currentPlanet];
        const resourceNames = Object.keys(availableResources);
        
        // Randomly select one resource to collect
        const resourceIndex = Math.floor(Math.random() * resourceNames.length);
        const collectedResource = resourceNames[resourceIndex];
        const resourceValue = availableResources[collectedResource];
        
        // Add to collected resources
        if (!explorerData.resourcesCollected[collectedResource]) {
            explorerData.resourcesCollected[collectedResource] = 0;
        }
        explorerData.resourcesCollected[collectedResource] += 1;
        
        // Add value as credits
        spacecraft.credits += resourceValue;
        
        // Increase used cargo
        spacecraft.cargoUsed += 1;
        
        // Save updated data
        this.box("explorer_data", explorerData);
        this.box("spacecraft", spacecraft);
        
        return `Successfully collected 1 unit of ${collectedResource} worth ${resourceValue} credits!
Cargo: ${spacecraft.cargoUsed}/${spacecraft.cargoCapacity}
Credits: ${spacecraft.credits}
Fuel remaining: ${spacecraft.fuelLevel}`;
    }
    """
    pass

@js_tool([AGENT_TYPE])
def refuel():
    """
    function refuel() {
        // Get the spacecraft data
        const spacecraft = this.unbox("spacecraft");
        const explorerData = this.unbox("explorer_data");
        
        // Check if on Earth (can only refuel on Earth)
        if (explorerData.currentPlanet !== "Earth") {
            return "You can only refuel on Earth!";
        }
        
        // Cost to refuel (10 credits per fuel unit)
        const fuelNeeded = 100 - spacecraft.fuelLevel;
        const refuelCost = fuelNeeded * 10;
        
        // Check if enough credits
        if (spacecraft.credits < refuelCost) {
            return `Not enough credits to refuel! Need ${refuelCost} credits but only have ${spacecraft.credits}.`;
        }
        
        // Refuel
        spacecraft.credits -= refuelCost;
        spacecraft.fuelLevel = 100;
        
        // Save updated data
        this.box("spacecraft", spacecraft);
        
        return `Successfully refueled to 100%! Cost: ${refuelCost} credits. Remaining credits: ${spacecraft.credits}.`;
    }
    """
    pass

@js_tool([AGENT_TYPE])
def sell_resources():
    """
    function sellResources() {
        // Get the explorer and spacecraft data
        const explorerData = this.unbox("explorer_data");
        const spacecraft = this.unbox("spacecraft");
        
        // Check if on Earth (can only sell on Earth)
        if (explorerData.currentPlanet !== "Earth") {
            return "You can only sell resources on Earth!";
        }
        
        // Resource values
        const resourceValues = {
            "water": 5,
            "oxygen": 8,
            "iron": 15,
            "silicon": 10,
            "carbon": 12,
            "sulfur": 18,
            "hydrogen": 20,
            "helium": 25,
            "methane": 22
        };
        
        // Check if has resources to sell
        if (Object.keys(explorerData.resourcesCollected).length === 0) {
            return "No resources to sell!";
        }
        
        let totalValue = 0;
        let salesReport = "Resources sold:";
        
        // Sell each resource
        for (const resource in explorerData.resourcesCollected) {
            const amount = explorerData.resourcesCollected[resource];
            const value = (resourceValues[resource] || 5) * amount;
            totalValue += value;
            salesReport += `\n- ${amount} ${resource}: ${value} credits`;
            
            // Free up cargo space
            spacecraft.cargoUsed -= amount;
        }
        
        // Update credits and clear resources
        spacecraft.credits += totalValue;
        explorerData.resourcesCollected = {};
        
        // Ensure cargo doesn't go negative
        if (spacecraft.cargoUsed < 0) spacecraft.cargoUsed = 0;
        
        // Save updated data
        this.box("explorer_data", explorerData);
        this.box("spacecraft", spacecraft);
        
        return `${salesReport}\n\nTotal earned: ${totalValue} credits\nNew balance: ${spacecraft.credits} credits\nCargo space: ${spacecraft.cargoUsed}/${spacecraft.cargoCapacity}`;
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
        base_url="https://pfm-ngrok-app.ngrok.app",# Update with your server URL
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

def interact_with_agent(client):
    """Interact with the deployed Space Explorer agent."""
    try:
        # Get the agent
        explorer = client.get_mind(mind_type=AGENT_TYPE, mind_id="Cosmo")
        
        # Initialize agent data
        explorer_data, spacecraft_data = initialize_data()
        first_thought = TextThought(
            content=f"Initialize explorer with name: {explorer_data['name']}",
            metadata={
                "explorer_data": explorer_data,
                "spacecraft": spacecraft_data
            }
        )
        
        # Send initialization thought
        response = explorer.think(first_thought)
        print(f"🤖 Initialization: {response.content}\n")
        
        # Test conversation
        test_messages = [
            "What's my current status?",
            "Scan the current planet",
            "Travel to Mars",
            "Scan Mars",
            "Collect resources on Mars",
            "Travel back to Earth",
            "Sell my resources"
        ]
        
        for message in test_messages:
            print(f"\n👤 You: {message}")
            try:
                response = explorer.think(message)
                print(f"🤖 Cosmo: {response.content}")
                time.sleep(1)  # Brief pause between messages
            except Exception as e:
                print(f"⚠️ Error: {e}")
        
        print("\n✅ Testing complete!")
        
    except Exception as e:
        print(f"\n❌ Interaction failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    client = deploy_agent()
    
    if client:
        print("\n⏳ Waiting for server to process deployment...")
        time.sleep(2)
        
        print("\n🤖 Testing the deployed agent...")
        print("-" * 50)
        interact_with_agent(client)

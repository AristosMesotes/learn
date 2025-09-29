# Space Explorer JS Agent Example

This example demonstrates how to create a NodeAI agent using JavaScript/TypeScript code that gets automatically converted to Python.

## About the Agent

Space Explorer is a simulation of an interplanetary exploration agent that can:

1. Travel between planets (Earth, Mars, Venus, Jupiter, Saturn)
2. Scan planets for information and resources
3. Collect valuable resources
4. Manage spacecraft fuel and cargo
5. Sell resources for credits
6. Refuel the spacecraft

## Key Features

This example showcases several important JavaScript/TypeScript features that our converter handles:

1. **TypeScript Interfaces** - Used for defining the spacecraft and explorer data models
2. **Object Manipulation** - Managing nested properties and collections
3. **Array Methods** - Using `includes()`, `push()`, and other array operations
4. **Conditional Logic** - Complex if/else statements and property checks
5. **Math Operations** - Random number generation and calculations
6. **String Formatting** - Template literals for rich text output

## How It Works

The agent implements six key tools:

1. `travelToPlanet(planetName)` - Navigate to different planets
2. `scanPlanet()` - Get information about the current planet
3. `collectResources()` - Collect available resources
4. `refuel()` - Refill fuel (only on Earth)
5. `sellResources()` - Convert collected resources to credits (only on Earth) 
6. `checkStatus()` - Get a full status report

## Running the Example

To run the example:

```bash
python -m learn.examples.space_explorer_js
```

This will:
1. Deploy the agent to your NodeAI server
2. Initialize the explorer with starting data
3. Run through a sequence of test interactions

## Code Structure

- **Data Models** - TypeScript interfaces for the explorer and spacecraft data
- **Tools** - JavaScript functions that implement the agent's capabilities
- **Brain Configuration** - Sets up the agent's instructions and AI model
- **Deployment Code** - Python code to deploy and test the agent

## Extending the Example

You can extend this example by:

1. Adding more planets with unique resources
2. Implementing spacecraft upgrades
3. Adding exploration missions or objectives
4. Creating hazards or challenges during exploration
5. Adding NPCs or other agents to interact with

## Integration with Converter

This example uses the `js_tool`, `js_box`, and `js_brain` decorators from our `nodeai_js_deployer` module to automatically convert JavaScript/TypeScript code to Python when deployed to the NodeAI backend.

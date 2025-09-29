#!/usr/bin/env python
"""
Minimal JavaScript NodeAI Agent Example

This example demonstrates a minimal working JavaScript agent that
follows best practices for clean conversion to Python.
"""

from learn.nodeai_js_deployer import NodeAIJSClient, js_tool, js_box, js_brain
from learn.thought import TextThought

# --- Agent Configuration ---
AGENT_TYPE = "WeatherAdvisor"
AI_MODEL = "gpt-4o"

ADVISOR_INSTRUCTIONS = """
You are a weather advisor that helps users decide what to wear based on weather conditions.
You have access to these boxes:
- self.user_preferences: The user's clothing preferences
- self.weather_data: Current weather information

You can suggest appropriate clothing based on temperature, conditions, and preferences.
"""

# --- Data Models ---

@js_box([AGENT_TYPE])
class UserPreferences:
    """
    interface UserPreferences {
        name: string;
        preferredStyle: string;
        temperatureSensitivity: "cold" | "neutral" | "hot";
    }
    """
    pass

@js_box([AGENT_TYPE])
class WeatherData:
    """
    interface WeatherData {
        temperature: number;  // in Celsius
        conditions: string;   // e.g., "sunny", "rainy", "cloudy" 
        windSpeed: number;    // in km/h
        humidity: number;     // percentage
    }
    """
    pass

# --- Tools ---

@js_tool([AGENT_TYPE])
def suggest_outfit():
    """
    function suggestOutfit() {
      // Get user preferences and weather data
      const prefs = this.unbox("user_preferences");
      const weather = this.unbox("weather_data");
      
      // Check if data is available
      if (!prefs || !weather) {
        return "Missing data - please provide preferences and weather information.";
      }
      
      // Calculate feels-like temperature
      let feelsLike = weather.temperature;
      
      // Adjust for wind chill (simplified formula)
      if (weather.temperature < 10 && weather.windSpeed > 5) {
        feelsLike = feelsLike - (weather.windSpeed * 0.1);
      }
      
      // Adjust for humidity (simplified)
      if (weather.temperature > 20 && weather.humidity > 70) {
        feelsLike = feelsLike + 3;
      }
      
      // Adjust for user's temperature sensitivity
      if (prefs.temperatureSensitivity === "cold") {
        feelsLike = feelsLike - 3;
      } else if (prefs.temperatureSensitivity === "hot") {
        feelsLike = feelsLike + 3;
      }
      
      // Determine base clothing type
      let clothing = "";
      
      if (feelsLike < 5) {
        clothing = "Heavy winter coat, scarf, hat, and gloves";
      } else if (feelsLike < 15) {
        clothing = "Light jacket or sweater";
      } else if (feelsLike < 25) {
        clothing = "Long sleeves or light sweater";
      } else {
        clothing = "T-shirt and shorts";
      }
      
      // Add condition-specific items
      let extras = [];
      
      if (weather.conditions === "rainy") {
        extras.push("umbrella");
        extras.push("waterproof shoes");
      }
      
      if (weather.conditions === "sunny" && feelsLike > 20) {
        extras.push("sunglasses");
        extras.push("hat");
        extras.push("sunscreen");
      }
      
      // Format the response
      let response = "Weather Outfit Suggestion for " + prefs.name + 
        "\n=========================================\n" +
        "Current conditions: " + weather.temperature + "°C, " + weather.conditions + "\n" +
        "Feels like: " + feelsLike.toFixed(1) + "°C\n\n" +
        "Recommended outfit:\n" +
        "- " + clothing + "\n";

      // Add extras if any
      if (extras.length > 0) {
        response += "\nDon't forget:\n";
        for (let i = 0; i < extras.length; i++) {
          response += "- " + extras[i] + "\n";
        }
      }
      
      // Add style note based on preference
      response += "\nStyle note: For your \"" + prefs.preferredStyle + "\" style preference, ";
      
      if (prefs.preferredStyle === "casual") {
        response += "consider comfortable sneakers and relaxed fit clothing.";
      } else if (prefs.preferredStyle === "formal") {
        response += "a structured jacket can elevate your look while staying weather-appropriate.";
      } else if (prefs.preferredStyle === "athletic") {
        response += "moisture-wicking fabrics will help keep you comfortable.";
      } else {
        response += "adapt the suggestions to match your personal taste.";
      }
      
      return response;
    }
    """
    pass

@js_tool([AGENT_TYPE])
def check_extreme_weather():
    """
    function checkExtremeWeather() {
      // Get weather data
      const weather = this.unbox("weather_data");
      
      // Check if data is available
      if (!weather) {
        return "No weather data available";
      }
      
      // Define extreme weather thresholds
      const extremes = {
        temperature: {
          high: 35,
          low: -15
        },
        windSpeed: 50,
        humidity: 90
      };
      
      // Check for extreme conditions
      let warnings = [];
      
      if (weather.temperature >= extremes.temperature.high) {
        warnings.push(`Extreme heat (${weather.temperature}°C)`);
      }
      
      if (weather.temperature <= extremes.temperature.low) {
        warnings.push(`Extreme cold (${weather.temperature}°C)`);
      }
      
      if (weather.windSpeed >= extremes.windSpeed) {
        warnings.push(`High winds (${weather.windSpeed} km/h)`);
      }
      
      if (weather.humidity >= extremes.humidity) {
        warnings.push(`Very high humidity (${weather.humidity}%)`);
      }
      
      // Format response
      if (warnings.length === 0) {
        return "No extreme weather conditions detected.";
      }
      
      return `⚠️ EXTREME WEATHER WARNING ⚠️
${warnings.join("\n")}

Please take appropriate precautions and consider limiting outdoor activities.`;
    }
    """
    pass

# --- Brain Configuration ---

@js_brain([AGENT_TYPE])
def weather_advisor_brain():
    """Configure the brain for the Weather Advisor."""
    return {
        "instructions": ADVISOR_INSTRUCTIONS,
        "clients": [
            {
                "model_name": AI_MODEL,
                "provider": "openai",
            }
        ]
    }

# --- Test Data ---
def create_test_data():
    """Create test data for demonstration."""
    user_preferences = {
        "name": "Alex",
        "preferredStyle": "casual",
        "temperatureSensitivity": "neutral"
    }
    
    weather_data = {
        "temperature": 22,
        "conditions": "sunny",
        "windSpeed": 8,
        "humidity": 65
    }
    
    return user_preferences, weather_data

# --- Test Conversion ---
def test_conversion():
    """Test the JS to Python conversion of our tools."""
    from learn.js_to_python_converter import js_to_python
    
    # Extract JavaScript code from tool
    js_code = suggest_outfit.__doc__.strip()
    
    # Convert to Python
    print("Converting JavaScript to Python:")
    python_code = js_to_python(js_code)
    print(python_code)
    
    # Check if the code is valid Python
    try:
        import ast
        ast.parse(python_code)
        print("\n✅ Successfully converted to valid Python code!")
        return True
    except SyntaxError as e:
        print(f"\n❌ Conversion produced invalid Python code: {e}")
        return False

if __name__ == "__main__":
    # Test the conversion
    conversion_success = test_conversion()
    
    if conversion_success:
        print("\n🎉 The JavaScript code follows best practices and converts successfully!")
        print("To deploy this agent to a NodeAI server:")
        print("1. Update the base_url in the code")
        print("2. Uncomment the deployment code below")
        print("3. Run this script again")
    else:
        print("\n⚠️ The conversion has issues. Please check the JavaScript code.")
    
    """
    # Deployment code (uncomment to use)
    client = NodeAIJSClient(
        base_url="https://your-nodeai-server.com",
        account="WeatherService",
        world="Forecast"
    )
    
    print("\n📦 Deploying Weather Advisor...")
    client.deploy()
    print("✅ Deployment complete!")
    
    # Initialize the agent with test data
    advisor = client.get_mind(AGENT_TYPE, "Advisor")
    user_prefs, weather = create_test_data()
    
    first_thought = TextThought(
        content="Initialize weather advisor",
        metadata={
            "user_preferences": user_prefs,
            "weather_data": weather
        }
    )
    
    # Send the thought
    response = advisor.think(first_thought)
    print(f"\n🤖 Weather Advisor: {response.content}")
    """

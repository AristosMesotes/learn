#!/usr/bin/env python3
"""
Example of JavaScript/TypeScript to Python conversion in a financial analysis agent.

This demonstrates how to use the JS/TS to Python converter to write tools in
JavaScript/TypeScript and have them automatically converted to Python for
the NodeAI backend.
"""

from learn.nodeai_js_deployer import NodeAIJSClient, js_tool, js_box, js_brain
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

# Define a financial data box in TypeScript syntax
@js_box(["FinancialAnalyst"])
class StockData:
    """
    interface StockData {
        symbol: string;
        data: Array<{
            date: string;
            open: number;
            high: number;
            close: number;
            low: number;
            volume: number;
        }>;
        metadata?: {
            name?: string;
            sector?: string;
            industry?: string;
        };
    }
    """
    pass

# JavaScript tool to calculate moving averages
@js_tool(["FinancialAnalyst"], language="javascript")
def calculate_moving_averages(data, window_sizes=[5, 10, 20, 50, 200]):
    """
    function calculateMovingAverages(data, windowSizes = [5, 10, 20, 50, 200]) {
        // Extract close prices
        const prices = data.map(day => day.close);
        
        // Calculate moving averages for each window size
        const movingAverages = {};
        
        windowSizes.forEach(window => {
            const ma = [];
            
            for (let i = 0; i < prices.length; i++) {
                if (i < window - 1) {
                    // Not enough data yet
                    ma.push(null);
                } else {
                    // Calculate average of last 'window' days
                    let sum = 0;
                    for (let j = 0; j < window; j++) {
                        sum += prices[i - j];
                    }
                    ma.push(sum / window);
                }
            }
            
            movingAverages[`MA${window}`] = ma;
        });
        
        return movingAverages;
    }
    """
    pass

# TypeScript tool to detect crossovers
@js_tool(["FinancialAnalyst"], language="typescript")
def detect_crossovers(data: Dict[str, List[float]], short_ma: str = "MA5", long_ma: str = "MA20") -> List[Dict[str, Any]]:
    """
    function detectCrossovers(data: Record<string, Array<number>>, shortMA: string = "MA5", longMA: string = "MA20"): Array<{index: number, type: string}> {
        const shortTermMA = data[shortMA];
        const longTermMA = data[longMA];
        const crossovers = [];
        
        // Start from index 1 since we need to compare with previous day
        for (let i = 1; i < shortTermMA.length; i++) {
            // Skip any nulls
            if (!shortTermMA[i] || !longTermMA[i] || !shortTermMA[i-1] || !longTermMA[i-1]) {
                continue;
            }
            
            // Detect golden cross (short term crosses above long term)
            if (shortTermMA[i] > longTermMA[i] && shortTermMA[i-1] <= longTermMA[i-1]) {
                crossovers.push({
                    index: i,
                    type: "golden_cross"
                });
            }
            
            // Detect death cross (short term crosses below long term)
            if (shortTermMA[i] < longTermMA[i] && shortTermMA[i-1] >= longTermMA[i-1]) {
                crossovers.push({
                    index: i,
                    type: "death_cross"
                });
            }
        }
        
        return crossovers;
    }
    """
    pass

# Python native tool for creating a chart
@js_tool(["FinancialAnalyst"])
def create_stock_chart(stock_data, moving_averages=None, crossovers=None):
    """Create a stock price chart with optional moving averages and crossovers."""
    dates = [day["date"] for day in stock_data["data"]]
    close_prices = [day["close"] for day in stock_data["data"]]
    
    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot the close prices
    ax.plot(dates, close_prices, label="Close Price")
    
    # Add moving averages if provided
    if moving_averages:
        for ma_name, ma_values in moving_averages.items():
            # Skip NaN values at the beginning
            valid_values = [v for v in ma_values if v is not None]
            valid_dates = dates[-len(valid_values):]
            ax.plot(valid_dates, valid_values, label=ma_name)
    
    # Add crossover markers if provided
    if crossovers:
        for crossover in crossovers:
            idx = crossover["index"]
            if idx < len(dates):
                if crossover["type"] == "golden_cross":
                    ax.plot(dates[idx], close_prices[idx], 'g^', markersize=10, label="Golden Cross")
                elif crossover["type"] == "death_cross":
                    ax.plot(dates[idx], close_prices[idx], 'rv', markersize=10, label="Death Cross")
    
    # Add labels and legend
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.set_title(f"Stock Chart: {stock_data['symbol']}")
    ax.legend()
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Convert plot to PNG image
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    
    # Clean up
    plt.close()
    
    return buffer.getvalue()

# Brain configuration for the Financial Analyst agent
@js_brain(["FinancialAnalyst"])
def financial_analyst_brain():
    return {
        "name": "Financial Analyst",
        "version": "1.0",
        "description": "An agent that can analyze financial data using both Python and JavaScript/TypeScript tools",
        "capabilities": [
            "Stock price analysis",
            "Moving average calculation",
            "Technical indicator detection",
            "Chart generation"
        ],
        "config": {
            "default_timeframe": "1y",
            "default_interval": "1d"
        }
    }

# Example of using the agent
def main():
    """Run a demo of the financial analyst agent."""
    # Create a NodeAI client
    client = NodeAIJSClient(
        base_url="http://127.0.0.1:8080",
        account="demo_account",
        world="FinancialWorld"
    )
    
    print("🚀 Financial Analyst Agent Demo")
    print("-------------------------------")
    
    # Note: In a real application, you'd deploy the agent and use it
    # client.deploy()
    
    # Import the registry to check what we've created
    from learn.nodeai_js_deployer import _JS_REGISTRY
    
    print("\n✅ Successfully created Financial Analyst agent with:")
    print(f"  - {len([t for t in _JS_REGISTRY['tools'] if 'FinancialAnalyst' in t['mind_types']])} tools")
    print(f"  - {len([b for b in _JS_REGISTRY['boxes'] if 'FinancialAnalyst' in b['mind_types']])} boxes")
    print(f"  - {len([b for b in _JS_REGISTRY['brains'] if 'FinancialAnalyst' in b['mind_types']])} brain configuration")
    
    print("\nIn a real application, these tools would be deployed to the NodeAI backend")
    print("and could be used by the agent to perform financial analysis.")

if __name__ == "__main__":
    main()

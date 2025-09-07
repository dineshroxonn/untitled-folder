#!/usr/bin/env python3
"""
Test script to verify agent modifications for persistent OBD connections.
"""

import asyncio
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

try:
    from agent import CarDiagnosticAgent
    print("✓ Agent module imported successfully")
    
    def test_agent_modifications():
        """Test that the agent has been modified correctly."""
        agent = CarDiagnosticAgent()
        
        # Check that the class docstring mentions persistent connections
        if "persistent" in agent.__class__.__doc__.lower():
            print("✓ Agent class docstring updated to mention persistent connections")
        else:
            print("⚠ Agent class docstring not updated")
            
        print(f"Agent class: {agent.__class__.__name__}")
        print(f"Module: {agent.__class__.__module__}")
        
        # List all methods to verify they exist
        methods = [
            'initialize_obd_system',
            'connect_obd', 
            'disconnect_obd',
            '_handle_obd_connect_command',
            '_handle_obd_disconnect_command'
        ]
        
        for method in methods:
            if hasattr(agent, method):
                print(f"✓ {method} method exists")
            else:
                print(f"✗ {method} method missing")
                
        print("\n✓ Agent modifications verification complete")
        
    test_agent_modifications()
    
except ImportError as e:
    print(f"✗ Failed to import Agent: {e}")
    print("Please check the agent.py file for issues.")
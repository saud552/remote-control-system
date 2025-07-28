#!/usr/bin/env python3
"""
Command Line Interface for Advanced Tool Manager
"""

import sys
import json
import asyncio
import argparse
from tool_manager import AdvancedToolManager
from enhanced_tool_integration import EnhancedToolIntegration, IntegrationConfig

async def main():
    parser = argparse.ArgumentParser(description='Advanced Tool Manager CLI')
    parser.add_argument('--install', help='Install a tool')
    parser.add_argument('--update', help='Update a tool')
    parser.add_argument('--run', help='Run a tool')
    parser.add_argument('--stop', help='Stop a tool')
    parser.add_argument('--status', action='store_true', help='Get tool status')
    parser.add_argument('--list', action='store_true', help='List available tools')
    parser.add_argument('--attack', help='Execute attack (JSON string)')
    parser.add_argument('--init', action='store_true', help='Initialize integration system')
    
    args = parser.parse_args()
    
    if args.init:
        # Initialize integration system
        config = IntegrationConfig()
        integration = EnhancedToolIntegration(config)
        success = await integration.initialize_integration()
        
        if success:
            print(json.dumps({
                "success": True,
                "message": "Integration system initialized successfully"
            }))
        else:
            print(json.dumps({
                "success": False,
                "error": "Failed to initialize integration system"
            }))
        return
    
    if args.attack:
        # Execute attack
        try:
            attack_config = json.loads(args.attack)
            config = IntegrationConfig()
            integration = EnhancedToolIntegration(config)
            await integration.initialize_integration()
            
            result = await integration.execute_advanced_attack(attack_config)
            print(json.dumps(result))
        except Exception as e:
            print(json.dumps({
                "success": False,
                "error": str(e)
            }))
        return
    
    # Initialize tool manager
    tool_manager = AdvancedToolManager()
    
    if args.install:
        # Install tool
        result = await tool_manager.install_tool(args.install)
        print(json.dumps(result))
        return
    
    if args.update:
        # Update tool
        result = await tool_manager.update_tool(args.update)
        print(json.dumps(result))
        return
    
    if args.run:
        # Run tool
        result = await tool_manager.run_tool(args.run)
        print(json.dumps(result))
        return
    
    if args.stop:
        # Stop tool
        result = await tool_manager.stop_tool(args.stop)
        print(json.dumps(result))
        return
    
    if args.status:
        # Get tool status
        status = tool_manager.get_tool_statistics()
        print(json.dumps(status))
        return
    
    if args.list:
        # List available tools
        tools = tool_manager.get_available_tools()
        print(json.dumps(tools))
        return
    
    # Default: show help
    parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())
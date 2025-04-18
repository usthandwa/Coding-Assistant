#!/usr/bin/env python
"""
WordPress Python Bridge for AI Coding Agent
"""
import argparse
import json
import sys
import os
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), "wp_bridge.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the WordPress bridge"""
    parser = argparse.ArgumentParser(description="WordPress Python Bridge for AI Coding Agent")
    parser.add_argument("--endpoint", required=True, help="API endpoint to call")
    parser.add_argument("--params", required=True, help="JSON-encoded parameters")
    args = parser.parse_args()
    
    try:
        # Parse parameters
        params = json.loads(args.params)
        
        # Call the appropriate endpoint
        if args.endpoint == 'process_query':
            response = process_query(params)
        elif args.endpoint == 'get_repository_status':
            response = get_repository_status(params)
        elif args.endpoint == 'analyze_code':
            response = analyze_code(params)
        else:
            response = {'success': False, 'message': f"Unknown endpoint: {args.endpoint}"}
            
        # Output response as JSON
        print(json.dumps(response))
        
    except Exception as e:
        logger.error(f"Error in WordPress bridge: {e}")
        print(json.dumps({'success': False, 'message': str(e)}))
        
def process_query(params):
    """Process a query from WordPress"""
    try:
        # Add the current directory to sys.path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        
        if parent_dir not in sys.path:
            sys.path.append(parent_dir)
            
        # Import the API bridge
        from wp_integration.api_bridge import WordPressAPIBridge
        
        # Load configuration
        from utils.config_utils import load_config
        config = load_config(os.path.join(parent_dir, 'config/default_config.yaml'))
        
        # Create the API bridge
        api_bridge = WordPressAPIBridge(config['wp_integration'])
        
        # Call the process_query_callback
        response = api_bridge.process_query_callback(params)
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return {'success': False, 'message': str(e)}
        
def get_repository_status(params):
    """Get repository status from WordPress"""
    try:
        # Add the current directory to sys.path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        
        if parent_dir not in sys.path:
            sys.path.append(parent_dir)
            
        # Import the API bridge
        from wp_integration.api_bridge import WordPressAPIBridge
        
        # Load configuration
        from utils.config_utils import load_config
        config = load_config(os.path.join(parent_dir, 'config/default_config.yaml'))
        
        # Create the API bridge
        api_bridge = WordPressAPIBridge(config['wp_integration'])
        
        # Call the get_repository_status_callback
        response = api_bridge.get_repository_status_callback(params)
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting repository status: {e}")
        return {'success': False, 'message': str(e)}
        
def analyze_code(params):
    """Analyze code from WordPress"""
    try:
        # Add the current directory to sys.path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        
        if parent_dir not in sys.path:
            sys.path.append(parent_dir)
            
        # Import the API bridge
        from wp_integration.api_bridge import WordPressAPIBridge
        
        # Load configuration
        from utils.config_utils import load_config
        config = load_config(os.path.join(parent_dir, 'config/default_config.yaml'))
        
        # Create the API bridge
        api_bridge = WordPressAPIBridge(config['wp_integration'])
        
        # Call the analyze_code_callback
        response = api_bridge.analyze_code_callback(params)
        
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing code: {e}")
        return {'success': False, 'message': str(e)}

if __name__ == "__main__":
    main()

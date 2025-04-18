# ai_coding_agent/utils/config_utils.py
import os
import yaml
import json
import logging
from pathlib import Path

def load_config(config_path):
    """
    Load configuration from file
    
    Args:
        config_path (str): Path to configuration file
        
    Returns:
        dict: Configuration dict
    """
    logger = logging.getLogger(__name__)
    
    try:
        config_path = Path(config_path)
        
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}, using default config")
            return _default_config()
            
        extension = config_path.suffix.lower()
        
        if extension == '.yaml' or extension == '.yml':
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
        elif extension == '.json':
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            logger.warning(f"Unsupported config file format: {extension}, using default config")
            return _default_config()
            
        # Merge with default config to ensure all required settings exist
        return _merge_configs(_default_config(), config)
        
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return _default_config()
        
def _default_config():
    """Default configuration"""
    return {
        "repository_integration": {
            "storage_dir": "repositories",
            "max_repo_size_mb": 100,
            "index_file_extensions": [".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".c", ".cpp", ".h", ".hpp", ".cs", ".go", ".rs"],
            "ignore_patterns": ["node_modules", "venv", ".git", "__pycache__", "*.min.js"]
        },
        "code_analysis": {
            "enable_syntax_parsing": True,
            "enable_semantic_analysis": True,
            "max_files_to_analyze": 1000,
            "line_length_limit": 120
        },
        "context_management": {
            "storage_dir": "sessions",
            "max_context_items": 50,
            "relevance_threshold": 0.5
        },
        "reasoning": {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 4000,
            "temperature": 0.7,
            "top_p": 0.9,
            "enable_heuristics": True
        },
        "interaction": {
            "response_format": "markdown",
            "code_highlighting": True,
            "max_suggestions": 5
        },
        "logging": {
            "level": "INFO",
            "file": "ai_coding_agent.log",
            "max_file_size_mb": 10,
            "backup_count": 3
        },
        "wp_integration": {
            "enabled": False,
            "api_endpoint": "/wp-json/ai-coding-agent/v1",
            "auth_required": True
        }
    }
    
def _merge_configs(default_config, user_config):
    """Merge default and user configs, ensuring all required keys exist"""
    merged_config = default_config.copy()
    
    for key, value in user_config.items():
        if key in merged_config and isinstance(merged_config[key], dict) and isinstance(value, dict):
            merged_config[key] = _merge_configs(merged_config[key], value)
        else:
            merged_config[key] = value
            
    return merged_config
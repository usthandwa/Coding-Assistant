# CodingAssistant/code_analysis/syntax_parser.py
import logging
from pathlib import Path
import os
import subprocess
import json
from tree_sitter import Language, Parser

class SyntaxParser:
    """
    Parses code syntax for multiple programming languages
    """
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.parsers = {}
        self.language_extensions = {
            'python': ['.py'],
            'javascript': ['.js', '.jsx'],
            'typescript': ['.ts', '.tsx'],
            'java': ['.java'],
            'c': ['.c', '.h'],
            'cpp': ['.cpp', '.hpp', '.cc', '.hh'],
            'csharp': ['.cs'],
            'rust': ['.rs'],
            'go': ['.go']
        }
        self._initialize_parsers()
        
    def _initialize_parsers(self):
        """Initialize tree-sitter parsers for supported languages"""
        try:
            # Path to tree-sitter language libraries
            # For a real implementation, these should be downloaded and built
            # See: https://github.com/tree-sitter/py-tree-sitter#language-libraries
            
            # This is a placeholder for actual implementation
            languages_dir = os.path.join(os.path.dirname(__file__), 'tree-sitter-langs')
            os.makedirs(languages_dir, exist_ok=True)
            
            # In a real implementation, we would load the language libraries:
            # Language.build_library(
            #     os.path.join(languages_dir, 'languages.so'),
            #     [
            #         os.path.join(languages_dir, 'tree-sitter-python'),
            #         os.path.join(languages_dir, 'tree-sitter-javascript'),
            #         # ... other languages
            #     ]
            # )
            
            # For demonstration, we'll create dummy parsers
            # In a real implementation, we would load them like this:
            # PY_LANGUAGE = Language(os.path.join(languages_dir, 'languages.so'), 'python')
            # JS_LANGUAGE = Language(os.path.join(languages_dir, 'languages.so'), 'javascript')
            # ...
            
            # Create parsers for each language
            for language in ['python', 'javascript', 'typescript', 'java', 'c', 'cpp', 'csharp', 'rust', 'go']:
                parser = Parser()
                # parser.set_language(globals()[f"{language.upper()}_LANGUAGE"])
                self.parsers[language] = parser
                
            self.logger.info(f"Initialized tree-sitter parsers for {len(self.parsers)} languages")
            
        except Exception as e:
            self.logger.error(f"Error initializing tree-sitter parsers: {e}")
            
    def parse_repository(self, repo_path):
        """
        Parse syntax for all code files in a repository
        
        Args:
            repo_path (str): Path to the repository
            
        Returns:
            dict: Parsed syntax information
        """
        self.logger.info(f"Parsing syntax for repository: {repo_path}")
        
        results = {
            'total_files': 0,
            'parsed_files': 0,
            'error_files': 0,
            'by_language': {}
        }
        
        try:
            repo_path = Path(repo_path)
            
            # Find all code files in the repository
            for path in repo_path.rglob('*'):
                if path.is_file() and '.git' not in str(path) and self._is_code_file(path):
                    results['total_files'] += 1
                    
                    try:
                        language = self._detect_language(path)
                        if language and language in self.parsers:
                            ast = self._parse_file(path, language)
                            
                            if language not in results['by_language']:
                                results['by_language'][language] = {
                                    'files': 0,
                                    'syntax_errors': 0
                                }
                                
                            results['by_language'][language]['files'] += 1
                            results['parsed_files'] += 1
                            
                            # Additional processing can be done here to store or analyze the AST
                            
                    except Exception as e:
                        self.logger.warning(f"Error parsing file {path}: {e}")
                        results['error_files'] += 1
                        
            self.logger.info(f"Parsed {results['parsed_files']} files out of {results['total_files']}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error during syntax parsing: {e}")
            return None
            
    def _is_code_file(self, path):
        """Check if a file is a code file"""
        extension = path.suffix.lower()
        for extensions in self.language_extensions.values():
            if extension in extensions:
                return True
        return False
        
    def _detect_language(self, path):
        """Detect the programming language of a file"""
        extension = path.suffix.lower()
        for language, extensions in self.language_extensions.items():
            if extension in extensions:
                return language
        return None
        
    def _parse_file(self, path, language):
        """Parse a file and generate AST"""
        parser = self.parsers.get(language)
        if not parser:
            self.logger.warning(f"No parser available for {language}")
            return None
            
        try:
            with open(path, 'rb') as f:
                source_code = f.read()
                
            # Parse the source code
            tree = parser.parse(source_code)
            
            # Return the syntax tree
            return tree
            
        except Exception as e:
            self.logger.error(f"Error parsing {path}: {e}")
            raise
            
    def parse_code_snippet(self, code, language):
        """
        Parse a code snippet and return the AST
        
        Args:
            code (str): Code snippet
            language (str): Programming language
            
        Returns:
            object: Abstract Syntax Tree
        """
        if language not in self.parsers:
            self.logger.warning(f"No parser available for {language}")
            return None
            
        try:
            parser = self.parsers[language]
            tree = parser.parse(code.encode('utf-8'))
            return tree
        except Exception as e:
            self.logger.error(f"Error parsing code snippet: {e}")
            return None


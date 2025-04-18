# CodingAssistant/code_analysis/semantic_analyzer.py
import logging
from pathlib import Path
import os
import subprocess
import json

class SemanticAnalyzer:
    """
    Analyzes code semantics to understand meaning and relationships
    """
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.language_handlers = {
            'python': self._analyze_python,
            'javascript': self._analyze_javascript,
            'typescript': self._analyze_typescript,
            'java': self._analyze_java,
            'csharp': self._analyze_csharp
        }
        
    def analyze_repository(self, repo_path):
        """
        Perform semantic analysis on a repository
        
        Args:
            repo_path (str): Path to the repository
            
        Returns:
            dict: Semantic analysis results
        """
        self.logger.info(f"Performing semantic analysis for repository: {repo_path}")
        
        results = {
            'total_files': 0,
            'analyzed_files': 0,
            'error_files': 0,
            'by_language': {}
        }
        
        try:
            repo_path = Path(repo_path)
            language_files = self._categorize_files(repo_path)
            
            # Analyze files for each language
            for language, files in language_files.items():
                if language in self.language_handlers:
                    language_results = self.language_handlers[language](repo_path, files)
                    results['by_language'][language] = language_results
                    results['total_files'] += language_results['total_files']
                    results['analyzed_files'] += language_results['analyzed_files']
                    results['error_files'] += language_results['error_files']
                else:
                    self.logger.warning(f"No semantic analyzer available for {language}")
                    
            self.logger.info(f"Semantic analysis complete: {results['analyzed_files']} files analyzed")
            return results
            
        except Exception as e:
            self.logger.error(f"Error during semantic analysis: {e}")
            return None
            
    def _categorize_files(self, repo_path):
        """Categorize files by programming language"""
        language_extensions = {
            'python': ['.py'],
            'javascript': ['.js', '.jsx'],
            'typescript': ['.ts', '.tsx'],
            'java': ['.java'],
            'csharp': ['.cs'],
            'cpp': ['.cpp', '.hpp', '.cc', '.hh'],
            'c': ['.c', '.h'],
            'go': ['.go'],
            'rust': ['.rs'],
            'php': ['.php']
        }
        
        language_files = {lang: [] for lang in language_extensions}
        
        for path in repo_path.rglob('*'):
            if path.is_file() and '.git' not in str(path):
                extension = path.suffix.lower()
                for language, extensions in language_extensions.items():
                    if extension in extensions:
                        language_files[language].append(path)
                        break
                        
        return language_files
        
    def _analyze_python(self, repo_path, files):
        """Analyze Python files"""
        self.logger.info(f"Analyzing {len(files)} Python files")
        
        results = {
            'total_files': len(files),
            'analyzed_files': 0,
            'error_files': 0,
            'entities': {
                'classes': [],
                'functions': [],
                'imports': [],
                'variables': []
            }
        }
        
        try:
            import ast
            
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        source = f.read()
                        
                    tree = ast.parse(source)
                    
                    # Extract classes, functions, imports, and global variables
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            results['entities']['classes'].append({
                                'name': node.name,
                                'file': str(file_path.relative_to(repo_path)),
                                'line': node.lineno,
                                'methods': [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
                                'bases': [b.id if isinstance(b, ast.Name) else 'complex' for b in node.bases]
                            })
                        elif isinstance(node, ast.FunctionDef) and node.parent_node.type != ast.ClassDef:
                            results['entities']['functions'].append({
                                'name': node.name,
                                'file': str(file_path.relative_to(repo_path)),
                                'line': node.lineno,
                                'args': [arg.arg for arg in node.args.args]
                            })
                        elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                            if isinstance(node, ast.Import):
                                module = None
                                names = [alias.name for alias in node.names]
                            else:  # ImportFrom
                                module = node.module
                                names = [alias.name for alias in node.names]
                                
                            results['entities']['imports'].append({
                                'file': str(file_path.relative_to(repo_path)),
                                'line': node.lineno,
                                'module': module,
                                'names': names
                            })
                        elif isinstance(node, ast.Assign) and all(isinstance(target, ast.Name) for target in node.targets):
                            for target in node.targets:
                                if isinstance(target, ast.Name):
                                    results['entities']['variables'].append({
                                        'name': target.id,
                                        'file': str(file_path.relative_to(repo_path)),
                                        'line': node.lineno
                                    })
                                    
                    results['analyzed_files'] += 1
                    
                except Exception as e:
                    self.logger.warning(f"Error analyzing Python file {file_path}: {e}")
                    results['error_files'] += 1
                    
            return results
            
        except ImportError:
            self.logger.error("Python ast module not available")
            results['error_files'] = len(files)
            return results
            
    def _analyze_javascript(self, repo_path, files):
        """Analyze JavaScript files"""
        # Implementation for JavaScript analysis
        return {
            'total_files': len(files),
            'analyzed_files': 0,
            'error_files': len(files),
            'entities': {}
        }
        
    def _analyze_typescript(self, repo_path, files):
        """Analyze TypeScript files"""
        # Implementation for TypeScript analysis
        return {
            'total_files': len(files),
            'analyzed_files': 0,
            'error_files': len(files),
            'entities': {}
        }
        
    def _analyze_java(self, repo_path, files):
        """Analyze Java files"""
        # Implementation for Java analysis
        return {
            'total_files': len(files),
            'analyzed_files': 0,
            'error_files': len(files),
            'entities': {}
        }
        
    def _analyze_csharp(self, repo_path, files):
        """Analyze C# files"""
        # Implementation for C# analysis
        return {
            'total_files': len(files),
            'analyzed_files': 0,
            'error_files': len(files),
            'entities': {}
        }
        
    def analyze_code_snippet(self, code, language):
        """
        Analyze a code snippet for semantic meaning
        
        Args:
            code (str): Code snippet
            language (str): Programming language
            
        Returns:
            dict: Semantic analysis results
        """
        if language not in self.language_handlers:
            self.logger.warning(f"No semantic analyzer available for {language}")
            return None
            
        try:
            # Use a temporary file for analysis
            import tempfile
            
            with tempfile.NamedTemporaryFile(suffix=f'.{language}', mode='w', delete=False) as temp:
                temp.write(code)
                temp_path = temp.name
                
            # Create a temporary directory to simulate a repository
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_repo = Path(temp_dir)
                temp_file = temp_repo / f"snippet.{language}"
                
                with open(temp_file, 'w') as f:
                    f.write(code)
                    
                # Call the appropriate language handler
                results = self.language_handlers[language](temp_repo, [temp_file])
                
                # Clean up
                os.unlink(temp_path)
                
                return results
                
        except Exception as e:
            self.logger.error(f"Error analyzing code snippet: {e}")
            return None


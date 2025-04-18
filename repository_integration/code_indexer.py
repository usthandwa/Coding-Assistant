# CodingAssistant/repository_integration/code_indexer.py
import logging
from pathlib import Path
import os
import subprocess
import json
from collections import defaultdict

class CodeIndexer:
    """
    Builds a searchable index of code structures, dependencies, and relationships
    """
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.language_extensions = {
            'python': ['.py'],
            'javascript': ['.js', '.jsx', '.ts', '.tsx'],
            'java': ['.java'],
            'c': ['.c', '.h'],
            'cpp': ['.cpp', '.hpp', '.cc', '.hh'],
            'csharp': ['.cs'],
            'go': ['.go'],
            'rust': ['.rs'],
            'php': ['.php'],
            'ruby': ['.rb']
        }
        self.index = defaultdict(list)
        
    def index_repository(self, repo_data):
        """
        Index a repository's code for searching
        
        Args:
            repo_data (dict): Repository data from GitParser
            
        Returns:
            dict: Indexed repository data
        """
        if not repo_data:
            self.logger.error("No repository data to index")
            return None
            
        self.logger.info(f"Indexing repository: {repo_data['path']}")
        
        try:
            # Create file-language mapping
            files_by_language = self._categorize_files(repo_data['files'])
            
            # Index files by language
            for language, files in files_by_language.items():
                self._index_files_by_language(repo_data['path'], language, files)
                
            # Build cross-references
            self._build_cross_references(repo_data['path'], files_by_language)
            
            return {
                'repository': repo_data['path'],
                'indexed_files': len(repo_data['files']),
                'language_distribution': {lang: len(files) for lang, files in files_by_language.items()},
                'index_summary': {k: len(v) for k, v in self.index.items()}
            }
            
        except Exception as e:
            self.logger.error(f"Error indexing repository: {e}")
            return None
            
    def _categorize_files(self, files):
        """Categorize files by programming language"""
        files_by_language = defaultdict(list)
        
        for file in files:
            extension = file['extension'].lower()
            language = None
            
            # Determine language by extension
            for lang, extensions in self.language_extensions.items():
                if extension in extensions:
                    language = lang
                    break
                    
            if language:
                files_by_language[language].append(file)
            else:
                files_by_language['other'].append(file)
                
        return files_by_language
        
    def _index_files_by_language(self, repo_path, language, files):
        """Index files for a specific language"""
        if language == 'python':
            self._index_python_files(repo_path, files)
        elif language in ['javascript', 'typescript']:
            self._index_js_files(repo_path, files)
        elif language == 'java':
            self._index_java_files(repo_path, files)
        # Add more language-specific indexers as needed
        
    def _index_python_files(self, repo_path, files):
        """Index Python files"""
        for file in files:
            file_path = os.path.join(repo_path, file['path'])
            try:
                # Could use ast module to parse Python files
                import ast
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        tree = ast.parse(f.read())
                        
                        # Index classes
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                self.index['classes'].append({
                                    'name': node.name,
                                    'file': file['path'],
                                    'line': node.lineno
                                })
                            elif isinstance(node, ast.FunctionDef):
                                self.index['functions'].append({
                                    'name': node.name,
                                    'file': file['path'],
                                    'line': node.lineno
                                })
                            elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                                self.index['imports'].append({
                                    'file': file['path'],
                                    'line': node.lineno,
                                    'names': [alias.name for alias in node.names]
                                })
                    except SyntaxError as e:
                        self.logger.warning(f"Syntax error in {file_path}: {e}")
            except Exception as e:
                self.logger.error(f"Error indexing Python file {file_path}: {e}")
                
    def _index_js_files(self, repo_path, files):
        """Index JavaScript/TypeScript files"""
        # Implementation for JavaScript/TypeScript indexing
        pass
        
    def _index_java_files(self, repo_path, files):
        """Index Java files"""
        # Implementation for Java indexing
        pass
        
    def _build_cross_references(self, repo_path, files_by_language):
        """Build cross-references between code entities"""
        # Implementation for cross-referencing
        pass
        
    def search_index(self, query, entity_type=None, max_results=10):
        """
        Search the code index
        
        Args:
            query (str): Search query
            entity_type (str, optional): Entity type to search (classes, functions, etc.)
            max_results (int, optional): Maximum number of results
            
        Returns:
            list: Search results
        """
        results = []
        
        if entity_type and entity_type in self.index:
            # Search specific entity type
            for item in self.index[entity_type]:
                if query.lower() in item['name'].lower():
                    results.append(item)
                    if len(results) >= max_results:
                        break
        else:
            # Search all entity types
            for entity_type, items in self.index.items():
                for item in items:
                    if 'name' in item and query.lower() in item['name'].lower():
                        results.append({**item, 'type': entity_type})
                        if len(results) >= max_results:
                            break
                            
        return results
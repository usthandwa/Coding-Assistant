# ai_coding_agent/source_processing/code_source_scanner.py
import os
import logging
import re
from pathlib import Path
import git
from git import Repo

class CodeSourceScanner:
    """
    Scans code from multiple sources: directories, git, files, or snippets
    """
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.language_extensions = {
            'python': ['.py'],
            'javascript': ['.js', '.jsx'],
            'typescript': ['.ts', '.tsx'],
            'java': ['.java'],
            'c': ['.c', '.h'],
            'cpp': ['.cpp', '.hpp', '.cc', '.hh'],
            'csharp': ['.cs'],
            'go': ['.go'],
            'rust': ['.rs'],
            'php': ['.php'],
            'ruby': ['.rb'],
            'swift': ['.swift'],
            'kotlin': ['.kt', '.kts'],
            'scala': ['.scala'],
            'html': ['.html', '.htm'],
            'css': ['.css'],
            'sql': ['.sql'],
            'yaml': ['.yaml', '.yml'],
            'json': ['.json'],
            'markdown': ['.md', '.markdown'],
            'bash': ['.sh', '.bash'],
            'powershell': ['.ps1'],
            'r': ['.r'],
            'lua': ['.lua'],
            'perl': ['.pl', '.pm'],
            'xml': ['.xml']
        }
        self.ignore_patterns = config.get('ignore_patterns', [
            '__pycache__', 
            'node_modules', 
            '.git', 
            '.idea', 
            '.vscode',
            '*.min.js',
            '*.min.css',
            '*.map',
            '*.pyc',
            '.env',
            'venv',
            'env',
            'virtualenv',
            'dist',
            'build'
        ])
        
    def scan_directory(self, dir_path, recursive=True):
        """
        Scan a directory for code files
        
        Args:
            dir_path (str): Path to directory
            recursive (bool): Whether to scan recursively
            
        Returns:
            dict: Scanned directory data
        """
        self.logger.info(f"Scanning directory: {dir_path}")
        
        try:
            dir_path = Path(dir_path)
            if not dir_path.exists() or not dir_path.is_dir():
                self.logger.error(f"Invalid directory path: {dir_path}")
                return None
                
            files_data = []
            dir_stats = {
                'total_files': 0,
                'code_files': 0,
                'by_language': {}
            }
            
            # Walk through directory
            for root, dirs, files in os.walk(dir_path):
                # Skip non-recursive for subdirectories
                if not recursive and root != str(dir_path):
                    continue
                    
                # Skip ignored directories
                dirs[:] = [d for d in dirs if not self._should_ignore(d)]
                
                # Process each file
                for file in files:
                    if self._should_ignore(file):
                        continue
                        
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(dir_path)
                    
                    try:
                        # Get file stats
                        file_size = file_path.stat().st_size
                        dir_stats['total_files'] += 1
                        
                        # Skip non-code files or files that are too large
                        if not self._is_code_file(file_path) or file_size > self.config.get('max_file_size_kb', 1000) * 1024:
                            continue
                            
                        # Read file content
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                        except Exception as file_e:
                            self.logger.warning(f"Error reading file {file_path}: {file_e}")
                            continue
                            
                        # Detect language
                        language = self._detect_language(file_path, content)
                        
                        # Update stats
                        dir_stats['code_files'] += 1
                        dir_stats['by_language'][language] = dir_stats['by_language'].get(language, 0) + 1
                        
                        # Add file data
                        files_data.append({
                            'path': str(rel_path),
                            'full_path': str(file_path),
                            'language': language,
                            'size': file_size,
                            'content': content
                        })
                        
                    except Exception as e:
                        self.logger.warning(f"Error processing file {file_path}: {e}")
                
            self.logger.info(f"Scanned {dir_stats['total_files']} files, found {dir_stats['code_files']} code files in {len(dir_stats['by_language'])} languages")
            
            # Check if it's also a git repository
            git_info = None
            try:
                if (dir_path / '.git').exists():
                    git_info = self._get_git_info(dir_path)
            except Exception as e:
                self.logger.info(f"Directory is not a Git repository or error accessing Git info: {e}")
            
            return {
                'source_type': 'directory',
                'path': str(dir_path),
                'files': files_data,
                'stats': dir_stats,
                'git_info': git_info
            }
            
        except Exception as e:
            self.logger.error(f"Error scanning directory: {e}")
            return None
    
    def scan_git_repository(self, repo_path):
        """
        Scan a git repository
        
        Args:
            repo_path (str): Path to the Git repository or Git URL
            
        Returns:
            dict: Repository data
        """
        self.logger.info(f"Scanning Git repository: {repo_path}")
        
        try:
            # Check if it's a URL
            if repo_path.startswith(('http://', 'https://', 'git@')):
                local_path = self.clone_repository(repo_path)
                if not local_path:
                    self.logger.error(f"Failed to clone repository: {repo_path}")
                    return None
                repo_path = local_path
                
            # Now handle as a local path
            repo_path = Path(repo_path)
            
            # Get Git repository info
            git_info = self._get_git_info(repo_path)
            if not git_info:
                self.logger.error(f"Invalid Git repository: {repo_path}")
                return None
                
            # Scan directory contents
            dir_scan = self.scan_directory(repo_path, recursive=True)
            if not dir_scan:
                return None
                
            # Add git specific data
            return {
                'source_type': 'git_repository',
                'path': str(repo_path),
                'files': dir_scan['files'],
                'stats': dir_scan['stats'],
                'git_info': git_info
            }
            
        except Exception as e:
            self.logger.error(f"Error scanning Git repository: {e}")
            return None
            
    def analyze_file(self, file_path):
        """
        Analyze a single file
        
        Args:
            file_path (str): Path to file
            
        Returns:
            dict: File data
        """
        self.logger.info(f"Analyzing file: {file_path}")
        
        try:
            file_path = Path(file_path)
            if not file_path.exists() or not file_path.is_file():
                self.logger.error(f"Invalid file path: {file_path}")
                return None
                
            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception as e:
                self.logger.error(f"Error reading file {file_path}: {e}")
                return None
                
            # Detect language
            language = self._detect_language(file_path, content)
            
            return {
                'source_type': 'file',
                'path': str(file_path),
                'language': language,
                'size': file_path.stat().st_size,
                'content': content
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing file: {e}")
            return None
            
    def analyze_snippet(self, snippet, language=None):
        """
        Analyze a code snippet
        
        Args:
            snippet (str): Code snippet
            language (str, optional): Programming language
            
        Returns:
            dict: Snippet data
        """
        self.logger.info(f"Analyzing code snippet of length: {len(snippet)}")
        
        try:
            # Detect language if not provided
            if not language:
                language = self._detect_language_from_content(snippet)
                
            return {
                'source_type': 'snippet',
                'language': language,
                'size': len(snippet),
                'content': snippet
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing snippet: {e}")
            return None
            
    def clone_repository(self, repo_url):
        """
        Clone a Git repository
        
        Args:
            repo_url (str): Git repository URL
            
        Returns:
            str: Path to cloned repository
        """
        self.logger.info(f"Cloning repository: {repo_url}")
        
        try:
            # Create temp directory for clones if it doesn't exist
            clone_dir = Path(self.config.get('clone_dir', 'cloned_repos'))
            clone_dir.mkdir(exist_ok=True)
            
            # Generate a unique directory name based on the URL
            import hashlib
            repo_hash = hashlib.md5(repo_url.encode()).hexdigest()
            target_dir = clone_dir / repo_hash
            
            # Check if already cloned
            if target_dir.exists():
                self.logger.info(f"Repository already cloned at: {target_dir}")
                
                # Try to update it
                try:
                    repo = Repo(target_dir)
                    origin = repo.remotes.origin
                    origin.pull()
                    self.logger.info("Repository updated successfully")
                except Exception as e:
                    self.logger.warning(f"Error updating repository: {e}")
                    
                return str(target_dir)
                
            # Clone the repository
            Repo.clone_from(repo_url, target_dir)
            self.logger.info(f"Repository cloned successfully to: {target_dir}")
            
            return str(target_dir)
            
        except Exception as e:
            self.logger.error(f"Error cloning repository: {e}")
            return None
    
    def _is_code_file(self, file_path):
        """Check if a file is a code file"""
        # Check by extension
        ext = file_path.suffix.lower()
        for extensions in self.language_extensions.values():
            if ext in extensions:
                return True
                
        # Could also check by content pattern, but extension is usually sufficient
        return False
        
    def _detect_language(self, file_path, content=None):
        """Detect programming language based on file extension and content"""
        # Extension-based detection
        ext = file_path.suffix.lower()
        for language, extensions in self.language_extensions.items():
            if ext in extensions:
                return language
                
        # Content-based detection if extension didn't work
        if content:
            return self._detect_language_from_content(content)
                
        return 'unknown'
        
    def _detect_language_from_content(self, content):
        """Detect programming language from content"""
        # Python indicators
        if re.search(r'def\s+\w+\s*\(.*\)\s*:', content) or re.search(r'import\s+\w+', content):
            return 'python'
            
        # JavaScript indicators
        if re.search(r'function\s+\w+\s*\(.*\)\s*{', content) or re.search(r'const|let|var', content):
            return 'javascript'
            
        # TypeScript indicators
        if re.search(r'interface\s+\w+\s*{', content) or re.search(r':\s*\w+\s*[,)]', content):
            return 'typescript'
            
        # Java indicators
        if re.search(r'public\s+class|private\s+class', content) or re.search(r'import\s+java\.', content):
            return 'java'
            
        # C/C++ indicators
        if re.search(r'#include\s*<', content) or re.search(r'int\s+main\s*\(', content):
            if re.search(r'std::', content) or re.search(r'template\s*<', content):
                return 'cpp'
            return 'c'
            
        # C# indicators
        if re.search(r'namespace\s+\w+', content) or re.search(r'using\s+System;', content):
            return 'csharp'
            
        # HTML indicators
        if re.search(r'<!DOCTYPE\s+html>|<html', content):
            return 'html'
            
        # CSS indicators
        if re.search(r'\{[^}]*color:', content) or re.search(r'\{[^}]*margin:', content):
            return 'css'
            
        # JSON indicators
        if content.strip().startswith('{') and content.strip().endswith('}'):
            try:
                import json
                json.loads(content)
                return 'json'
            except:
                pass
                
        # YAML indicators
        if re.search(r'^\s*\w+:\s*\w+', content, re.MULTILINE):
            return 'yaml'
            
        return 'unknown'
        
    def _should_ignore(self, path):
        """Check if a file or directory should be ignored"""
        path_str = str(path)
        
        # Check against ignore patterns
        for pattern in self.ignore_patterns:
            if '*' in pattern:
                # Simple glob pattern
                pattern_regex = pattern.replace('.', '\.').replace('*', '.*')
                if re.search(pattern_regex, path_str):
                    return True
            elif pattern in path_str:
                return True
                
        return False
        
    def _get_git_info(self, repo_path):
        """Get Git repository information"""
        try:
            repo = Repo(repo_path)
            
            # Check if it's a valid git repository
            if repo.bare:
                self.logger.warning(f"Repository {repo_path} is a bare repository")
                return None
                
            # Get repo info
            active_branch = None
            try:
                active_branch = repo.active_branch.name
            except:
                # Detached HEAD state or other issues
                pass
                
            branches = [branch.name for branch in repo.branches]
            
            # Get recent commits
            commits = []
            for commit in list(repo.iter_commits())[:10]:  # Get last 10 commits
                commits.append({
                    'hash': commit.hexsha,
                    'message': commit.message,
                    'author': commit.author.name,
                    'date': commit.authored_datetime.isoformat()
                })
                
            # Get remotes
            remotes = {remote.name: remote.url for remote in repo.remotes}
            
            return {
                'active_branch': active_branch,
                'branches': branches,
                'commits': commits,
                'remotes': remotes
            }
            
        except Exception as e:
            self.logger.error(f"Error getting Git info: {e}")
            return None
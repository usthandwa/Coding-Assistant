# CodingAssistant/repository_integration/git_parser.py
import logging
import os
from pathlib import Path
import git
from git import Repo

class GitParser:
    """
    Handles Git repository parsing, extracting structure and metadata
    """
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def parse_repository(self, repo_path):
        """
        Parse a Git repository to extract structure and metadata
        
        Args:
            repo_path (Path): Path to the Git repository
            
        Returns:
            dict: Repository structure and metadata
        """
        self.logger.info(f"Parsing Git repository: {repo_path}")
        
        try:
            repo = Repo(repo_path)
            
            # Check if it's a valid git repository
            if not repo.bare:
                return {
                    'path': str(repo_path),
                    'active_branch': self._get_active_branch(repo),
                    'branches': self._get_branches(repo),
                    'commits': self._get_recent_commits(repo),
                    'remotes': self._get_remotes(repo),
                    'files': self._get_files(repo_path),
                    'submodules': self._get_submodules(repo)
                }
            else:
                self.logger.warning(f"Repository {repo_path} is a bare repository")
                return None
                
        except git.InvalidGitRepositoryError:
            self.logger.error(f"Invalid Git repository: {repo_path}")
            return None
        except Exception as e:
            self.logger.error(f"Error parsing repository: {e}")
            return None
            
    def _get_active_branch(self, repo):
        """Get the active branch name"""
        try:
            return repo.active_branch.name
        except:
            return None
            
    def _get_branches(self, repo):
        """Get all branches in the repository"""
        return [branch.name for branch in repo.branches]
        
    def _get_recent_commits(self, repo, count=10):
        """Get recent commits"""
        commits = []
        for commit in list(repo.iter_commits())[:count]:
            commits.append({
                'hash': commit.hexsha,
                'message': commit.message,
                'author': commit.author.name,
                'date': commit.authored_datetime.isoformat()
            })
        return commits
        
    def _get_remotes(self, repo):
        """Get repository remotes"""
        return {remote.name: remote.url for remote in repo.remotes}
        
    def _get_files(self, repo_path):
        """Get all files in the repository"""
        files = []
        for path in Path(repo_path).rglob('*'):
            if path.is_file() and '.git' not in str(path):
                files.append({
                    'path': str(path.relative_to(repo_path)),
                    'size': path.stat().st_size,
                    'extension': path.suffix
                })
        return files
        
    def _get_submodules(self, repo):
        """Get repository submodules"""
        return [submodule.name for submodule in repo.submodules]
    
    # In git_parser.py, add a method to clone repositories
    def clone_repository(self, repo_url, target_dir=None):
        """Clone a remote repository to a local directory"""
        if target_dir is None:
            target_dir = os.path.join(self.config.get('storage_dir', 'repositories'), 
                                    os.path.basename(repo_url).replace('.git', ''))
        
        if not os.path.exists(target_dir):
            os.makedirs(os.path.dirname(target_dir), exist_ok=True)
            
        try:
            Repo.clone_from(repo_url, target_dir)
            return target_dir
        except Exception as e:
            self.logger.error(f"Error cloning repository: {e}")
            return None
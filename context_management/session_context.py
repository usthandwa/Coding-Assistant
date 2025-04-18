# CodingAssistant/context_management/session_context.py
import logging
import json
import os
from datetime import datetime
from pathlib import Path
import uuid

class SessionContextStore:
    """
    Stores and manages conversation context across sessions
    """
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.session_id = str(uuid.uuid4())
        self.context = {
            'session_id': self.session_id,
            'created_at': datetime.now().isoformat(),
            'interactions': [],
            'state': {},
            'active_files': [],
            'insights': []
        }
        self.storage_dir = Path(config.get('storage_dir', 'sessions'))
        os.makedirs(self.storage_dir, exist_ok=True)
        
    def update_context(self, query, response, metadata=None):
        """
        Update the session context with a new interaction
        
        Args:
            query (str): User query
            response (str): Agent response
            metadata (dict, optional): Additional metadata
            
        Returns:
            bool: Success
        """
        try:
            interaction = {
                'timestamp': datetime.now().isoformat(),
                'query': query,
                'response': response,
                'metadata': metadata or {}
            }
            
            self.context['interactions'].append(interaction)
            self.context['updated_at'] = datetime.now().isoformat()
            
            # Save context to disk
            self._save_context()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating session context: {e}")
            return False
            
    def get_relevant_context(self, query, max_interactions=5):
        """
        Get relevant context for a query
        
        Args:
            query (str): User query
            max_interactions (int, optional): Maximum number of interactions to include
            
        Returns:
            dict: Relevant context
        """
        try:
            # Basic implementation: just return most recent interactions
            recent_interactions = self.context['interactions'][-max_interactions:] if self.context['interactions'] else []
            
            # In a more sophisticated implementation, we would:
            # 1. Use vector embeddings to find semantically similar interactions
            # 2. Include relevant code snippets mentioned in those interactions
            # 3. Build a more structured context based on the query intent
            
            return {
                'recent_interactions': recent_interactions,
                'active_files': self.context['active_files'],
                'state': self.context['state']
            }
            
        except Exception as e:
            self.logger.error(f"Error retrieving relevant context: {e}")
            return {}
            
    def update_state(self, key, value):
        """
        Update the session state
        
        Args:
            key (str): State key
            value (any): State value
            
        Returns:
            bool: Success
        """
        try:
            self.context['state'][key] = value
            self.context['updated_at'] = datetime.now().isoformat()
            self._save_context()
            return True
        except Exception as e:
            self.logger.error(f"Error updating session state: {e}")
            return False
            
    def get_state(self, key=None):
        """
        Get session state
        
        Args:
            key (str, optional): State key. If None, returns all state
            
        Returns:
            any: State value or full state dict
        """
        if key is None:
            return self.context['state']
        return self.context['state'].get(key)
        
    def add_active_file(self, file_path, metadata=None):
        """
        Add an active file to the context
        
        Args:
            file_path (str): Path to the file
            metadata (dict, optional): Additional metadata
            
        Returns:
            bool: Success
        """
        try:
            file_info = {
                'path': file_path,
                'added_at': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            
            # Check if file is already in active files
            for existing in self.context['active_files']:
                if existing['path'] == file_path:
                    existing.update(file_info)
                    break
            else:
                self.context['active_files'].append(file_info)
                
            self.context['updated_at'] = datetime.now().isoformat()
            self._save_context()
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding active file: {e}")
            return False
            
    def add_insight(self, insight, source=None):
        """
        Add an insight to the context
        
        Args:
            insight (str): The insight text
            source (str, optional): Source of the insight
            
        Returns:
            bool: Success
        """
        try:
            insight_entry = {
                'text': insight,
                'source': source,
                'timestamp': datetime.now().isoformat()
            }
            
            self.context['insights'].append(insight_entry)
            self.context['updated_at'] = datetime.now().isoformat()
            self._save_context()
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding insight: {e}")
            return False
            
    def load_session(self, session_id):
        """
        Load a session from storage
        
        Args:
            session_id (str): Session ID
            
        Returns:
            bool: Success
        """
        try:
            session_path = self.storage_dir / f"{session_id}.json"
            
            if not session_path.exists():
                self.logger.warning(f"Session {session_id} not found")
                return False
                
            with open(session_path, 'r') as f:
                self.context = json.load(f)
                self.session_id = session_id
                
            self.logger.info(f"Loaded session {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading session {session_id}: {e}")
            return False
            
    def _save_context(self):
        """Save context to disk"""
        try:
            session_path = self.storage_dir / f"{self.session_id}.json"
            
            with open(session_path, 'w') as f:
                json.dump(self.context, f, indent=2)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving context: {e}")
            return False

### Enhanced Context Management
### This module provides an enhanced context management system for handling
### conversations, code analysis, and insights in a structured manner. It allows for  
### the addition of code sources, analysis results, conversation history, and insights,
### while ensuring that the context remains manageable and relevant to the user's queries.
class EnhancedContextManager:
    """Manages rich context across conversations and code analysis sessions"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.context = {
            'session_id': str(uuid.uuid4()),
            'created_at': datetime.now().isoformat(),
            'code_sources': [],
            'analyses': {},
            'conversation_history': [],
            'active_files': [],
            'code_explanations': {},
            'insights': []
        }
        
    def add_code_source(self, source_data):
        """Add a code source to the context"""
        source_id = str(uuid.uuid4())
        source_summary = {
            'id': source_id,
            'type': source_data['source_type'],
            'path': source_data['path'],
            'file_count': len(source_data['files']),
            'added_at': datetime.now().isoformat()
        }
        
        self.context['code_sources'].append(source_summary)
        
        # Store minimal file info to avoid bloating context
        files_summary = []
        for file in source_data['files']:
            files_summary.append({
                'path': file['path'],
                'language': file['language'],
                'size': file['size']
            })
            
        self.context['analyses'][source_id] = {
            'files': files_summary,
            'analyzed': False
        }
        
        return source_id
        
    def add_analysis_results(self, source_id, analysis_results):
        """Add analysis results for a code source"""
        if source_id not in self.context['analyses']:
            self.logger.warning(f"Unknown source ID: {source_id}")
            return False
            
        self.context['analyses'][source_id].update({
            'analyzed': True,
            'functions_count': len(analysis_results['functions']),
            'classes_count': len(analysis_results['classes']),
            'language_breakdown': analysis_results['language_breakdown']
        })
        
        # Store function and class summaries
        function_summaries = []
        for func in analysis_results['functions']:
            function_summaries.append({
                'name': func['name'],
                'file': func['file'],
                'language': func['language'],
                'signature': func.get('signature', '')
            })
            
        self.context['analyses'][source_id]['functions'] = function_summaries
        
        # Add insights
        for insight in analysis_results.get('insights', []):
            self.add_insight(insight, source_id)
            
        return True
        
    def add_conversation_interaction(self, query, response, metadata=None):
        """Add a conversation interaction to the context"""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'response': response,
            'metadata': metadata or {}
        }
        
        self.context['conversation_history'].append(interaction)
        return True
        
    def add_code_explanation(self, code_id, explanation):
        """Add a code explanation to the context"""
        self.context['code_explanations'][code_id] = {
            'created_at': datetime.now().isoformat(),
            'explanation': explanation
        }
        return True
        
    def add_insight(self, insight, source=None):
        """Add an insight to the context"""
        insight_entry = {
            'text': insight,
            'source': source,
            'timestamp': datetime.now().isoformat()
        }
        
        self.context['insights'].append(insight_entry)
        return True
        
    def get_relevant_context(self, query, code_entities=None):
        """Get context relevant to a query and code entities"""
        # Full context may be too large, so get relevant parts
        
        # Include recent conversation history
        recent_history = self.context['conversation_history'][-5:] if self.context['conversation_history'] else []
        
        # Find relevant code entities if provided
        relevant_functions = []
        relevant_classes = []
        
        if code_entities:
            for entity in code_entities:
                for source_id, analysis in self.context['analyses'].items():
                    if not analysis.get('analyzed', False):
                        continue
                        
                    # Look for matching functions
                    for func in analysis.get('functions', []):
                        if entity.lower() in func['name'].lower():
                            relevant_functions.append(func)
                            
                    # Look for matching classes (if we had stored them)
                    # Similar approach would apply
        
        # Include relevant insights
        relevant_insights = []
        for insight in self.context['insights']:
            if any(term in insight['text'].lower() for term in query.lower().split()):
                relevant_insights.append(insight)
        
        return {
            'recent_history': recent_history,
            'functions': relevant_functions,
            'classes': relevant_classes,
            'insights': relevant_insights
        }
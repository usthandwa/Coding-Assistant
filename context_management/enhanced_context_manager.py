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
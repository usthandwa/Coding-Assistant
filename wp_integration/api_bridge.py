# wp_integration/api_bridge.py
import logging
import json
import requests
from pathlib import Path
import os

class WordPressAPIBridge:
    """
    Bridge between AI Coding Agent and WordPress plugin
    """
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.base_url = config.get('wp_url', 'http://localhost/wordpress')
        self.api_endpoint = config.get('api_endpoint', '/wp-json/ai-coding-agent/v1')
        self.api_key = config.get('api_key', os.environ.get('WP_API_KEY', ''))
        
    def register_endpoints(self):
        """Register API endpoints for WordPress plugin"""
        endpoints = {
            'process_query': {
                'method': 'POST',
                'callback': self.process_query_callback
            },
            'get_repository_status': {
                'method': 'GET',
                'callback': self.get_repository_status_callback
            },
            'analyze_code': {
                'method': 'POST',
                'callback': self.analyze_code_callback
            }
        }
        
        return endpoints
        
    def process_query_callback(self, request):
        """Process a query from WordPress"""
        try:
            # Extract query from request
            query = request.get('query', '')
            session_id = request.get('session_id', '')
            repository = request.get('repository', '')
            
            if not query:
                return {
                    'success': False,
                    'message': 'Query is required'
                }
                
            # Create an instance of the AI Coding Agent
            from main import AICodingAgent
            from utils.config_utils import load_config
            
            config = load_config('config/default_config.yaml')
            
            # Initialize components (simplified for demonstration)
            from repository_integration.git_parser import GitParser
            from repository_integration.code_indexer import CodeIndexer
            from code_analysis.syntax_parser import SyntaxParser
            from code_analysis.semantic_analyzer import SemanticAnalyzer
            from context_management.session_context import SessionContextStore
            from context_management.code_context_graph import CodeContextGraph
            from reasoning.llm_interface import LLMInterface
            from reasoning.heuristics import HeuristicsEngine
            from interaction.query_processor import QueryProcessor
            from interaction.response_generator import ResponseGenerator
            
            git_parser = GitParser(config["repository_integration"])
            code_indexer = CodeIndexer(config["repository_integration"])
            syntax_parser = SyntaxParser(config["code_analysis"])
            semantic_analyzer = SemanticAnalyzer(config["code_analysis"])
            session_store = SessionContextStore(config["context_management"])
            code_graph = CodeContextGraph(config["context_management"])
            llm = LLMInterface(config["reasoning"])
            heuristics = HeuristicsEngine(config["reasoning"])
            query_processor = QueryProcessor(config["interaction"])
            response_generator = ResponseGenerator(config["interaction"])
            
            # Create agent
            agent = AICodingAgent(
                git_parser=git_parser,
                code_indexer=code_indexer,
                syntax_parser=syntax_parser,
                semantic_analyzer=semantic_analyzer,
                session_store=session_store,
                code_graph=code_graph,
                llm=llm,
                heuristics=heuristics,
                query_processor=query_processor,
                response_generator=response_generator,
                config=config
            )
            
            # Load existing session if provided
            if session_id:
                session_store.load_session(session_id)
                
            # Process repository if provided
            if repository:
                repo_path = Path(repository)
                if repo_path.exists():
                    agent.process_repository(repo_path)
                    
            # Process query
            processed_query = query_processor.process(query)
            
            # Get relevant context
            context = session_store.get_relevant_context(processed_query)
            code_context = code_graph.get_relevant_nodes(processed_query)
            
            # Generate response
            llm_response = llm.generate_response(
                query=processed_query,
                context=context,
                code_context=code_context
            )
            
            # Apply heuristics
            refined_response = heuristics.apply_heuristics(llm_response, code_context)
            
            # Format response
            formatted_response = response_generator.format_response(refined_response)
            
            # Update session context
            session_store.update_context(query, formatted_response)
            
            return {
                'success': True,
                'response': formatted_response,
                'session_id': session_store.session_id,
                'query_type': processed_query['type']
            }
        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            return {
                'success': False,
                'message': f"Error: {str(e)}"
            }
            
    def get_repository_status_callback(self, request):
        """Get repository status from WordPress"""
        try:
            repository = request.get('repository', '')
            
            if not repository:
                return {
                    'success': False,
                    'message': 'Repository path is required'
                }
                
            # Parse repository
            from repository_integration.git_parser import GitParser
            from utils.config_utils import load_config
            
            config = load_config('config/default_config.yaml')
            git_parser = GitParser(config["repository_integration"])
            
            repo_data = git_parser.parse_repository(repository)
            
            if not repo_data:
                return {
                    'success': False,
                    'message': 'Invalid repository or repository not found'
                }
                
            return {
                'success': True,
                'status': {
                    'active_branch': repo_data.get('active_branch'),
                    'branches': repo_data.get('branches'),
                    'files_count': len(repo_data.get('files', [])),
                    'remotes': repo_data.get('remotes'),
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting repository status: {e}")
            return {
                'success': False,
                'message': f"Error: {str(e)}"
            }
            
    def analyze_code_callback(self, request):
        """Analyze code from WordPress"""
        try:
            code = request.get('code', '')
            language = request.get('language', '')
            
            if not code:
                return {
                    'success': False,
                    'message': 'Code is required'
                }
                
            if not language:
                return {
                    'success': False,
                    'message': 'Language is required'
                }
                
            # Analyze code
            from reasoning.llm_interface import LLMInterface
            from utils.config_utils import load_config
            
            config = load_config('config/default_config.yaml')
            llm = LLMInterface(config["reasoning"])
            
            analysis = llm.analyze_code(code, language)
            
            return {
                'success': True,
                'analysis': analysis
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing code: {e}")
            return {
                'success': False,
                'message': f"Error: {str(e)}"
            }
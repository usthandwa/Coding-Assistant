import argparse
import logging
import os

from context_management.session_context import EnhancedContextManager
from interaction.query_processor import QueryProcessor
from interaction.response_generator import ResponseGenerator
from reasoning.heuristics import ExpertReasoning
from source_processing.code_source_scanner import CodeSourceScanner
from source_processing.enhanced_code_analyzer import EnhancedCodeAnalyzer
from utils.config_utils import load_config


class AICodingAssistant:
    """
    AI Coding Assistant with enhanced capabilities for explaining and analyzing code
    """
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.scanner = CodeSourceScanner(config)
        self.analyzer = EnhancedCodeAnalyzer(config)
        self.context_manager = EnhancedContextManager(config)
        self.expert_reasoning = ExpertReasoning(config)
        self.query_processor = QueryProcessor(config)
        self.response_generator = ResponseGenerator(config)
        
    def process_directory(self, dir_path, recursive=True):
        """Process a directory of code files"""
        self.logger.info(f"Processing directory: {dir_path}")
        
        try:
            # Scan the directory
            source_data = self.scanner.scan_directory(dir_path, recursive)
            
            # Add to context
            source_id = self.context_manager.add_code_source(source_data)
            
            # Analyze the code
            analysis_results = self.analyzer.analyze_code_source(source_data)
            
            # Store analysis results
            self.context_manager.add_analysis_results(source_id, analysis_results)
            
            return {
                'source_id': source_id,
                'files_count': len(source_data['files']),
                'functions_count': len(analysis_results['functions']),
                'classes_count': len(analysis_results['classes']),
                'language_breakdown': analysis_results['language_breakdown']
            }
            
        except Exception as e:
            self.logger.error(f"Error processing directory: {e}")
            return {
                'error': str(e)
            }
            
    def process_query(self, query):
        """Process a user query about code"""
        try:
            # Process the query
            processed_query = self.query_processor.process(query)
            
            # Get relevant context
            relevant_context = self.context_manager.get_relevant_context(
                query, 
                processed_query.get('entities', [])
            )
            
            response = None
            
            # Handle different query types
            if processed_query['type'] == 'code_explanation':
                # Extract the function or class to explain
                entity_name = self._extract_entity_from_query(processed_query)
                if entity_name:
                    # Try to find the function or class
                    function_data = self._find_function(entity_name, relevant_context)
                    if function_data:
                        explanation = self.analyzer.explain_function(entity_name, relevant_context)
                        response = self.response_generator.format_code_explanation(explanation)
                    else:
                        # If not found, look for class
                        class_data = self._find_class(entity_name, relevant_context)
                        if class_data:
                            explanation = self.analyzer.explain_class(entity_name, relevant_context)
                            response = self.response_generator.format_code_explanation(explanation)
            
            # If no specific handling, use expert reasoning
            if not response:
                # Determine which expert role to use
                role = self._determine_expert_role(processed_query)
                
                if role == 'senior_dev':
                    expert_response = self.expert_reasoning.analyze_as_senior_dev(
                        query, 
                        processed_query.get('language', 'general'),
                        relevant_context
                    )
                elif role == 'quality_expert':
                    expert_response = self.expert_reasoning.analyze_as_quality_expert(
                        query, 
                        processed_query.get('language', 'general'),
                        relevant_context
                    )
                elif role == 'tester':
                    expert_response = self.expert_reasoning.analyze_as_tester(
                        query, 
                        processed_query.get('language', 'general'),
                        relevant_context
                    )
                else:
                    # Default to general explanation
                    expert_response = self.expert_reasoning.explain_code(
                        query,
                        processed_query.get('language', 'general'),
                        "medium",
                        relevant_context
                    )
                    
                response = self.response_generator.format_expert_response(expert_response, role)
            
            # Store interaction in context
            self.context_manager.add_conversation_interaction(query, response)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            return {
                'content': f"I encountered an error while processing your query: {str(e)}",
                'error': str(e)
            }
            
    def _determine_expert_role(self, processed_query):
        """Determine which expert role to use based on the query"""
        query_lower = processed_query['raw_query'].lower()
        
        if any(term in query_lower for term in ['architecture', 'design', 'structure', 'review', 'senior']):
            return 'senior_dev'
            
        if any(term in query_lower for term in ['quality', 'best practice', 'style', 'improve', 'optimize']):
            return 'quality_expert'
            
        if any(term in query_lower for term in ['test', 'testing', 'cases', 'coverage', 'unit test']):
            return 'tester'
            
        # Default
        return 'explainer'
    # Missing methods for AICodingAssistant class

def _extract_entity_from_query(self, processed_query):
    """Extract function or class name from a query"""
    # Try to extract from entities list
    if 'entities' in processed_query and processed_query['entities']:
        for entity in processed_query['entities']:
            if entity.get('type') in ['function', 'class', 'method']:
                return entity.get('value')
    
    # Try regex extraction from raw query
    import re
    query = processed_query['raw_query'].lower()
    
    # Look for common patterns like "explain function X" or "how does class Y work"
    patterns = [
        r'(?:function|method|def)\s+([a-zA-Z0-9_]+)',
        r'(?:class)\s+([a-zA-Z0-9_]+)',
        r'(?:explain|tell me about|describe|how does)\s+([a-zA-Z0-9_]+)\s+(?:function|method|class|work)',
        r'what does\s+([a-zA-Z0-9_]+)\s+(?:do|function|method)',
        r'(?:explain|tell me about|describe)\s+([a-zA-Z0-9_]+)'
    ]
    
    for pattern in patterns:
        matches = re.search(pattern, query)
        if matches:
            return matches.group(1)
    
    # If code snippets exist, try to extract function/class names from them
    if 'code_snippets' in processed_query and processed_query['code_snippets']:
        for snippet in processed_query['code_snippets']:
            # Look for function definitions in the snippet
            func_matches = re.search(r'(?:function|def)\s+([a-zA-Z0-9_]+)', snippet['content'])
            if func_matches:
                return func_matches.group(1)
            
            # Look for class definitions in the snippet
            class_matches = re.search(r'class\s+([a-zA-Z0-9_]+)', snippet['content'])
            if class_matches:
                return class_matches.group(1)
    
    # No entity found
    return None

def _find_function(self, function_name, context):
    """Find function data from context"""
    # Case-insensitive search
    function_name_lower = function_name.lower()
    
    # Check in functions from all analyses
    for source_id, analysis in context.get('analyses', {}).items():
        if not analysis.get('functions'):
            continue
            
        for func in analysis['functions']:
            if func['name'].lower() == function_name_lower:
                return func
            
            # Check for partial matches (helpful for methods)
            if '.' in function_name_lower and function_name_lower.split('.')[-1] == func['name'].lower():
                return func
    
    # If no exact match, try fuzzy matching
    best_match = None
    best_score = 0
    
    for source_id, analysis in context.get('analyses', {}).items():
        if not analysis.get('functions'):
            continue
            
        for func in analysis['functions']:
            # Simple string similarity
            from difflib import SequenceMatcher
            similarity = SequenceMatcher(None, function_name_lower, func['name'].lower()).ratio()
            
            if similarity > 0.7 and similarity > best_score:  # 70% similarity threshold
                best_match = func
                best_score = similarity
    
    return best_match

def _find_class(self, class_name, context):
    """Find class data from context"""
    # Case-insensitive search
    class_name_lower = class_name.lower()
    
    # Check in classes from all analyses
    for source_id, analysis in context.get('analyses', {}).items():
        if not analysis.get('classes'):
            continue
            
        for cls in analysis['classes']:
            if cls['name'].lower() == class_name_lower:
                return cls
    
    # If no exact match, try fuzzy matching
    best_match = None
    best_score = 0
    
    for source_id, analysis in context.get('analyses', {}).items():
        if not analysis.get('classes'):
            continue
            
        for cls in analysis['classes']:
            # Simple string similarity
            from difflib import SequenceMatcher
            similarity = SequenceMatcher(None, class_name_lower, cls['name'].lower()).ratio()
            
            if similarity > 0.7 and similarity > best_score:  # 70% similarity threshold
                best_match = cls
                best_score = similarity
    
    return best_match
    
def main():
    parser = argparse.ArgumentParser(description="AI Coding Assistant")
    parser.add_argument("--dir", type=str, default=".", help="Directory to process (default: current directory)")
    parser.add_argument("--recursive", action="store_true", help="Process directory recursively")
    parser.add_argument("--config", type=str, default="config/default_config.yaml", help="Path to configuration file")
    parser.add_argument("--query", type=str, help="Direct query to process")
    parser.add_argument("--interactive", action="store_true", help="Start interactive mode")
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Create assistant
    assistant = AICodingAssistant(config)
    
    # Process directory
    dir_path = os.path.abspath(args.dir)
    print(f"Processing directory: {dir_path}")
    result = assistant.process_directory(dir_path, args.recursive)
    
    if 'error' in result:
        print(f"Error: {result['error']}")
        return
        
    print(f"Processed {result['files_count']} files containing {result['functions_count']} functions and {result['classes_count']} classes")
    
    # Print language breakdown
    if 'language_breakdown' in result:
        print("\nLanguage breakdown:")
        for lang, count in result['language_breakdown'].items():
            print(f"  {lang}: {count} files")
    
    # Process direct query if provided
    if args.query:
        print(f"\nProcessing query: {args.query}")
        response = assistant.process_query(args.query)
        print("\nResponse:")
        print(response['content'])
    
    # Start interactive mode if requested
    if args.interactive:
        print("\nStarting interactive mode. Type 'exit' to quit.")
        
        while True:
            try:
                query = input("\n> ")
                if query.lower() == 'exit':
                    break
                    
                response = assistant.process_query(query)
                print(response['content'])
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")    
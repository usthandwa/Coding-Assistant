# ai_coding_agent/interaction/query_processor.py
import logging
import re
from enum import Enum

class QueryType(Enum):
    REPOSITORY = 'repository'
    DEBUGGING = 'debugging'
    CODE_REVIEW = 'code_review'
    CODE_SUGGESTION = 'code_suggestion'
    EXPLANATION = 'explanation'
    GENERAL = 'general'

class QueryProcessor:
    """
    Processes and categorizes user queries
    """
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def process(self, query):
        """
        Process a user query
        
        Args:
            query (str): Raw user query
            
        Returns:
            dict: Processed query information
        """
        # Fix for the logging issue - safely convert query to string and truncate
        query_str = str(query) if query is not None else ""
        log_preview = query_str[:50] + "..." if len(query_str) > 50 else query_str
        self.logger.info(f"Processing query: {log_preview}")
        
        try:
             # Safely log without any slicing operations
            self.logger.info(f"Processing query (length: {len(str(query) if query is not None else '')})")
            
            # Ensure query is a string
            if not isinstance(query, str):
                query = str(query) if query is not None else ""
                
            # Determine query type
            query_type = self._determine_query_type(query)
            
            # Extract mentioned entities
            entities = self._extract_entities(query)
            
            # Extract code snippets
            code_snippets = self._extract_code_snippets(query)
            
            # Determine language if applicable
            language = self._determine_language(query, code_snippets)
            
            # Process query based on type
            processed_query = self._process_by_type(query, query_type)
            
            return {
                'raw_query': query,
                'processed_query': processed_query,
                'type': query_type,
                'entities': entities,
                'code_snippets': code_snippets,
                'language': language
            }
        
        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            return {
                'raw_query': query,
                'type': QueryType.GENERAL.value,
                'error': str(e)
            }
              
    def _determine_query_type(self, query):
        """Determine the type of query"""
        self.logger.info(f"Processing query: \"Determining the type of query\"")
        query_lower = query.lower()
        
        if re.search(r'(repository|repo|git|clone|upload|download)', query_lower):
            return QueryType.REPOSITORY.value
            
        if re.search(r'(debug|error|fix|issue|problem|not working|fails|exception)', query_lower):
            return QueryType.DEBUGGING.value
            
        if re.search(r'(review|improve|better|optimize|refactor)', query_lower):
            return QueryType.CODE_REVIEW.value
            
        if re.search(r'(suggestion|recommend|suggest|how to implement|how to write)', query_lower):
            return QueryType.CODE_SUGGESTION.value
            
        if re.search(r'(explain|what does|how does|what is|mean)', query_lower):
            return QueryType.EXPLANATION.value
            
        return QueryType.GENERAL.value
        
    def _extract_entities(self, query):
        """Extract mentioned entities from query"""
        entities = []
        
        # Extract file paths
        file_paths = re.findall(r'(\b[\/\\]?[a-zA-Z0-9_-]+[\/\\][a-zA-Z0-9_\-\.\/\\]+\b)', query)
        for path in file_paths:
            entities.append({'type': 'file_path', 'value': path})
            
        # Extract class names (CamelCase)
        class_names = re.findall(r'\b([A-Z][a-zA-Z0-9]*)\b', query)
        for class_name in class_names:
            entities.append({'type': 'class', 'value': class_name})
            
        # Extract function/method names
        function_names = re.findall(r'\b([a-zA-Z0-9_]+)\(\)', query)
        for function_name in function_names:
            entities.append({'type': 'function', 'value': function_name})
            
        # Extract variables (some heuristics)
        variable_names = re.findall(r'\b(var|let|const|self\.|this\.)\s+([a-zA-Z0-9_]+)\b', query)
        for _, variable_name in variable_names:
            entities.append({'type': 'variable', 'value': variable_name})
            
        return entities
        
    def _extract_code_snippets(self, query):
        """Extract code snippets from query"""
        snippets = []
        
        # Extract code blocks with backticks
        code_blocks = re.findall(r'```(?:\w+)?\s*([\s\S]*?)\s*```', query)
        for i, block in enumerate(code_blocks):
            snippets.append({
                'id': f'snippet_{i+1}',
                'content': block,
                'type': 'block'
            })
            
        # Extract inline code
        inline_code = re.findall(r'`([^`]+)`', query)
        for i, code in enumerate(inline_code):
            snippets.append({
                'id': f'inline_{i+1}',
                'content': code,
                'type': 'inline'
            })
            
        return snippets
        
    def _determine_language(self, query, code_snippets):
        """Determine programming language from query and snippets"""
        query_lower = query.lower()
        
        # Check if language is explicitly mentioned
        language_patterns = {
            'python': r'\b(python|py)\b',
            'javascript': r'\b(javascript|js)\b',
            'typescript': r'\b(typescript|ts)\b',
            'java': r'\b(java)\b',
            'c#': r'\b(c#|csharp|c-sharp)\b',
            'c++': r'\b(c\+\+|cpp)\b',
            'go': r'\b(go|golang)\b',
            'rust': r'\b(rust)\b',
            'php': r'\b(php)\b',
            'ruby': r'\b(ruby|rb)\b'
        }
        
        for language, pattern in language_patterns.items():
            if re.search(pattern, query_lower):
                return language
                
        # Check code block language specification
        code_block_lang = re.search(r'```(\w+)', query)
        if code_block_lang:
            lang = code_block_lang.group(1).lower()
            if lang in language_patterns:
                return lang
            if lang == 'py':
                return 'python'
            if lang == 'js':
                return 'javascript'
            if lang == 'ts':
                return 'typescript'
                
        # Analyze code snippets for language hints
        for snippet in code_snippets:
            content = snippet['content']
            
            # Python indicators
            if re.search(r'def\s+\w+\s*\(.*\):|\bimport\s+\w+|from\s+\w+\s+import', content):
                return 'python'
                
            # JavaScript/TypeScript indicators
            if re.search(r'function\s+\w+\s*\(.*\)|const|let|var|=>|import\s+.*\s+from', content):
                if re.search(r':\s*(\w+)\b', content):  # Type annotations
                    return 'typescript'
                return 'javascript'
                
            # Java indicators
            if re.search(r'public\s+class|private|protected|System\.out\.println', content):
                return 'java'
                
            # C# indicators
            if re.search(r'namespace|using\s+\w+;|Console\.WriteLine', content):
                return 'c#'
                
        return None
        
    def _process_by_type(self, query, query_type):
        """Process query based on its type"""
        if query_type == QueryType.DEBUGGING.value:
            return self._process_debugging_query(query)
            
        if query_type == QueryType.CODE_REVIEW.value:
            return self._process_code_review_query(query)
            
        if query_type == QueryType.CODE_SUGGESTION.value:
            return self._process_code_suggestion_query(query)
            
        if query_type == QueryType.EXPLANATION.value:
            return self._process_explanation_query(query)
            
        # Default processing for other types
        return query
        
    def _process_debugging_query(self, query):
        """Process debugging query"""
        # Extract error messages
        error_messages = re.findall(r'Error: (.*?)(?:\n|$)', query)
        
        # Add some context for debugging
        if error_messages:
            return f"{query}\n[Detected error message: {error_messages[0]}]"
            
        return query
        
    def _process_code_review_query(self, query):
        """Process code review query"""
        # Could add some context or structure here
        return query
        
    def _process_code_suggestion_query(self, query):
        """Process code suggestion query"""
        # Could add some context or structure here
        return query
        
    def _process_explanation_query(self, query):
        """Process explanation query"""
        # Could add some context or structure here
        return query

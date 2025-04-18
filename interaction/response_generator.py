# ai_coding_agent/interaction/response_generator.py
import logging
import re
import json
from typing import Dict, Any

class ResponseGenerator:
    """
    Generates formatted responses for different query types
    """
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def format_response(self, llm_response: Dict[str, Any]) -> str:
        """
        Format LLM response for presentation
        
        Args:
            llm_response (dict): Response from LLM
            
        Returns:
            str: Formatted response
        """
        if not llm_response:
            return "I couldn't generate a response. Please try again."
            
        content = llm_response.get('content', '')
        
        if 'error' in llm_response:
            return f"Error: {llm_response['error']}"
            
        # Format code blocks with syntax highlighting
        content = self._format_code_blocks(content)
        
        # Add section headers if needed
        content = self._add_section_headers(content)
        
        # Format lists
        content = self._format_lists(content)
        
        # Add citations if applicable
        content = self._add_citations(content)
        
        return content
        
    def _format_code_blocks(self, content: str) -> str:
        """Format code blocks with syntax highlighting"""
        # Find code blocks with no language specified
        pattern = r'```(\s*\n[\s\S]*?\n\s*)```'
        
        def add_language(match):
            code_block = match.group(1)
            
            # Try to detect language
            language = self._detect_code_language(code_block)
            
            # Add language to code block
            return f"```{language}{code_block}```"
            
        # Replace code blocks with no language
        content = re.sub(pattern, add_language, content)
        
        return content
        
    def _detect_code_language(self, code_block: str) -> str:
        """Detect language of a code block"""
        # Simple heuristics for language detection
        if re.search(r'def\s+\w+\s*\(.*\):|import\s+\w+|from\s+\w+\s+import', code_block):
            return 'python'
        if re.search(r'function\s+\w+\s*\(.*\)|const|let|var|=>|import\s+.*\s+from', code_block):
            if re.search(r':\s*(\w+)\b', code_block):  # Type annotations
                return 'typescript'
            return 'javascript'
        if re.search(r'public\s+class|private|protected|System\.out\.println', code_block):
            return 'java'
        if re.search(r'namespace|using\s+\w+;|Console\.WriteLine', code_block):
            return 'csharp'
        if re.search(r'#include|printf|malloc|free|scanf', code_block):
            return 'c'
        if re.search(r'#include|std::|cout|cin|vector<', code_block):
            return 'cpp'
            
        # Default to plain text if can't detect
        return ''
        
    def _add_section_headers(self, content: str) -> str:
        """Add section headers to content if needed"""
        # Check if content is long and might benefit from sections
        if len(content) > 500 and not re.search(r'^#\s+\w+', content, re.MULTILINE):
            lines = content.split('\n')
            
            # Add a title if not present
            if not lines[0].startswith('#'):
                content = f"# Response\n\n{content}"
                
        return content
        
    def _format_lists(self, content: str) -> str:
        """Format lists in content"""
        # Ensure numbered lists have proper spacing
        content = re.sub(r'(\d+)\.\s*(\w)', r'\1. \2', content)
        
        # Ensure bullet lists have proper spacing
        content = re.sub(r'(\*|-)\s*(\w)', r'\1 \2', content)
        
        return content
        
    def _add_citations(self, content: str) -> str:
        """Add citations to content if applicable"""
        # This would typically link to specific files or documentation
        # For demonstration, we'll just return the content unchanged
        return content
        
    def format_error_response(self, error: str) -> str:
        """
        Format error response
        
        Args:
            error (str): Error message
            
        Returns:
            str: Formatted error response
        """
        return f"""# Error Occurred

I encountered an error while processing your request:

```
{error}
```

Please try again or modify your request. If the problem persists, check your repository structure or provide more details."""
        
    def format_debug_suggestion(self, debug_info: Dict[str, Any]) -> str:
        """
        Format debugging suggestion
        
        Args:
            debug_info (dict): Debugging information
            
        Returns:
            str: Formatted debugging suggestion
        """
        if not debug_info:
            return "I couldn't generate debugging suggestions. Please provide more context or error details."
            
        error_message = debug_info.get('error_message', 'Unknown error')
        possible_causes = debug_info.get('possible_causes', [])
        suggested_fixes = debug_info.get('suggested_fixes', [])
        code_snippet = debug_info.get('code_snippet', '')
        
        response = f"""# Debugging Suggestion

## Error
```
{error_message}
```

## Possible Causes
"""
        
        for i, cause in enumerate(possible_causes, 1):
            response += f"{i}. {cause}\n"
            
        response += "\n## Suggested Fixes\n"
        
        for i, fix in enumerate(suggested_fixes, 1):
            response += f"{i}. {fix}\n"
            
        if code_snippet:
            language = debug_info.get('language', '')
            response += f"\n## Fixed Code Example\n```{language}\n{code_snippet}\n```"
            
        return response
        
    def format_code_review(self, review_info: Dict[str, Any]) -> str:
        """
        Format code review response
        
        Args:
            review_info (dict): Code review information
            
        Returns:
            str: Formatted code review
        """
        if not review_info:
            return "I couldn't generate a code review. Please provide the code you want reviewed."
            
        code_quality = review_info.get('code_quality', 'Unknown')
        issues = review_info.get('issues', [])
        strengths = review_info.get('strengths', [])
        suggestions = review_info.get('suggestions', [])
        
        response = f"""# Code Review

## Overall Quality
{code_quality}

## Strengths
"""
        
        for i, strength in enumerate(strengths, 1):
            response += f"{i}. {strength}\n"
            
        response += "\n## Issues\n"
        
        for i, issue in enumerate(issues, 1):
            response += f"{i}. {issue}\n"
            
        response += "\n## Suggestions for Improvement\n"
        
        for i, suggestion in enumerate(suggestions, 1):
            response += f"{i}. {suggestion}\n"
            
        return response

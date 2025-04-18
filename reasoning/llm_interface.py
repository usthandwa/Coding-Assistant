# CodingAssistant/reasoning/llm_interface.py
import logging
import os
import json
import pprint
import requests
from typing import Dict, List, Any, Optional

class LLMInterface:
    """
    Interface for Large Language Model API to provide reasoning capabilities
    """
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.api_key = config.get('api_key', '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')
        self.model = config.get('model', 'deepseek-r1-distill-llama-32b')
        self.max_tokens = config.get('max_tokens', 4000)
        self.temperature = config.get('temperature', 0.25)
        self.api_url = config.get('api_url', 'https://api.groq.com/openai/v1/chat/completions')
        
    def generate_response(self, query: str, context: Dict[str, Any], code_context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a response using the LLM
        
        Args:
            query (str): User query
            context (dict): Session context
            code_context (list): Code context nodes
            
        Returns:
            dict: Response from LLM
        """
        query_str = pprint.pformat(query)
        self.logger.info(f"Generating response for query: {str(query_str)[:100]}...")
        
        try:
            # Prepare the prompt with context
            prompt = self._build_prompt(query_str, context, code_context)
            
            # Call the LLM API
            response = self._call_api(prompt, query_str)
            
            # Process the response
            processed_response = self._process_response(response)
            
            return processed_response
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return {
                'content': f"I encountered an error while processing your request: {str(e)}",
                'error': str(e)
            }
            
    def _build_prompt(self, query: str, context: Dict[str, Any], code_context: List[Dict[str, Any]]) -> str:
        """Build a prompt with context"""
        # Include recent interactions
        recent_interactions = ""
        if 'recent_interactions' in context:
            for interaction in context['recent_interactions']:
                recent_interactions += f"User: {interaction['query']}\nAssistant: {interaction['response']}\n\n"
                
        # Include code context
        code_context_str = ""
        if code_context:
            code_context_str = "Relevant code entities:\n"
            for node in code_context:
                node_id, data = node
                node_type = data.get('type', 'unknown')
                path = data.get('path', 'unknown')
                
                code_context_str += f"- {node_type}: {node_id} (path: {path})\n"
                
        # Build system prompt
        system_prompt = f"""You are an AI coding agent that assists with coding tasks. 
            You have the following context about the repository and recent interactions:

            {recent_interactions}

            {code_context_str}

            Answer the user's query based on this context. If you need more information or context, 
            ask clarifying questions. If you provide code solutions, ensure they follow best practices 
            and are well-commented.
            """
        
        return system_prompt
        
    def _call_api(self, prompt: str, query: str) -> Dict[str, Any]:
        """Call the LLM API with improved error handling"""
        if not self.api_key:
            self.logger.warning("No API key provided for LLM")
            return {
                'content': "I can't access the language model API without an API key. Please configure the API key in settings."
            }
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                'model': self.model,
                'messages': [
                    {'role': 'system', 'content': prompt},
                    {'role': 'user', 'content': query}
                ],
                'max_tokens': self.max_tokens,
                'temperature': self.temperature
            }
            
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
                
        except requests.exceptions.HTTPError as e:
            if hasattr(e, 'response') and e.response.status_code == 503:
                self.logger.error(f"API service unavailable: {e}")
                return {
                    'content': "The language model service is currently unavailable. Please try again later.",
                    'error': f"Service unavailable: {str(e)}"
                }
            self.logger.error(f"API HTTP error: {e}")
            return {
                'content': f"There was an HTTP error communicating with the language model API: {str(e)}",
                'error': str(e)
            }
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"API connection error: {e}")
            return {
                'content': "Could not connect to the language model API. Please check your internet connection.",
                'error': str(e)
            }
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request error: {e}")
            return {
                'content': f"There was an error communicating with the language model API: {str(e)}",
                'error': str(e)
            }
          
    def _process_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Process the API response from Groq"""
        try:
            # Extract content from Groq API response structure
            if 'choices' in response and len(response['choices']) > 0:
                content = response['choices'][0]['message']['content']
            else:
                content = response.get('content', '')
                if not content:
                    self.logger.warning(f"Unexpected API response structure: {response}")
                    content = "I received an unexpected response format from the API."
            
            # Add metadata to the response
            processed_response = {
                'content': content,
                'model': self.model,
                'timestamp': '2025-04-01T12:00:00Z'  # Would be actual timestamp in real implementation
            }
            
            return processed_response
        except Exception as e:
            self.logger.error(f"Error processing API response: {e}")
            return {
                'content': "I encountered an error while processing the API response.",
                'error': str(e)
            }
        
    def analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """
        Analyze code using the LLM
        
        Args:
            code (str): Code to analyze
            language (str): Programming language
            
        Returns:
            dict: Analysis results
        """
        try:
            prompt = f"""Analyze the following {language} code and provide insights:
                        ```{language}
                        {code}
                        ```

                        Please identify:
                        1. Potential bugs or issues
                        2. Performance optimizations
                        3. Readability improvements
                        4. Security concerns
                        5. Best practices violations

                        Return your analysis in a structured format."""
            
            response = self._call_api(prompt, code)
            return response
            
        except Exception as e:
            self.logger.error(f"Error analyzing code: {e}")
            return {
                'content': f"I encountered an error while analyzing the code: {str(e)}",
                'error': str(e)
            }
            
    def suggest_code_improvements(self, code: str, language: str) -> Dict[str, Any]:
        """
        Suggest improvements for code
        
        Args:
            code (str): Code to improve
            language (str): Programming language
            
        Returns:
            dict: Suggested improvements
        """
        try:
            prompt = f"""Suggest improvements for the following {language} code:

                        ```{language}
                        {code}
                        ```

                        Provide specific suggestions for:
                        1. Code structure
                        2. Performance
                        3. Readability
                        4. Error handling
                        5. Following best practices

                        For each suggestion, show both the original code and the improved version."""
            
            response = self._call_api(prompt, code)
            return response
            
        except Exception as e:
            self.logger.error(f"Error suggesting code improvements: {e}")
            return {
                'content': f"I encountered an error while suggesting improvements: {str(e)}",
                'error': str(e)
            }
        
    def _call_llm_with_role(self, role, query, code=None, language=None, context=None):
        """Call LLM with a specific expert role"""
        
        role_prompts = {
            'senior_dev': """You are a Senior Software Developer with 15+ years of experience in {language}.
                        Analyze this code from an architectural and design perspective. Focus on:
                        - Overall design patterns and architecture
                        - Code organization and structure
                        - Potential improvements to the design
                        - Edge cases and potential bugs
                        - Performance considerations""",
                        
            'quality_expert': """You are a Code Quality Expert who specializes in {language} best practices.
                            Review this code for quality issues. Focus on:
                            - Adherence to {language} conventions
                            - Clean code principles (SOLID, DRY, etc.)
                            - Consistent style and formatting
                            - Proper error handling
                            - Documentation quality""",
                            
            'tester': """You are a Software Testing Expert with deep knowledge of testing {language} applications.
                    Analyze this code for testability and suggest test cases. Focus on:
                    - Unit testing approach
                    - Key test cases needed (provide examples)
                    - Edge cases that should be tested
                    - Mocking requirements
                    - Integration testing considerations""",
                    
            'explainer': """You are a Code Educator who excels at explaining code clearly to developers.
                        Explain this {language} code in detail. Focus on:
                        - The overall purpose and functionality
                        - How each part works and why it's designed that way
                        - The algorithm or approach used
                        - Any notable techniques or patterns
                        - How the code fits into the larger system"""
        }
        
        # Select the appropriate role prompt
        role_prompt = role_prompts.get(role, role_prompts['explainer'])
        role_prompt = role_prompt.format(language=language or 'programming')
        
        # Build the full prompt
        if code:
            full_prompt = f"{role_prompt}\n\nAnalyze this code:\n```{language or ''}\n{code}\n```\n\n{query}"
        else:
            full_prompt = f"{role_prompt}\n\n{query}"
        
        # Call LLM with the prompt
        return self.llm.generate_response(full_prompt, context or {}, [])
# ai_coding_agent/reasoning/heuristics.py

import logging
import os
import re
from typing import Dict, List, Any, Pattern, Callable, Match, Optional
import json

from reasoning.llm_interface import LLMInterface

class HeuristicsEngine:
    """
    Applies heuristic rules to refine and enhance LLM responses
    """
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.programming_languages = {
            'python': ['.py'],
            'javascript': ['.js', '.jsx'],
            'typescript': ['.ts', '.tsx'],
            'java': ['.java'],
            'csharp': ['.cs'],
            'go': ['.go'],
            'rust': ['.rs'],
            'cpp': ['.cpp', '.hpp', '.cc', '.hh'],
            'c': ['.c', '.h'],
            'php': ['.php'],
            'ruby': ['.rb']
        }
        self._load_heuristics()
        
    def _load_heuristics(self):
        """Load heuristics rules"""
        self.heuristics = {
            'general': self._general_heuristics(),
            'language_specific': self._language_specific_heuristics(),
            'formatting': self._formatting_heuristics(),
            'context': self._context_heuristics(),
            'windows_specific': self._windows_specific_heuristics()
        }
        
    def apply_heuristics(self, llm_response: Dict[str, Any], code_context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Apply heuristics to refine LLM response
        
        Args:
            llm_response (dict): Response from LLM
            code_context (list): Code context nodes
            
        Returns:
            dict: Refined response
        """
        self.logger.info("Applying heuristics to LLM response")
        
        try:
            if not llm_response:
                return llm_response
                
            content = llm_response.get('content', '')
            if not content:
                return llm_response
                
            original_content = content
            applied_rules = []
            
            # Apply general heuristics
            content, gen_rules = self._apply_general_heuristics(content)
            applied_rules.extend(gen_rules)
            
            # Detect languages in the content
            languages = self._detect_languages(content)
            
            # Apply language-specific heuristics
            content, lang_rules = self._apply_language_specific_heuristics(content, languages)
            applied_rules.extend(lang_rules)
            
            # Apply formatting heuristics
            content, fmt_rules = self._apply_formatting_heuristics(content)
            applied_rules.extend(fmt_rules)
            
            # Apply Windows-specific heuristics
            content, win_rules = self._apply_windows_specific_heuristics(content)
            applied_rules.extend(win_rules)
            
            # Apply context-aware heuristics
            content, ctx_rules = self._apply_context_heuristics(content, code_context)
            applied_rules.extend(ctx_rules)
            
            # Update the response
            llm_response['content'] = content
            llm_response['heuristics_applied'] = True
            llm_response['heuristics_rules_applied'] = applied_rules
            
            # Only log changes if content was modified
            if content != original_content:
                self.logger.info(f"Applied {len(applied_rules)} heuristic rules")
                for rule in applied_rules:
                    self.logger.debug(f"Applied rule: {rule}")
            else:
                self.logger.info("No heuristic rules applied (content unchanged)")
            
            return llm_response
            
        except Exception as e:
            self.logger.error(f"Error applying heuristics: {e}")
            return llm_response
            
    def _general_heuristics(self):
        """Define general heuristics"""
        return [
            # Remove uncertainty language
            {
                'pattern': r'(?:^|\s)(I think|I believe|Maybe|Perhaps|Probably)(\s+)',
                'replacement': r'\2',
                'description': 'Remove uncertainty phrases'
            },
            # Ensure code blocks have syntax highlighting
            {
                'pattern': r'```(\s*\n[\s\S]*?\n\s*)```',
                'replacement': r'```python\1```',
                'description': 'Add language to code blocks'
            },
            # Improve heading spacing
            {
                'pattern': r'(#+)([A-Za-z0-9])',
                'replacement': r'\1 \2',
                'description': 'Add space after heading markers'
            },
            # Fix common inconsistencies
            {
                'pattern': r'\b(vs|VS)\.?\s',
                'replacement': r'vs. ',
                'description': 'Standardize vs. abbreviation'
            },
            # Fix quotes
            {
                'pattern': r'(\w)"(\w)',
                'replacement': r"\1'\2",
                'description': 'Replace double quotes with single quotes for contractions'
            }
        ]
        
    def _language_specific_heuristics(self):
        """Define language-specific heuristics"""
        return {
            'python': [
                # Ensure proper Python imports
                {
                    'pattern': r'import\s+([A-Za-z0-9_]+)\.([A-Za-z0-9_]+)',
                    'replacement': r'from \1 import \2',
                    'description': 'Convert import x.y to from x import y'
                },
                # Fix common Python indentation issues in examples
                {
                    'pattern': r'(\s*)def\s+\w+\(.*\):(.*?)(?:\n\1)([^\s])',
                    'replacement': r'\1def function():\2\n\1    \3',
                    'description': 'Fix Python function indentation'
                },
                # Add docstrings to function examples that don't have them
                {
                    'pattern': r'(def\s+\w+\(.*\):)\s*\n(\s+)(?![\'"])',
                    'replacement': r'\1\n\2"""\n\2Description\n\2"""\n\2',
                    'description': 'Add docstrings to functions'
                },
                # Fix Python list comprehension spacing
                {
                    'pattern': r'\[\s*([^[\]]+?)\s+for\s+',
                    'replacement': r'[\1 for ',
                    'description': 'Fix list comprehension spacing'
                }
            ],
            'javascript': [
                # Ensure semicolons at line ends in JavaScript code blocks
                {
                    'pattern': r'```javascript[\s\S]*?(?<![;{}\[\]])(\n)(?![\s})\];])(?!```)',
                    'replacement': r';\1',
                    'description': 'Add semicolons to line ends in JavaScript'
                },
                # Fix arrow function spacing
                {
                    'pattern': r'(\(.*?\))\s*=>\s*{',
                    'replacement': r'\1 => {',
                    'description': 'Standardize arrow function spacing'
                },
                # Fix inconsistent quote usage
                {
                    'pattern': r'(const|let|var)\s+(\w+)\s*=\s*"([^"]*?")',
                    'replacement': r"\1 \2 = '\3",
                    'description': 'Use consistent quotes (single) in JavaScript'
                }
            ],
            'java': [
                # Fix Java bracing style
                {
                    'pattern': r'(\)\s*)\n(\s*{)',
                    'replacement': r'\1{\n',
                    'description': 'Fix Java bracing style'
                },
                # Ensure proper access modifiers
                {
                    'pattern': r'(class\s+\w+)\s*{',
                    'replacement': r'public \1 {',
                    'description': 'Add missing public access modifier to classes'
                }
            ],
            'csharp': [
                # Fix C# naming conventions for methods
                {
                    'pattern': r'(public|private|protected|internal)?\s*(\w+)\s+(\w)(\w+)\s*\(',
                    'replacement': lambda m: f"{m.group(1) or 'public'} {m.group(2)} {m.group(3).upper()}{m.group(4)}(",
                    'description': 'Fix C# method naming (PascalCase)'
                }
            ],
            'go': [
                # Ensure proper Go error checking
                {
                    'pattern': r'(\w+),\s*(\w+)\s*:=\s*.+[^{]\n(?!\s*if\s+\2\s*!=\s*nil)',
                    'replacement': r'\1, \2 := ...\n    if \2 != nil {\n        return ...\n    }\n',
                    'description': 'Add Go error checking'
                }
            ]
        }
        
    def _formatting_heuristics(self):
        """Define formatting heuristics"""
        return [
            # Fix list formatting
            {
                'pattern': r'([0-9]+)\.([^\n])',
                'replacement': r'\1. \2',
                'description': 'Add space after list numbers'
            },
            # Fix bullet points
            {
                'pattern': r'(\n\s*)[-*]([^\s])',
                'replacement': r'\1- \2',
                'description': 'Add space after bullet points'
            },
            # Fix table formatting
            {
                'pattern': r'\|([^\|\n]+)\|([^\|\n]+)\|',
                'replacement': r'| \1 | \2 |',
                'description': 'Add spaces in table cells'
            },
            # Fix code block syntax (separate code blocks with blank lines)
            {
                'pattern': r'```\n([\s\S]*?)```\n([^`\n])',
                'replacement': r'```\n\1```\n\n\2',
                'description': 'Add blank line after code blocks'
            }
        ]
        
    def _windows_specific_heuristics(self):
        """Define Windows-specific heuristics"""
        return [
            # Fix Windows path separators
            {
                'pattern': r'(?<![\\`\'"])(\/[\w\.]+)+(?![\\`\'"])',
                'replacement': lambda m: m.group(0).replace('/', '\\'),
                'description': 'Convert forward slashes to backslashes in Windows paths'
            },
            # Fix Windows path format in code blocks
            {
                'pattern': r'(?<=```\w*\n)([^`]+?)(?:[\'"])([A-Za-z]:(?:/[^\'"\n]+)+)(?:[\'"])',
                'replacement': lambda m: m.group(1) + '"' + m.group(2).replace('/', '\\\\') + '"',
                'description': 'Fix Windows path format in code blocks'
            },
            # Fix Windows path escaping in strings
            {
                'pattern': r'"([A-Za-z]:\\[^"]+)"',
                'replacement': lambda m: '"' + m.group(1).replace('\\', '\\\\') + '"',
                'description': 'Fix Windows path escaping in strings'
            },
            # Fix Windows environment variables
            {
                'pattern': r'(%\w+%)',
                'replacement': r'%\1%',
                'description': 'Fix Windows environment variables'
            },
            # Fix Windows command syntax
            {
                'pattern': r'(cmd\.exe\s*/c\s+)([^"\n]+?\s)(\s*)',
                'replacement': r'\1"\2"\3',
                'description': 'Quote Windows command arguments'
            }
        ]
        
    def _context_heuristics(self):
        """Define context-aware heuristics"""
        return [
            # Replace generic names with context-specific names
            {
                'pattern': r'\b(myFunction|doSomething|process|handler)\b',
                'replacement': lambda m, context: self._get_context_specific_name(m.group(0), context),
                'description': 'Replace generic function names with context-specific ones'
            },
            # Add repository-specific references
            {
                'pattern': r'\b(in\s+the\s+codebase|in\s+your\s+project)\b',
                'replacement': lambda m, context: self._get_specific_reference(m.group(0), context),
                'description': 'Add repository-specific references'
            }
        ]
        
    def _apply_general_heuristics(self, content):
        """Apply general heuristics"""
        applied_rules = []
        for rule in self.heuristics['general']:
            pattern = rule['pattern']
            replacement = rule['replacement']
            original = content
            
            try:
                content = re.sub(pattern, replacement, content)
                if content != original:
                    applied_rules.append(rule['description'])
            except Exception as e:
                self.logger.error(f"Error applying general heuristic {rule['description']}: {e}")
                
        return content, applied_rules
        
    def _apply_language_specific_heuristics(self, content, languages):
        """Apply language-specific heuristics"""
        applied_rules = []
        
        for language in languages:
            if language in self.heuristics['language_specific']:
                language_rules = self.heuristics['language_specific'][language]
                for rule in language_rules:
                    pattern = rule['pattern']
                    replacement = rule['replacement']
                    original = content
                    
                    try:
                        # Handle both string and callable replacements
                        if callable(replacement):
                            # Create a replacement function that doesn't need context
                            def replace_func(match):
                                return replacement(match)
                            content = re.sub(pattern, replace_func, content)
                        else:
                            content = re.sub(pattern, replacement, content)
                            
                        if content != original:
                            applied_rules.append(f"{language}: {rule['description']}")
                    except Exception as e:
                        self.logger.error(f"Error applying {language} heuristic {rule['description']}: {e}")
                    
        return content, applied_rules
        
    def _apply_formatting_heuristics(self, content):
        """Apply formatting heuristics"""
        applied_rules = []
        for rule in self.heuristics['formatting']:
            pattern = rule['pattern']
            replacement = rule['replacement']
            original = content
            
            try:
                content = re.sub(pattern, replacement, content)
                if content != original:
                    applied_rules.append(rule['description'])
            except Exception as e:
                self.logger.error(f"Error applying formatting heuristic {rule['description']}: {e}")
                
        return content, applied_rules
        
    def _apply_windows_specific_heuristics(self, content):
        """Apply Windows-specific heuristics"""
        applied_rules = []
        for rule in self.heuristics['windows_specific']:
            pattern = rule['pattern']
            replacement = rule['replacement']
            original = content
            
            try:
                if callable(replacement):
                    # For callable replacements
                    content = re.sub(pattern, replacement, content)
                else:
                    content = re.sub(pattern, replacement, content)
                    
                if content != original:
                    applied_rules.append(rule['description'])
            except Exception as e:
                self.logger.error(f"Error applying Windows heuristic {rule['description']}: {e}")
                
        return content, applied_rules
        
    def _apply_context_heuristics(self, content, code_context):
        """Apply context-aware heuristics"""
        applied_rules = []
        for rule in self.heuristics['context']:
            pattern = rule['pattern']
            replacement_func = rule['replacement']
            original = content
            
            try:
                def replace_func(match):
                    if callable(replacement_func):
                        return replacement_func(match, code_context)
                    return replacement_func
                    
                content = re.sub(pattern, replace_func, content)
                
                if content != original:
                    applied_rules.append(rule['description'])
            except Exception as e:
                self.logger.error(f"Error applying context heuristic {rule['description']}: {e}")
                
        return content, applied_rules
        
    def _detect_languages(self, content):
        """Detect programming languages in content"""
        languages_found = set()
        
        # Check for explicit code blocks
        code_blocks = re.findall(r'```(\w*)', content)
        for lang in code_blocks:
            lang = lang.lower().strip()
            # Map some common aliases
            lang_mapping = {
                'py': 'python',
                'js': 'javascript',
                'ts': 'typescript',
                'cs': 'csharp',
                'cpp': 'cpp',
                'c++': 'cpp',
                'rb': 'ruby',
                'sh': 'bash',
                'shell': 'bash'
            }
            
            if lang in lang_mapping:
                languages_found.add(lang_mapping[lang])
            elif lang in self.programming_languages:
                languages_found.add(lang)
                
        # Check for common language indicators if no language tags found
        if not languages_found:
            if re.search(r'def\s+\w+\s*\(.*\):', content):
                languages_found.add('python')
            if re.search(r'function\s+\w+\s*\(.*\)\s*{', content):
                languages_found.add('javascript')
            if re.search(r'public\s+class\s+\w+', content):
                languages_found.add('java')
            if re.search(r'package\s+main|func\s+\w+\s*\(.*\)\s*{', content):
                languages_found.add('go')
            if re.search(r'namespace\s+\w+|public\s+class\s+\w+\s*:', content):
                languages_found.add('csharp')
                
        return languages_found
        
    def _get_context_specific_name(self, generic_name, code_context):
        """Get context-specific name from code context"""
        if not code_context:
            return generic_name
            
        # Map of generic names to meaningful prefixes
        context_prefixes = {
            'myFunction': 'handle',
            'doSomething': 'process',
            'process': 'transform',
            'handler': 'handle'
        }
        
        prefix = context_prefixes.get(generic_name, '')
        
        # Try to find a relevant context node
        for node_id, data in code_context:
            if data.get('type') == 'class' and prefix:
                return f"{prefix}{node_id}"
                
        # If no context found, make a generic improvement
        generic_improvements = {
            'myFunction': 'processData',
            'doSomething': 'handleRequest',
            'process': 'processInput',
            'handler': 'handleEvent'
        }
        
        return generic_improvements.get(generic_name, generic_name)
        
    def _get_specific_reference(self, generic_reference, code_context):
        """Replace generic references with specific ones based on context"""
        if not code_context or not code_context[0:2]:
            return generic_reference
            
        # Try to extract repository name from context
        repo_name = None
        for node_id, data in code_context:
            if data.get('type') == 'repository':
                repo_name = os.path.basename(node_id)
                break
                
        if repo_name:
            if generic_reference == 'in the codebase':
                return f"in the {repo_name} codebase"
            elif generic_reference == 'in your project':
                return f"in the {repo_name} project"
                
        return generic_reference
    
class ExpertReasoning:
    """Provides expert-level reasoning in different roles"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.llm = LLMInterface(config)
        
    def analyze_as_senior_dev(self, code, language, context=None):
        """Analyze code as a senior developer"""
        prompt = f"""As a Senior Developer with extensive experience in {language}, analyze this code:

{code}"""
        return self.llm.generate_response(prompt, context or {}, [])

def analyze_as_quality_expert(self, code, language, context=None):
    """Analyze code quality and best practices"""
    prompt = f"""As a Code Quality Expert specializing in {language}, review this code: {code}"""

def analyze_as_tester(self, code, language, context=None):
    """Analyze testability and suggest test cases"""
    prompt = f"""As a Testing Expert for {language} applications, analyze this code for testability:
{code}"""
    return self.llm.generate_response(prompt, context or {}, [])

def explain_code(self, code, language, detail_level="medium", context=None):
    """Generate a detailed explanation of code"""
    # Adjust detail level (brief, medium, detailed)
    detail_prompts = {
        "brief": "Provide a concise summary of what this code does.",
        "medium": "Explain this code's functionality, key components, and how they work together.",
        "detailed": "Provide a detailed line-by-line explanation of this code, its purpose, and implementation details."
    }
    
    detail_instruction = detail_prompts.get(detail_level, detail_prompts["medium"])
    
    prompt = f"""Explain this {language} code: {code} {detail_instruction}"""
    return self.llm.generate_response(prompt, context or {}, [])
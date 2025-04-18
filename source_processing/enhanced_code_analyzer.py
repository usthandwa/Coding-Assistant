# ai_coding_agent/source_processing/enhanced_code_analyzer.py
import logging
import os
import re
import ast
from pathlib import Path
from typing import Dict, List, Any, Optional

class EnhancedCodeAnalyzer:
    """Advanced code analysis for understanding functions, classes, and relationships"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.language_parsers = {}
        self._init_parsers()
        
    def _init_parsers(self):
        """Initialize language-specific parsers"""
        # Python parser is built-in using ast module
        self.language_parsers['python'] = PythonCodeParser()
        
        # JavaScript/TypeScript parser
        self.language_parsers['javascript'] = JavaScriptCodeParser()
        self.language_parsers['typescript'] = self.language_parsers['javascript']
        
        # Java parser
        self.language_parsers['java'] = JavaCodeParser()
        
        # C/C++ parser
        self.language_parsers['c'] = CCodeParser()
        self.language_parsers['cpp'] = self.language_parsers['c']
        
        # Generic parser for other languages
        generic_parser = GenericCodeParser()
        for language in ['csharp', 'go', 'ruby', 'php', 'swift', 'rust', 'kotlin']:
            self.language_parsers[language] = generic_parser
            
    def analyze_code_source(self, source_data):
        """
        Analyze an entire code source (directory, repository, etc.)
        
        Args:
            source_data (dict): Source data from CodeSourceScanner
            
        Returns:
            dict: Analysis results
        """
        self.logger.info(f"Analyzing code source: {source_data['path']}")
        
        analysis_results = {
            'files_analyzed': 0,
            'functions': [],
            'classes': [],
            'dependencies': [],
            'quality_metrics': {},
            'language_breakdown': {},
            'symbols': {},
            'insights': []
        }
        
        try:
            # Track language distribution
            language_count = {}
            
            # Analyze each file
            for file_data in source_data['files']:
                file_path = file_data['path']
                content = file_data['content']
                language = file_data['language']
                
                # Update language count
                language_count[language] = language_count.get(language, 0) + 1
                
                # Skip files that are too large or in unsupported languages
                if language == 'unknown' or len(content) > self.config.get('max_analysis_size', 500000):
                    continue
                
                try:
                    # Analyze file
                    file_analysis = self.analyze_file(file_path, content, language)
                    if file_analysis:
                        # Add functions
                        for func in file_analysis.get('functions', []):
                            # Add source location
                            func['file'] = file_path
                            func['language'] = language
                            analysis_results['functions'].append(func)
                            
                        # Add classes
                        for cls in file_analysis.get('classes', []):
                            # Add source location
                            cls['file'] = file_path
                            cls['language'] = language
                            analysis_results['classes'].append(cls)
                            
                        # Update count
                        analysis_results['files_analyzed'] += 1
                        
                except Exception as e:
                    self.logger.warning(f"Error analyzing file {file_path}: {e}")
            
            # Set language breakdown
            analysis_results['language_breakdown'] = language_count
            
            # Build cross-file relationships
            self._build_cross_file_relationships(analysis_results)
            
            # Generate insights
            self._generate_insights(analysis_results, source_data)
            
            self.logger.info(f"Analyzed {analysis_results['files_analyzed']} files, found {len(analysis_results['functions'])} functions, {len(analysis_results['classes'])} classes")
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Error analyzing code source: {e}")
            return analysis_results
            
    def analyze_file(self, file_path, content, language=None):
        """
        Analyze a single file
        
        Args:
            file_path (str): Path to the file
            content (str): File content
            language (str, optional): Programming language
            
        Returns:
            dict: File analysis results
        """
        try:
            # Detect language if not provided
            if not language:
                language = self._detect_language(file_path, content)
                
            # Get parser for language
            parser = self.language_parsers.get(language)
            if not parser:
                # Use generic parser if no specific parser is available
                parser = GenericCodeParser()
                
            # Parse and analyze
            analysis = parser.parse_and_analyze(content, file_path)
            
            # Add basic metrics
            analysis['metrics'] = self._calculate_metrics(content, language)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing file {file_path}: {e}")
            return None
            
    def explain_function(self, function_name, context):
        """
        Generate an explanation for a specific function
        
        Args:
            function_name (str): Function name to explain
            context (dict): Context with available functions
            
        Returns:
            dict: Function explanation
        """
        function_data = self._find_function(function_name, context)
        if not function_data:
            return {
                'name': function_name,
                'explanation': f"Function '{function_name}' not found in the current context."
            }
            
        # Get the function source code
        file_path = function_data.get('file')
        if not file_path or not os.path.exists(file_path):
            return {
                'name': function_name,
                'file': file_path,
                'explanation': f"Source file for function '{function_name}' not found."
            }
            
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Extract function code
            function_code = self._extract_function_code(
                content, 
                function_data.get('line_start', 0), 
                function_data.get('line_end', 0)
            )
            
            if not function_code:
                function_code = "// Function code could not be extracted"
                
            # Get function callers and callees
            callers = self._find_function_callers(function_name, context)
            callees = function_data.get('calls', [])
            
            # Build explanation
            language = function_data.get('language', 'unknown')
            
            explanation = {
                'name': function_name,
                'file': file_path,
                'language': language,
                'code': function_code,
                'signature': function_data.get('signature', function_name + '()'),
                'parameters': function_data.get('parameters', []),
                'return_type': function_data.get('return_type', 'unknown'),
                'docstring': function_data.get('docstring', ''),
                'complexity': function_data.get('complexity', 'unknown'),
                'called_by': callers,
                'calls': callees,
                'class': function_data.get('class', None)
            }
            
            return explanation
            
        except Exception as e:
            self.logger.error(f"Error explaining function {function_name}: {e}")
            return {
                'name': function_name,
                'file': file_path,
                'explanation': f"Error generating explanation: {str(e)}"
            }
            
    def explain_class(self, class_name, context):
        """
        Generate an explanation for a specific class
        
        Args:
            class_name (str): Class name to explain
            context (dict): Context with available classes
            
        Returns:
            dict: Class explanation
        """
        class_data = self._find_class(class_name, context)
        if not class_data:
            return {
                'name': class_name,
                'explanation': f"Class '{class_name}' not found in the current context."
            }
            
        # Get the class source code
        file_path = class_data.get('file')
        if not file_path or not os.path.exists(file_path):
            return {
                'name': class_name,
                'file': file_path,
                'explanation': f"Source file for class '{class_name}' not found."
            }
            
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Extract class code
            class_code = self._extract_class_code(
                content, 
                class_data.get('line_start', 0), 
                class_data.get('line_end', 0)
            )
            
            if not class_code:
                class_code = "// Class code could not be extracted"
                
            # Get class methods
            methods = class_data.get('methods', [])
            
            # Build explanation
            language = class_data.get('language', 'unknown')
            
            explanation = {
                'name': class_name,
                'file': file_path,
                'language': language,
                'code': class_code,
                'docstring': class_data.get('docstring', ''),
                'methods': methods,
                'properties': class_data.get('properties', []),
                'superclasses': class_data.get('superclasses', []),
                'subclasses': class_data.get('subclasses', [])
            }
            
            return explanation
            
        except Exception as e:
            self.logger.error(f"Error explaining class {class_name}: {e}")
            return {
                'name': class_name,
                'file': file_path,
                'explanation': f"Error generating explanation: {str(e)}"
            }
    
    def _extract_function_code(self, content, line_start, line_end):
        """Extract function code from content using line numbers"""
        if line_start <= 0 or line_end <= 0:
            return None
            
        try:
            lines = content.split('\n')
            if line_start > len(lines):
                return None
                
            # Adjust line_end if it's beyond the file length
            if line_end > len(lines):
                line_end = len(lines)
                
            # Extract the lines
            function_lines = lines[line_start-1:line_end]
            return '\n'.join(function_lines)
            
        except Exception as e:
            self.logger.error(f"Error extracting function code: {e}")
            return None
            
    def _extract_class_code(self, content, line_start, line_end):
        """Extract class code from content using line numbers"""
        return self._extract_function_code(content, line_start, line_end)
        
    def _find_function(self, function_name, context):
        """Find function data in the context"""
        # This should search context for the function
        functions = context.get('functions', [])
        
        # Case-insensitive search
        function_name_lower = function_name.lower()
        
        # Look for exact matches
        for func in functions:
            if func['name'].lower() == function_name_lower:
                return func
                
        # Look for partial matches (for methods)
        if '.' in function_name_lower:
            method_name = function_name_lower.split('.')[-1]
            for func in functions:
                if func['name'].lower() == method_name:
                    return func
                    
        return None
        
    def _find_class(self, class_name, context):
        """Find class data in the context"""
        # This should search context for the class
        classes = context.get('classes', [])
        
        # Case-insensitive search
        class_name_lower = class_name.lower()
        
        for cls in classes:
            if cls['name'].lower() == class_name_lower:
                return cls
                
        return None
        
    def _find_function_callers(self, function_name, context):
        """Find functions that call the given function"""
        callers = []
        
        # Get all functions from context
        functions = context.get('functions', [])
        
        # Look for callers
        for func in functions:
            if 'calls' in func and function_name in func['calls']:
                callers.append(func['name'])
                
        return callers
        
    def _build_cross_file_relationships(self, analysis_results):
        """Build relationships between functions and classes across files"""
        # Create a symbol map
        symbol_map = {}
        
        # Add functions to symbol map
        for func in analysis_results['functions']:
            symbol_map[func['name']] = {
                'type': 'function',
                'data': func
            }
            
        # Add classes to symbol map
        for cls in analysis_results['classes']:
            symbol_map[cls['name']] = {
                'type': 'class',
                'data': cls
            }
            
        # Find dependencies
        for func in analysis_results['functions']:
            # Skip if no calls
            if 'calls' not in func:
                continue
                
            for called_func in func['calls']:
                if called_func in symbol_map:
                    # Add dependency
                    target = symbol_map[called_func]['data']
                    analysis_results['dependencies'].append({
                        'source': func['name'],
                        'target': called_func,
                        'source_file': func['file'],
                        'target_file': target['file'],
                        'type': 'call'
                    })
        
        # Store symbol map
        analysis_results['symbols'] = symbol_map
        
    def _generate_insights(self, analysis_results, source_data):
        """Generate insights about the code"""
        insights = []
        
        # Insight 1: Language distribution
        if analysis_results['language_breakdown']:
            languages = analysis_results['language_breakdown']
            primary_language = max(languages.items(), key=lambda x: x[1])[0]
            if primary_language != 'unknown':
                insights.append(f"Primary language is {primary_language} ({languages[primary_language]} files)")
        
        # Insight 2: Code complexity
        complex_functions = []
        for func in analysis_results['functions']:
            if func.get('complexity', 0) > 10:  # Arbitrary threshold
                complex_functions.append(func['name'])
                
        if complex_functions:
            if len(complex_functions) > 3:
                insights.append(f"Found {len(complex_functions)} complex functions that may need refactoring")
            else:
                insights.append(f"Complex functions that may need refactoring: {', '.join(complex_functions)}")
        
        # Insight 3: Cross-file dependencies
        dependencies = {}
        for dep in analysis_results['dependencies']:
            source_file = dep['source_file']
            target_file = dep['target_file']
            
            if source_file != target_file:
                key = f"{source_file} -> {target_file}"
                dependencies[key] = dependencies.get(key, 0) + 1
                
        if dependencies:
            most_coupled = max(dependencies.items(), key=lambda x: x[1])
            insights.append(f"Strongest coupling: {most_coupled[0]} ({most_coupled[1]} connections)")
        
        # Add insights to analysis results
        analysis_results['insights'] = insights
        
    def _calculate_metrics(self, content, language):
        """Calculate code metrics for a file"""
        metrics = {}
        
        # Line count
        lines = content.split('\n')
        metrics['total_lines'] = len(lines)
        
        # Code lines (non-empty, non-comment)
        code_lines = 0
        comment_lines = 0
        
        # Language-specific comment patterns
        comment_pattern = r'^\s*#'  # Default to Python-style comments
        if language in ['javascript', 'typescript', 'java', 'csharp', 'cpp', 'c']:
            comment_pattern = r'^\s*(//|/\*|\*)'
            
        for line in lines:
            if not line.strip():
                continue  # Skip empty lines
                
            if re.match(comment_pattern, line):
                comment_lines += 1
            else:
                code_lines += 1
                
        metrics['code_lines'] = code_lines
        metrics['comment_lines'] = comment_lines
        
        # Calculate comment ratio
        if code_lines > 0:
            metrics['comment_ratio'] = round(comment_lines / code_lines, 2)
        else:
            metrics['comment_ratio'] = 0
            
        return metrics
        
    def _detect_language(self, file_path, content=None):
        """Detect programming language from file path and content"""
        # Get extension
        ext = os.path.splitext(file_path)[1].lower()
        
        # Map extension to language
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.c': 'c',
            '.h': 'c',
            '.cpp': 'cpp',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.go': 'go',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.rs': 'rust'
        }
        
        if ext in language_map:
            return language_map[ext]
            
        # If extension not found, try content-based detection
        if content:
            # Python indicators
            if re.search(r'def\s+\w+\s*\(.*\):', content) or re.search(r'import\s+\w+', content):
                return 'python'
                
            # JavaScript indicators
            if re.search(r'function\s+\w+\s*\(.*\)\s*{', content) or re.search(r'const|let|var', content):
                return 'javascript'
        
        return 'unknown'


class BaseCodeParser:
    """Base class for language-specific code parsers"""
    
    def parse_and_analyze(self, content, file_path):
        """Parse and analyze code"""
        raise NotImplementedError("Subclasses must implement parse_and_analyze")


class PythonCodeParser(BaseCodeParser):
    """Parser for Python code"""
    
    def parse_and_analyze(self, content, file_path):
        """Parse and analyze Python code"""
        try:
            # Parse Python code
            tree = ast.parse(content)
            
            # Extract functions and classes
            functions = []
            classes = []
            
            for node in ast.walk(tree):
                # Extract functions
                if isinstance(node, ast.FunctionDef):
                    # Skip if it's a method (handled with classes)
                    if isinstance(node.parent, ast.ClassDef):
                        continue
                        
                    # Get docstring
                    docstring = ast.get_docstring(node)
                    
                    # Get parameters
                    parameters = []
                    for arg in node.args.args:
                        parameters.append({
                            'name': arg.arg,
                            'type': getattr(arg.annotation, 'id', None) if arg.annotation else None
                        })
                        
                    # Get return type
                    return_type = None
                    if node.returns:
                        return_type = getattr(node.returns, 'id', None)
                        
                    # Get function calls
                    calls = []
                    for subnode in ast.walk(node):
                        if isinstance(subnode, ast.Call) and hasattr(subnode.func, 'id'):
                            calls.append(subnode.func.id)
                            
                    # Calculate complexity (approximation)
                    complexity = 1
                    for subnode in ast.walk(node):
                        if isinstance(subnode, (ast.If, ast.For, ast.While, ast.Try)):
                            complexity += 1
                            
                    # Create function info
                    function_info = {
                        'name': node.name,
                        'line_start': node.lineno,
                        'line_end': node.end_lineno if hasattr(node, 'end_lineno') else node.lineno + 10,  # Approximation
                        'parameters': parameters,
                        'return_type': return_type,
                        'docstring': docstring,
                        'calls': calls,
                        'complexity': complexity,
                        'signature': f"def {node.name}({', '.join(arg['name'] for arg in parameters)})"
                    }
                    
                    functions.append(function_info)
                
                # Extract classes
                elif isinstance(node, ast.ClassDef):
                    # Get docstring
                    docstring = ast.get_docstring(node)
                    
                    # Get base classes
                    superclasses = []
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            superclasses.append(base.id)
                            
                    # Get methods
                    methods = []
                    for subnode in node.body:
                        if isinstance(subnode, ast.FunctionDef):
                            methods.append(subnode.name)
                            
                    # Get properties
                    properties = []
                    for subnode in node.body:
                        if isinstance(subnode, ast.Assign):
                            for target in subnode.targets:
                                if isinstance(target, ast.Name):
                                    properties.append(target.id)
                                    
                    # Create class info
                    class_info = {
                        'name': node.name,
                        'line_start': node.lineno,
                        'line_end': node.end_lineno if hasattr(node, 'end_lineno') else node.lineno + 20,  # Approximation
                        'superclasses': superclasses,
                        'methods': methods,
                        'properties': properties,
                        'docstring': docstring
                    }
                    
                    classes.append(class_info)
            
            return {
                'functions': functions,
                'classes': classes
            }
            
        except SyntaxError as e:
            # Handle syntax errors in Python code
            return {
                'functions': [],
                'classes': [],
                'error': f"Syntax error: {str(e)}"
            }
        except Exception as e:
            # Handle other errors
            return {
                'functions': [],
                'classes': [],
                'error': f"Error parsing Python code: {str(e)}"
            }


class JavaScriptCodeParser(BaseCodeParser):
    """Parser for JavaScript/TypeScript code"""
    
    def parse_and_analyze(self, content, file_path):
        """Parse and analyze JavaScript/TypeScript code"""
        try:
            # Use regex for simple parsing (not ideal but works for basic extraction)
            functions = []
            classes = []
            
            # Extract functions
            # Function declaration: function name(...) {...}
            function_pattern = r'function\s+(\w+)\s*\(([^)]*)\)\s*\{(.*?)(?<=})'
            func_matches = re.finditer(function_pattern, content, re.DOTALL)
            
            for match in func_matches:
                name = match.group(1)
                params_str = match.group(2)
                body = match.group(3)
                
                # Get line numbers
                start_pos = match.start()
                end_pos = match.end()
                line_start = content[:start_pos].count('\n') + 1
                line_end = content[:end_pos].count('\n') + 1
                
                # Parse parameters
                parameters = []
                for param in params_str.split(','):
                    param = param.strip()
                    if param:
                        param_name = param
                        param_type = None
                        
                        # Check for TypeScript type annotations
                        if ':' in param:
                            param_parts = param.split(':')
                            param_name = param_parts[0].strip()
                            param_type = param_parts[1].strip()
                            
                        parameters.append({
                            'name': param_name,
                            'type': param_type
                        })
                
                # Find function calls
                call_pattern = r'\b(\w+)\s*\('
                calls = [match[0][:-1] for match in re.findall(call_pattern, body)]
                
                # Calculate complexity
                complexity = 1
                complexity += body.count('if ')
                complexity += body.count('for ')
                complexity += body.count('while ')
                complexity += body.count('try ')
                complexity += body.count('catch ')
                
                # Create function info
                function_info = {
                    'name': name,
                    'line_start': line_start,
                    'line_end': line_end,
                    'parameters': parameters,
                    'return_type': None,  # Hard to detect without proper parsing
                    'docstring': self._extract_js_docstring(content, start_pos),
                    'calls': list(set(calls)),  # Remove duplicates
                    'complexity': complexity,
                    'signature': f"function {name}({', '.join(p['name'] for p in parameters)})"
                }
                
                functions.append(function_info)
            
            # Extract arrow functions assigned to variables
            arrow_pattern = r'(?:const|let|var)\s+(\w+)\s*=\s*(?:\([^)]*\)|\w+)\s*=>\s*\{(.*?)(?<=})'
            arrow_matches = re.finditer(arrow_pattern, content, re.DOTALL)
            
            for match in arrow_matches:
                name = match.group(1)
                body = match.group(2)
                
                # Get line numbers
                start_pos = match.start()
                end_pos = match.end()
                line_start = content[:start_pos].count('\n') + 1
                line_end = content[:end_pos].count('\n') + 1
                
                # Create function info (simplified)
                function_info = {
                    'name': name,
                    'line_start': line_start,
                    'line_end': line_end,
                    'parameters': [],  # Hard to parse with regex
                    'return_type': None,
                    'docstring': self._extract_js_docstring(content, start_pos),
                    'calls': [],
                    'complexity': 1,
                    'signature': f"{name} = () => {{ ... }}"  # Simplified
                }
                
                functions.append(function_info)
            
            # Extract classes
            class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{(.*?)(?<=})'
            class_matches = re.finditer(class_pattern, content, re.DOTALL)
            
            for match in class_matches:
                name = match.group(1)
                superclass = match.group(2)
                body = match.group(3)
                
                # Get line numbers
                start_pos = match.start()
                end_pos = match.end()
                line_start = content[:start_pos].count('\n') + 1
                line_end = content[:end_pos].count('\n') + 1
                
                # Extract methods
                method_pattern = r'(?:async\s+)?(\w+)\s*\(([^)]*)\)\s*\{(.*?)(?<=})'
                methods = [m.group(1) for m in re.finditer(method_pattern, body)]
                
                # Extract properties (simple approximation)
                prop_pattern = r'this\.(\w+)\s*='
                properties = [p for p in re.findall(prop_pattern, body)]
                
                # Create class info
                class_info = {
                    'name': name,
                    'line_start': line_start,
                    'line_end': line_end,
                    'superclasses': [superclass] if superclass else [],
                    'methods': methods,
                    'properties': properties,
                    'docstring': self._extract_js_docstring(content, start_pos)
                }
                
                classes.append(class_info)
            
            return {
                'functions': functions,
                'classes': classes
            }
            
        except Exception as e:
            # Handle errors
            return {
                'functions': [],
                'classes': [],
                'error': f"Error parsing JavaScript/TypeScript code: {str(e)}"
            }
            
    def _extract_js_docstring(self, content, pos):
        """Extract JSDoc comment above a function/class"""
        # Find the line start
        line_start = content.rfind('\n', 0, pos) + 1
        
        # Get the code before the function
        before_func = content[0:line_start].rstrip()
        
        # Look for JSDoc comment
        jsdoc_end = before_func.rfind('*/')
        if jsdoc_end != -1:
            jsdoc_start = before_func.rfind('/**', 0, jsdoc_end)
            if jsdoc_start != -1:
                return before_func[jsdoc_start:jsdoc_end + 2].strip()
                
        return None


class JavaCodeParser(BaseCodeParser):
    """Parser for Java code"""
    
    def parse_and_analyze(self, content, file_path):
        """Parse and analyze Java code"""
        try:
            # Use regex for simple parsing (not ideal but works for basic extraction)
            functions = []
            classes = []
            
            # Extract classes
            class_pattern = r'(?:public|private|protected)?\s+class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?\s*\{(.*?)(?<=})'
            class_matches = re.finditer(class_pattern, content, re.DOTALL)
            
            for match in class_matches:
                name = match.group(1)
                superclass = match.group(2)
                interfaces = match.group(3)
                body = match.group(4)
                
                # Get line numbers
                start_pos = match.start()
                end_pos = match.end()
                line_start = content[:start_pos].count('\n') + 1
                line_end = content[:end_pos].count('\n') + 1
                
                # Parse superclasses and interfaces
                superclasses = []
                if superclass:
                    superclasses.append(superclass)
                    
                if interfaces:
                    for interface in interfaces.split(','):
                        superclasses.append(interface.strip())
                
                # Extract methods
                method_pattern = r'(?:public|private|protected)?\s+(?:static\s+)?(?:final\s+)?(?:\w+)(?:<[^>]*>)?\s+(\w+)\s*\(([^)]*)\)\s*(?:throws\s+[^{]+)?\s*\{(.*?)(?<=})'
                method_matches = re.finditer(method_pattern, body, re.DOTALL)
                
                methods = []
                for m in method_matches:
                    method_name = m.group(1)
                    methods.append(method_name)
                    
                    # Add method as a function
                    method_start = start_pos + m.start()
                    method_end = start_pos + m.end()
                    method_line_start = content[:method_start].count('\n') + 1
                    method_line_end = content[:method_end].count('\n') + 1
                    
                    # Parse parameters
                    params_str = m.group(2)
                    parameters = []
                    
                    for param in params_str.split(','):
                        param = param.strip()
                        if param:
                            param_parts = param.split()
                            if len(param_parts) >= 2:
                                param_type = param_parts[0]
                                param_name = param_parts[-1]
                                parameters.append({
                                    'name': param_name,
                                    'type': param_type
                                })
                    
                    # Create function info
                    function_info = {
                        'name': method_name,
                        'line_start': method_line_start,
                        'line_end': method_line_end,
                        'parameters': parameters,
                        'return_type': None,  # Hard to extract with regex
                        'docstring': None,
                        'calls': [],
                        'complexity': 1,
                        'signature': f"{method_name}({', '.join(p['name'] for p in parameters)})",
                        'class': name  # Link to the containing class
                    }
                    
                    functions.append(function_info)
                
                # Extract properties (fields)
                prop_pattern = r'(?:public|private|protected)?\s+(?:static\s+)?(?:final\s+)?(?:\w+)(?:<[^>]*>)?\s+(\w+)\s*[=;]'
                properties = [p for p in re.findall(prop_pattern, body)]
                
                # Create class info
                class_info = {
                    'name': name,
                    'line_start': line_start,
                    'line_end': line_end,
                    'superclasses': superclasses,
                    'methods': methods,
                    'properties': properties,
                    'docstring': self._extract_javadoc(content, start_pos)
                }
                
                classes.append(class_info)
            
            return {
                'functions': functions,
                'classes': classes
            }
            
        except Exception as e:
            # Handle errors
            return {
                'functions': [],
                'classes': [],
                'error': f"Error parsing Java code: {str(e)}"
            }
            
    def _extract_javadoc(self, content, pos):
        """Extract Javadoc comment above a class/method"""
        # Find the line start
        line_start = content.rfind('\n', 0, pos) + 1
        
        # Get the code before the class/method
        before_code = content[0:line_start].rstrip()
        
        # Look for Javadoc comment
        javadoc_end = before_code.rfind('*/')
        if javadoc_end != -1:
            javadoc_start = before_code.rfind('/**', 0, javadoc_end)
            if javadoc_start != -1:
                return before_code[javadoc_start:javadoc_end + 2].strip()
                
        return None


class CCodeParser(BaseCodeParser):
    """Parser for C/C++ code"""
    
    def parse_and_analyze(self, content, file_path):
        """Parse and analyze C/C++ code"""
        try:
            # Use regex for simple parsing
            functions = []
            classes = []
            
            # Extract functions (C-style)
            func_pattern = r'(?:static\s+)?(?:inline\s+)?(?:\w+)(?:\s+\*?\s*|\s+\*\s+|\s+)(\w+)\s*\(([^)]*)\)\s*(?:const)?\s*\{(.*?)(?<=})'
            func_matches = re.finditer(func_pattern, content, re.DOTALL)
            
            for match in func_matches:
                name = match.group(1)
                params_str = match.group(2)
                body = match.group(3)
                
                # Skip main function in header files or forward declarations
                if name == 'main' and '.h' in file_path:
                    continue
                    
                # Get line numbers
                start_pos = match.start()
                end_pos = match.end()
                line_start = content[:start_pos].count('\n') + 1
                line_end = content[:end_pos].count('\n') + 1
                
                # Parse parameters (simplified)
                parameters = []
                for param in params_str.split(','):
                    param = param.strip()
                    if param and param != 'void':
                        # Try to separate type and name
                        parts = param.split()
                        if len(parts) >= 2:
                            param_name = parts[-1].rstrip('*')
                            param_type = ' '.join(parts[:-1])
                            parameters.append({
                                'name': param_name,
                                'type': param_type
                            })
                        else:
                            parameters.append({
                                'name': param,
                                'type': None
                            })
                
                # Find function calls (simplified)
                call_pattern = r'\b(\w+)\s*\('
                calls = [match[0][:-1] for match in re.findall(call_pattern, body)]
                calls = [call for call in calls if call != name]  # Remove self-recursion
                
                # Calculate complexity (approximation)
                complexity = 1
                complexity += body.count('if ')
                complexity += body.count('else ')
                complexity += body.count('for ')
                complexity += body.count('while ')
                complexity += body.count('switch ')
                complexity += body.count('case ')
                
                # Create function info
                function_info = {
                    'name': name,
                    'line_start': line_start,
                    'line_end': line_end,
                    'parameters': parameters,
                    'return_type': None,  # Hard to extract with simple regex
                    'docstring': None,
                    'calls': list(set(calls)),  # Remove duplicates
                    'complexity': complexity,
                    'signature': f"{name}({', '.join(p['name'] for p in parameters)})"
                }
                
                functions.append(function_info)
            
            # For C++, extract classes
            if '.cpp' in file_path or '.hpp' in file_path or '.cc' in file_path:
                class_pattern = r'(?:class|struct)\s+(\w+)(?:\s*:\s*(?:public|protected|private)\s+(\w+))?\s*\{(.*?)(?<=})\s*;'
                class_matches = re.finditer(class_pattern, content, re.DOTALL)
                
                for match in class_matches:
                    name = match.group(1)
                    superclass = match.group(2)
                    body = match.group(3)
                    
                    # Get line numbers
                    start_pos = match.start()
                    end_pos = match.end()
                    line_start = content[:start_pos].count('\n') + 1
                    line_end = content[:end_pos].count('\n') + 1
                    
                    # Extract methods (simplified)
                    method_pattern = r'(?:public|private|protected)?\s*:?\s*(?:virtual\s+)?(?:static\s+)?(?:\w+)(?:\s+\*?\s*|\s+\*\s+|\s+)(\w+)\s*\(([^)]*)\)\s*(?:const)?\s*(?:=\s*0)?\s*(?:override)?\s*(?:;\s*|(?::\s*[^{]+)?\s*\{)'
                    methods = [m.group(1) for m in re.finditer(method_pattern, body)]
                    
                    # Extract properties (simplified)
                    prop_pattern = r'(?:(?:public|private|protected)?\s*:?\s*)(?:static\s+)?(?:const\s+)?(?:\w+)(?:<[^>]*>)?(?:\s+\*?\s*|\s+\*\s+|\s+)(\w+)\s*[=;]'
                    properties = [p for p in re.findall(prop_pattern, body)]
                    
                    # Create class info
                    class_info = {
                        'name': name,
                        'line_start': line_start,
                        'line_end': line_end,
                        'superclasses': [superclass] if superclass else [],
                        'methods': methods,
                        'properties': properties,
                        'docstring': None
                    }
                    
                    classes.append(class_info)
            
            return {
                'functions': functions,
                'classes': classes
            }
            
        except Exception as e:
            # Handle errors
            return {
                'functions': [],
                'classes': [],
                'error': f"Error parsing C/C++ code: {str(e)}"
            }


class GenericCodeParser(BaseCodeParser):
    """Generic parser for other languages"""
    
    def parse_and_analyze(self, content, file_path):
        """Parse and analyze code in a language-agnostic way"""
        try:
            functions = []
            classes = []
            
            # Try to identify functions with common patterns
            # Pattern 1: function/def name(params)
            func_pattern1 = r'(?:function|def|sub|proc|fn)\s+(\w+)\s*\(([^)]*)\)'
            
            # Pattern 2: public/private returnType name(params)
            func_pattern2 = r'(?:public|private|protected|internal)?\s+(?:static\s+)?(?:\w+(?:<[^>]*>)?)\s+(\w+)\s*\(([^)]*)\)'
            
            # Find functions using pattern 1
            for match in re.finditer(func_pattern1, content):
                name = match.group(1)
                
                # Get line numbers
                start_pos = match.start()
                line_start = content[:start_pos].count('\n') + 1
                
                # Create function info
                function_info = {
                    'name': name,
                    'line_start': line_start,
                    'line_end': line_start + 5,  # Rough estimate
                    'parameters': [],
                    'return_type': None,
                    'docstring': None,
                    'calls': [],
                    'complexity': 1,
                    'signature': match.group(0)
                }
                
                functions.append(function_info)
                
            # Find functions using pattern 2
            for match in re.finditer(func_pattern2, content):
                name = match.group(1)
                
                # Get line numbers
                start_pos = match.start()
                line_start = content[:start_pos].count('\n') + 1
                
                # Create function info
                function_info = {
                    'name': name,
                    'line_start': line_start,
                    'line_end': line_start + 5,  # Rough estimate
                    'parameters': [],
                    'return_type': None,
                    'docstring': None,
                    'calls': [],
                    'complexity': 1,
                    'signature': match.group(0)
                }
                
                functions.append(function_info)
                
            # Try to identify classes
            class_pattern = r'(?:class|struct|interface)\s+(\w+)(?:\s+(?:extends|implements|inherits)\s+([^{]+))?'
            
            for match in re.finditer(class_pattern, content):
                name = match.group(1)
                inheritance = match.group(2)
                
                # Get line numbers
                start_pos = match.start()
                line_start = content[:start_pos].count('\n') + 1
                
                # Parse inheritance
                superclasses = []
                if inheritance:
                    superclasses = [s.strip() for s in inheritance.split(',')]
                
                # Create class info
                class_info = {
                    'name': name,
                    'line_start': line_start,
                    'line_end': line_start + 10,  # Rough estimate
                    'superclasses': superclasses,
                    'methods': [],
                    'properties': [],
                    'docstring': None
                }
                
                classes.append(class_info)
            
            return {
                'functions': functions,
                'classes': classes
            }
            
        except Exception as e:
            # Handle errors
            return {
                'functions': [],
                'classes': [],
                'error': f"Error parsing code: {str(e)}"
            }
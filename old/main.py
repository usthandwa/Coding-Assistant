# /main.py
import os
import argparse
import logging
from pathlib import Path
import traceback

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
from utils.config_utils import load_config

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(".log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="AI Coding Agent")
    parser.add_argument("--repo", type=str, help="Path to Git repository")
    parser.add_argument("--config", type=str, default="config/default_config.yaml", 
                       help="Path to configuration file")
    args = parser.parse_args()
    
    logger = setup_logging()
    logger.info("Starting AI Coding Agent")
    
    # Load configuration
    config = load_config(args.config)
    
    # Initialize components
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
    
    # Create the AI Coding Agent
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
    
    # Process repository if provided
    # In main.py, modify the repository processing logic
    if args.repo:
        repo_path = args.repo
    if repo_path.startswith(('http://', 'https://')):
        # It's a remote URL, clone it first
        repo_path = git_parser.clone_repository(repo_path)
        if not repo_path:
            logger.error(f"Failed to clone repository: {args.repo}")
            return
    
    # Now process the local repository
    if os.path.exists(repo_path):
        agent.process_repository(Path(repo_path))
    else:
        logger.error(f"Repository path does not exist: {repo_path}")
        return
    
    # Start interactive mode
    agent.start_interactive_mode()

class AICodingAgent:
    def __init__(self, git_parser, code_indexer, syntax_parser, semantic_analyzer,
                 session_store, code_graph, llm, heuristics, query_processor, 
                 response_generator, config):
        self.git_parser = git_parser
        self.code_indexer = code_indexer
        self.syntax_parser = syntax_parser
        self.semantic_analyzer = semantic_analyzer
        self.session_store = session_store
        self.code_graph = code_graph
        self.llm = llm
        self.heuristics = heuristics
        self.query_processor = query_processor
        self.response_generator = response_generator
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def process_repository(self, repo_path):
        """Process a Git repository to build the code knowledge base"""
        self.logger.info(f"Processing repository: {repo_path}")
        
        # Parse Git repository structure
        repo_data = self.git_parser.parse_repository(repo_path)
        
        # Index the code
        self.code_indexer.index_repository(repo_data)
        
        # Build syntax trees
        self.syntax_parser.parse_repository(repo_path)
        
        # Perform semantic analysis
        self.semantic_analyzer.analyze_repository(repo_path)
        
        # Build code context graph
        self.code_graph.build_graph(repo_path)
        
        self.logger.info(f"Repository processing complete: {repo_path}")
        
    def start_interactive_mode(self):
        """Start interactive mode to accept user queries"""
        self.logger.info("Starting interactive mode")
        print("AI Coding Agent is ready. Type 'exit' to quit.")
        
        while True:
            try:
                user_input = input("> ")
                if user_input.lower() == 'exit':
                    break
                    
                # Process query
                processed_query = self.query_processor.process(user_input)
                
                # Get relevant context
                context = self.session_store.get_relevant_context(processed_query)
                code_context = self.code_graph.get_relevant_nodes(processed_query)
                
                # Generate response using reasoning framework
                llm_response = self.llm.generate_response(
                    query=processed_query,
                    context=context,
                    code_context=code_context
                )
                
                # Apply heuristics to improve response
                refined_response = self.heuristics.apply_heuristics(llm_response, code_context)
                
                # Format and display response
                formatted_response = self.response_generator.format_response(refined_response)
                print(formatted_response)
                
                # Update session context
                self.session_store.update_context(user_input, formatted_response)
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                self.logger.error(f"Error processing query: {e}\n{traceback.format_exc()}")
                print(f"Error: {e}")
        
        self.logger.info("Interactive mode ended")

if __name__ == "__main__":
    main()
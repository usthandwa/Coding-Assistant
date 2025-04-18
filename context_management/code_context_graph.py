# CodingAssistant/context_management/code_context_graph.py
import logging
import json
import os
from pathlib import Path
import networkx as nx

class CodeContextGraph:
    """
    Builds and manages a graph representation of code relationships
    """
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.graph = nx.DiGraph()
        self.storage_dir = Path(config.get('storage_dir', 'graphs'))
        os.makedirs(self.storage_dir, exist_ok=True)
        
    def build_graph(self, repo_path):
        """
        Build a code context graph for a repository
        
        Args:
            repo_path (str): Path to the repository
            
        Returns:
            bool: Success
        """
        self.logger.info(f"Building code context graph for repository: {repo_path}")
        
        try:
            repo_path = Path(repo_path)
            
            # Clear existing graph
            self.graph = nx.DiGraph()
            
            # Add repository node
            self.graph.add_node(str(repo_path), type='repository', path=str(repo_path))
            
            # Add file nodes
            self._add_file_nodes(repo_path)
            
            # Add code entity nodes (classes, functions, etc.)
            self._add_code_entities(repo_path)
            
            # Add relationships
            self._add_code_relationships(repo_path)
            
            # Save graph
            self._save_graph(repo_path.name)
            
            self.logger.info(f"Built code context graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
            return True
            
        except Exception as e:
            self.logger.error(f"Error building code context graph: {e}")
            return False
            
    def _add_file_nodes(self, repo_path):
        """Add file nodes to the graph"""
        for path in repo_path.rglob('*'):
            if path.is_file() and '.git' not in str(path):
                relative_path = path.relative_to(repo_path)
                self.graph.add_node(
                    str(relative_path),
                    type='file',
                    path=str(relative_path),
                    extension=path.suffix,
                    size=path.stat().st_size
                )
                
                # Add edge from repository to file
                self.graph.add_edge(str(repo_path), str(relative_path), relationship='contains')
                
                # Add directory hierarchy
                parent_dir = relative_path.parent
                while parent_dir != Path('.'):
                    # Add directory node if it doesn't exist
                    if str(parent_dir) not in self.graph:
                        self.graph.add_node(
                            str(parent_dir),
                            type='directory',
                            path=str(parent_dir)
                        )
                        
                        # Add edge from repository to directory
                        self.graph.add_edge(str(repo_path), str(parent_dir), relationship='contains')
                        
                    # Add edge from directory to file
                    self.graph.add_edge(str(parent_dir), str(relative_path), relationship='contains')
                    
                    # Move up one level
                    parent_dir = parent_dir.parent
                    
    def _add_code_entities(self, repo_path):
        """Add code entity nodes to the graph"""
        # This would typically use language-specific parsers to extract entities
        # For demonstration, we'll add a few placeholder nodes
        
        # In a real implementation, we would:
        # 1. Parse each file
        # 2. Extract classes, functions, variables, etc.
        # 3. Add them as nodes with appropriate attributes
        # 4. Connect them to their containing files
        
        # Example: Adding a placeholder class node
        self.graph.add_node(
            'ExampleClass',
            type='class',
            path='example/file.py',
            methods=['method1', 'method2']
        )
        
        # Connect to file
        self.graph.add_edge('example/file.py', 'ExampleClass', relationship='contains')
        
    def _add_code_relationships(self, repo_path):
        """Add relationships between code entities"""
        # This would typically analyze imports, function calls, etc.
        # For demonstration, we'll add a few placeholder relationships
        
        # Example: Adding a placeholder "calls" relationship
        self.graph.add_edge(
            'ExampleClass',
            'method1',
            relationship='defines'
        )
        
    def get_relevant_nodes(self, query, max_nodes=10):
        """
        Get nodes relevant to a query
        
        Args:
            query (str): User query
            max_nodes (int, optional): Maximum number of nodes to return
            
        Returns:
            list: Relevant nodes
        """
        # In a real implementation, we would:
        # 1. Parse the query to identify mentioned code entities
        # 2. Find those entities in the graph
        # 3. Get neighboring nodes that are relevant to the query
        # 4. Return the subgraph
        
        # For demonstration, return a few random nodes
        import random
        
        if len(self.graph) == 0:
            return []
            
        nodes = list(self.graph.nodes(data=True))
        if len(nodes) > max_nodes:
            nodes = random.sample(nodes, max_nodes)
            
        return nodes
        
    def find_path(self, source, target):
        """
        Find a path between two code entities
        
        Args:
            source (str): Source entity
            target (str): Target entity
            
        Returns:
            list: Path between entities
        """
        try:
            if source in self.graph and target in self.graph:
                path = nx.shortest_path(self.graph, source, target)
                return [{'node': node, 'data': self.graph.nodes[node]} for node in path]
            else:
                return []
        except nx.NetworkXNoPath:
            return []
        except Exception as e:
            self.logger.error(f"Error finding path: {e}")
            return []
            
    def find_dependencies(self, entity):
        """
        Find dependencies of a code entity
        
        Args:
            entity (str): Code entity
            
        Returns:
            dict: Dependencies
        """
        if entity not in self.graph:
            return {}
            
        dependencies = {
            'incoming': [],
            'outgoing': []
        }
        
        # Incoming edges (what depends on this entity)
        for source, _, data in self.graph.in_edges(entity, data=True):
            dependencies['incoming'].append({
                'entity': source,
                'type': self.graph.nodes[source].get('type'),
                'relationship': data.get('relationship')
            })
            
        # Outgoing edges (what this entity depends on)
        for _, target, data in self.graph.out_edges(entity, data=True):
            dependencies['outgoing'].append({
                'entity': target,
                'type': self.graph.nodes[target].get('type'),
                'relationship': data.get('relationship')
            })
            
        return dependencies
        
    def _save_graph(self, repo_name):
        """Save graph to disk"""
        try:
            graph_path = self.storage_dir / f"{repo_name}_graph.json"
            
            # Convert NetworkX graph to JSON
            data = nx.node_link_data(self.graph)
            
            with open(graph_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving graph: {e}")
            return False
            
    def load_graph(self, repo_name):
        """
        Load graph from disk
        
        Args:
            repo_name (str): Repository name
            
        Returns:
            bool: Success
        """
        try:
            graph_path = self.storage_dir / f"{repo_name}_graph.json"
            
            if not graph_path.exists():
                self.logger.warning(f"Graph for {repo_name} not found")
                return False
                
            with open(graph_path, 'r') as f:
                data = json.load(f)
                
            self.graph = nx.node_link_graph(data)
            
            self.logger.info(f"Loaded graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading graph: {e}")
            return False


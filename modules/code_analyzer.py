"""
Code Analysis for Intelligent Refactoring
Identifies clusters of related functions for extraction into child modules
"""

import ast
import networkx as nx
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FunctionInfo:
    """Information about a function"""
    name: str
    lineno: int
    end_lineno: int
    calls: Set[str] = field(default_factory=set)  # Functions this calls
    called_by: Set[str] = field(default_factory=set)  # Functions that call this
    uses_globals: Set[str] = field(default_factory=set)  # Global variables used
    assigns_globals: Set[str] = field(default_factory=set)  # Global variables assigned
    class_methods: Set[str] = field(default_factory=set)  # Methods if this is a class


@dataclass
class FunctionCluster:
    """A cluster of related functions that could be extracted"""
    functions: List[str]
    cohesion_score: float  # 0-1, higher = more tightly coupled
    coupling_score: float  # 0-1, lower = less coupled to rest of file
    total_lines: int
    suggested_module_name: str
    rationale: str


class CodeAnalyzer:
    """Analyze Python code to identify refactoring opportunities"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.functions: Dict[str, FunctionInfo] = {}
        self.call_graph = nx.DiGraph()
        self.data_graph = nx.Graph()  # Undirected - shared data connections

    def analyze(self) -> bool:
        """Analyze the file and build graphs"""
        try:
            with open(self.file_path, 'r') as f:
                source = f.read()

            tree = ast.parse(source, filename=str(self.file_path))

            # Extract all functions and their relationships
            self._extract_functions(tree)
            self._build_call_graph()
            self._build_data_graph()

            return True

        except Exception as e:
            print(f"Error analyzing {self.file_path}: {e}")
            return False

    def _extract_functions(self, tree: ast.AST):
        """Extract all function definitions and their metadata"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = FunctionInfo(
                    name=node.name,
                    lineno=node.lineno,
                    end_lineno=node.end_lineno or node.lineno
                )

                # Find function calls within this function
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name):
                            func_info.calls.add(child.func.id)
                        elif isinstance(child.func, ast.Attribute):
                            func_info.calls.add(child.func.attr)

                    # Find global variable usage
                    if isinstance(child, ast.Name):
                        if isinstance(child.ctx, ast.Load):
                            func_info.uses_globals.add(child.id)
                        elif isinstance(child.ctx, ast.Store):
                            func_info.assigns_globals.add(child.id)

                self.functions[node.name] = func_info

            # Handle class methods
            elif isinstance(node, ast.ClassDef):
                class_name = node.name
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_info = FunctionInfo(
                            name=f"{class_name}.{item.name}",
                            lineno=item.lineno,
                            end_lineno=item.end_lineno or item.lineno
                        )
                        # Mark as class method
                        method_info.class_methods.add(class_name)
                        self.functions[method_info.name] = method_info

    def _build_call_graph(self):
        """Build directed graph of function calls"""
        for func_name, func_info in self.functions.items():
            self.call_graph.add_node(func_name)

            for called_func in func_info.calls:
                if called_func in self.functions:
                    self.call_graph.add_edge(func_name, called_func)
                    self.functions[called_func].called_by.add(func_name)

    def _build_data_graph(self):
        """Build undirected graph of shared data dependencies"""
        # Functions that share global variables are connected
        for func1_name, func1_info in self.functions.items():
            self.data_graph.add_node(func1_name)

            for func2_name, func2_info in self.functions.items():
                if func1_name >= func2_name:  # Avoid duplicates
                    continue

                # Check for shared global usage
                shared_reads = func1_info.uses_globals & func2_info.uses_globals
                shared_writes = func1_info.assigns_globals & func2_info.assigns_globals
                read_write_conflict = (func1_info.uses_globals & func2_info.assigns_globals) | \
                                     (func2_info.uses_globals & func1_info.assigns_globals)

                if shared_reads or shared_writes or read_write_conflict:
                    # Weight by number of shared variables
                    weight = len(shared_reads) + len(shared_writes) + len(read_write_conflict)
                    self.data_graph.add_edge(func1_name, func2_name, weight=weight)

    def identify_clusters(self, min_cluster_size: int = 3, min_lines: int = 100) -> List[FunctionCluster]:
        """Identify clusters of functions that could be extracted"""
        clusters = []

        # Use community detection to find clusters
        try:
            # Combine call graph and data graph for clustering
            combined_graph = nx.Graph()

            # Add call graph edges (directed -> undirected)
            for edge in self.call_graph.edges():
                combined_graph.add_edge(edge[0], edge[1], weight=2.0)

            # Add data graph edges
            for edge in self.data_graph.edges(data=True):
                weight = edge[2].get('weight', 1.0)
                if combined_graph.has_edge(edge[0], edge[1]):
                    combined_graph[edge[0]][edge[1]]['weight'] += weight
                else:
                    combined_graph.add_edge(edge[0], edge[1], weight=weight)

            # Find connected components as potential clusters
            components = list(nx.connected_components(combined_graph))

            for component in components:
                if len(component) < min_cluster_size:
                    continue

                # Calculate metrics for this cluster
                total_lines = sum(
                    self.functions[f].end_lineno - self.functions[f].lineno + 1
                    for f in component if f in self.functions
                )

                if total_lines < min_lines:
                    continue

                # Calculate cohesion (internal connections)
                internal_edges = sum(
                    1 for f1 in component for f2 in component
                    if combined_graph.has_edge(f1, f2)
                )
                max_internal = len(component) * (len(component) - 1) / 2
                cohesion = internal_edges / max_internal if max_internal > 0 else 0

                # Calculate coupling (external connections)
                external_edges = sum(
                    1 for f in component
                    for neighbor in combined_graph.neighbors(f)
                    if neighbor not in component
                )
                max_external = len(component) * (len(self.functions) - len(component))
                coupling = external_edges / max_external if max_external > 0 else 0

                # Generate suggested module name
                suggested_name = self._suggest_module_name(list(component))

                # Generate rationale
                rationale = self._generate_rationale(component, cohesion, coupling, total_lines)

                cluster = FunctionCluster(
                    functions=sorted(list(component)),
                    cohesion_score=cohesion,
                    coupling_score=coupling,
                    total_lines=total_lines,
                    suggested_module_name=suggested_name,
                    rationale=rationale
                )

                clusters.append(cluster)

        except Exception as e:
            print(f"Error identifying clusters: {e}")

        # Sort by quality (high cohesion, low coupling, good size)
        clusters.sort(key=lambda c: (c.cohesion_score - c.coupling_score, c.total_lines), reverse=True)

        return clusters

    def _suggest_module_name(self, functions: List[str]) -> str:
        """Suggest a module name based on function names"""
        # Extract common prefixes or patterns
        if not functions:
            return "helpers"

        # Look for common prefixes
        first_func = functions[0]
        if '_' in first_func:
            prefix = first_func.split('_')[0]
            if all(f.startswith(prefix) for f in functions):
                return f"{prefix}_utils"

        # Look for common themes in names
        if any('handle' in f.lower() for f in functions):
            return "handlers"
        if any('process' in f.lower() for f in functions):
            return "processors"
        if any('parse' in f.lower() or 'format' in f.lower() for f in functions):
            return "formatters"
        if any('tool' in f.lower() for f in functions):
            return "tool_utils"

        # Default
        base_name = self.file_path.stem
        return f"{base_name}_helpers"

    def _generate_rationale(self, component: Set[str], cohesion: float, coupling: float, total_lines: int) -> str:
        """Generate human-readable rationale for extraction"""
        reasons = []

        if cohesion > 0.7:
            reasons.append("Functions are highly cohesive (frequently call each other)")
        if coupling < 0.3:
            reasons.append("Low coupling to rest of file (few external dependencies)")
        if total_lines > 200:
            reasons.append(f"Significant size reduction ({total_lines} lines)")

        # Check for shared data
        shared_data = set()
        for func in component:
            if func in self.functions:
                shared_data.update(self.functions[func].uses_globals)

        if shared_data:
            reasons.append(f"Share {len(shared_data)} global variables/state")

        return ". ".join(reasons) if reasons else "Candidate for extraction"

    def get_file_stats(self) -> Dict[str, int]:
        """Get statistics about the file"""
        total_lines = 0
        if self.file_path.exists():
            with open(self.file_path, 'r') as f:
                total_lines = sum(1 for _ in f)

        return {
            'total_lines': total_lines,
            'function_count': len(self.functions),
            'max_nesting': self._calculate_max_nesting(),
        }

    def _calculate_max_nesting(self) -> int:
        """Calculate maximum nesting depth in file"""
        try:
            with open(self.file_path, 'r') as f:
                tree = ast.parse(f.read())

            max_depth = 0

            def visit_node(node, depth=0):
                nonlocal max_depth
                max_depth = max(max_depth, depth)

                for child in ast.iter_child_nodes(node):
                    if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                        visit_node(child, depth + 1)
                    else:
                        visit_node(child, depth)

            visit_node(tree)
            return max_depth

        except Exception:
            return 0


def analyze_file(file_path: str) -> Tuple[CodeAnalyzer, List[FunctionCluster]]:
    """Convenience function to analyze a file"""
    analyzer = CodeAnalyzer(file_path)
    if analyzer.analyze():
        clusters = analyzer.identify_clusters()
        return analyzer, clusters
    return analyzer, []

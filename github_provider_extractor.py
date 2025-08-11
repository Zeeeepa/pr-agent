#!/usr/bin/env python3
"""
GitHub Provider Extractor using Tree-sitter

This script uses tree-sitter to programmatically extract and consolidate
all GitHub provider dependencies from the pr-agent codebase into a single
standalone code file.
"""

import os
import re
import ast
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict

try:
    import tree_sitter_python as tspython
    from tree_sitter import Language, Parser, Node
except ImportError:
    print("Error: tree-sitter-python not installed. Run: pip install tree-sitter tree-sitter-python")
    sys.exit(1)


@dataclass
class ImportInfo:
    """Information about an import statement"""
    module: str
    names: List[str]
    alias: Optional[str] = None
    is_from_import: bool = False
    line_number: int = 0


@dataclass
class ClassInfo:
    """Information about a class definition"""
    name: str
    bases: List[str]
    methods: List[str]
    source_code: str
    line_start: int
    line_end: int
    file_path: str


@dataclass
class FunctionInfo:
    """Information about a function definition"""
    name: str
    args: List[str]
    source_code: str
    line_start: int
    line_end: int
    file_path: str


class GitHubProviderExtractor:
    """Extract GitHub provider and all its dependencies using tree-sitter"""
    
    def __init__(self, pr_agent_root: str):
        self.pr_agent_root = Path(pr_agent_root)
        self.parser = Parser(Language(tspython.language()))
        
        # Track all discovered dependencies
        self.imports: Dict[str, List[ImportInfo]] = defaultdict(list)
        self.classes: Dict[str, ClassInfo] = {}
        self.functions: Dict[str, FunctionInfo] = {}
        self.constants: Dict[str, str] = {}
        self.enums: Dict[str, str] = {}
        
        # Files to analyze
        self.target_files = [
            "pr_agent/git_providers/github_provider.py",
            "pr_agent/git_providers/git_provider.py",
            "pr_agent/algo/file_filter.py",
            "pr_agent/algo/git_patch_processing.py",
            "pr_agent/algo/language_handler.py",
            "pr_agent/algo/types.py",
            "pr_agent/algo/utils.py",
            "pr_agent/config_loader.py",
            "pr_agent/log/__init__.py",
            "pr_agent/servers/utils.py",
        ]
        
        # Track processed files to avoid cycles
        self.processed_files: Set[str] = set()
        
        # External dependencies that need to be imported
        self.external_deps = {
            'github', 'retry', 'starlette_context', 'dynaconf', 
            'loguru', 'pydantic', 'html2text', 'requests', 'yaml'
        }

    def parse_file(self, file_path: str) -> Optional[Node]:
        """Parse a Python file using tree-sitter"""
        try:
            full_path = self.pr_agent_root / file_path
            if not full_path.exists():
                print(f"Warning: File not found: {full_path}")
                return None
                
            with open(full_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
                
            tree = self.parser.parse(bytes(source_code, 'utf8'))
            return tree.root_node
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None

    def extract_imports(self, node: Node, source_code: str, file_path: str) -> List[ImportInfo]:
        """Extract import statements from AST node"""
        imports = []
        
        def visit_node(n: Node):
            if n.type == 'import_statement':
                # Handle: import module
                import_text = source_code[n.start_byte:n.end_byte]
                match = re.match(r'import\s+(.+)', import_text)
                if match:
                    modules = [m.strip() for m in match.group(1).split(',')]
                    for module in modules:
                        if ' as ' in module:
                            mod, alias = module.split(' as ')
                            imports.append(ImportInfo(
                                module=mod.strip(),
                                names=[],
                                alias=alias.strip(),
                                is_from_import=False,
                                line_number=n.start_point[0] + 1
                            ))
                        else:
                            imports.append(ImportInfo(
                                module=module.strip(),
                                names=[],
                                is_from_import=False,
                                line_number=n.start_point[0] + 1
                            ))
                            
            elif n.type == 'import_from_statement':
                # Handle: from module import name1, name2
                import_text = source_code[n.start_byte:n.end_byte]
                match = re.match(r'from\s+(.+?)\s+import\s+(.+)', import_text)
                if match:
                    module = match.group(1).strip()
                    names_part = match.group(2).strip()
                    
                    # Handle parentheses and multiline imports
                    names_part = re.sub(r'[()]', '', names_part)
                    names = [n.strip() for n in names_part.split(',') if n.strip()]
                    
                    imports.append(ImportInfo(
                        module=module,
                        names=names,
                        is_from_import=True,
                        line_number=n.start_point[0] + 1
                    ))
            
            for child in n.children:
                visit_node(child)
        
        visit_node(node)
        return imports

    def extract_classes(self, node: Node, source_code: str, file_path: str) -> Dict[str, ClassInfo]:
        """Extract class definitions from AST node"""
        classes = {}
        
        def visit_node(n: Node):
            if n.type == 'class_definition':
                class_name = None
                bases = []
                methods = []
                
                # Get class name
                for child in n.children:
                    if child.type == 'identifier':
                        class_name = source_code[child.start_byte:child.end_byte]
                        break
                
                # Get base classes
                for child in n.children:
                    if child.type == 'argument_list':
                        base_text = source_code[child.start_byte:child.end_byte]
                        # Simple extraction of base class names
                        base_matches = re.findall(r'(\w+)', base_text)
                        bases.extend(base_matches)
                        break
                
                # Get methods
                def find_methods(class_node: Node):
                    for child in class_node.children:
                        if child.type == 'function_definition':
                            for grandchild in child.children:
                                if grandchild.type == 'identifier':
                                    method_name = source_code[grandchild.start_byte:grandchild.end_byte]
                                    methods.append(method_name)
                                    break
                        elif child.type == 'block':
                            find_methods(child)
                
                find_methods(n)
                
                if class_name:
                    class_source = source_code[n.start_byte:n.end_byte]
                    classes[class_name] = ClassInfo(
                        name=class_name,
                        bases=bases,
                        methods=methods,
                        source_code=class_source,
                        line_start=n.start_point[0] + 1,
                        line_end=n.end_point[0] + 1,
                        file_path=file_path
                    )
            
            for child in n.children:
                visit_node(child)
        
        visit_node(node)
        return classes

    def extract_functions(self, node: Node, source_code: str, file_path: str) -> Dict[str, FunctionInfo]:
        """Extract function definitions from AST node"""
        functions = {}
        
        def visit_node(n: Node):
            if n.type == 'function_definition':
                func_name = None
                args = []
                
                # Get function name
                for child in n.children:
                    if child.type == 'identifier':
                        func_name = source_code[child.start_byte:child.end_byte]
                        break
                
                # Get arguments
                for child in n.children:
                    if child.type == 'parameters':
                        param_text = source_code[child.start_byte:child.end_byte]
                        # Simple extraction of parameter names
                        param_matches = re.findall(r'(\w+)(?:\s*:\s*\w+)?(?:\s*=\s*[^,)]+)?', param_text)
                        args = [p for p in param_matches if p not in ['self', 'cls']]
                        break
                
                if func_name:
                    func_source = source_code[n.start_byte:n.end_byte]
                    functions[func_name] = FunctionInfo(
                        name=func_name,
                        args=args,
                        source_code=func_source,
                        line_start=n.start_point[0] + 1,
                        line_end=n.end_point[0] + 1,
                        file_path=file_path
                    )
            
            for child in n.children:
                visit_node(child)
        
        visit_node(node)
        return functions

    def extract_constants_and_enums(self, node: Node, source_code: str, file_path: str) -> Tuple[Dict[str, str], Dict[str, str]]:
        """Extract constants and enum definitions"""
        constants = {}
        enums = {}
        
        def visit_node(n: Node):
            if n.type == 'assignment':
                # Look for constants (ALL_CAPS variables)
                assign_text = source_code[n.start_byte:n.end_byte]
                match = re.match(r'([A-Z_][A-Z0-9_]*)\s*=\s*(.+)', assign_text)
                if match:
                    const_name = match.group(1)
                    constants[const_name] = assign_text
            
            elif n.type == 'class_definition':
                # Check if it's an Enum class
                class_text = source_code[n.start_byte:n.end_byte]
                if 'Enum' in class_text:
                    class_name = None
                    for child in n.children:
                        if child.type == 'identifier':
                            class_name = source_code[child.start_byte:child.end_byte]
                            break
                    if class_name:
                        enums[class_name] = class_text
            
            for child in n.children:
                visit_node(child)
        
        visit_node(node)
        return constants, enums

    def analyze_file(self, file_path: str):
        """Analyze a single file and extract all relevant information"""
        if file_path in self.processed_files:
            return
            
        print(f"Analyzing: {file_path}")
        self.processed_files.add(file_path)
        
        root_node = self.parse_file(file_path)
        if not root_node:
            return
            
        # Read source code
        full_path = self.pr_agent_root / file_path
        with open(full_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Extract imports
        imports = self.extract_imports(root_node, source_code, file_path)
        self.imports[file_path].extend(imports)
        
        # Extract classes
        classes = self.extract_classes(root_node, source_code, file_path)
        self.classes.update(classes)
        
        # Extract functions
        functions = self.extract_functions(root_node, source_code, file_path)
        self.functions.update(functions)
        
        # Extract constants and enums
        constants, enums = self.extract_constants_and_enums(root_node, source_code, file_path)
        self.constants.update(constants)
        self.enums.update(enums)

    def resolve_internal_dependencies(self):
        """Resolve internal dependencies and add missing files"""
        # Look for internal imports that need to be included
        additional_files = set()
        
        for file_path, imports in self.imports.items():
            for imp in imports:
                if imp.module.startswith('pr_agent') or imp.module.startswith('..'):
                    # Convert relative imports to file paths
                    if imp.module.startswith('..'):
                        # Handle relative imports
                        current_dir = Path(file_path).parent
                        parts = imp.module.split('.')
                        target_path = current_dir
                        for part in parts:
                            if part == '..':
                                target_path = target_path.parent
                            elif part:
                                target_path = target_path / part
                        
                        potential_file = str(target_path) + '.py'
                        if (self.pr_agent_root / potential_file).exists():
                            additional_files.add(potential_file)
                    else:
                        # Handle absolute pr_agent imports
                        module_path = imp.module.replace('.', '/') + '.py'
                        if (self.pr_agent_root / module_path).exists():
                            additional_files.add(module_path)
        
        # Analyze additional files
        for file_path in additional_files:
            if file_path not in self.processed_files:
                self.analyze_file(file_path)

    def generate_consolidated_code(self) -> str:
        """Generate the consolidated code file"""
        output_lines = []
        
        # Header
        output_lines.extend([
            '#!/usr/bin/env python3',
            '"""',
            'Standalone GitHub Provider Module',
            '',
            'This file contains all the necessary code from pr-agent to use the GitHub provider',
            'as a standalone module. Generated using tree-sitter based extraction.',
            '',
            'Original source: https://github.com/qodo-ai/pr-agent',
            '"""',
            '',
        ])
        
        # Standard library imports
        std_imports = set()
        external_imports = set()
        
        for file_imports in self.imports.values():
            for imp in file_imports:
                if not imp.module.startswith('pr_agent') and not imp.module.startswith('..'):
                    if imp.module.split('.')[0] in self.external_deps:
                        external_imports.add(imp.module)
                    else:
                        std_imports.add(imp.module)
        
        # Add standard library imports
        if std_imports:
            for imp in sorted(std_imports):
                output_lines.append(f'import {imp}')
            output_lines.append('')
        
        # Add external library imports
        if external_imports:
            output_lines.append('# External dependencies')
            for imp in sorted(external_imports):
                output_lines.append(f'import {imp}')
            output_lines.append('')
        
        # Add constants
        if self.constants:
            output_lines.append('# Constants')
            for const_name, const_code in self.constants.items():
                output_lines.append(const_code)
            output_lines.append('')
        
        # Add enums
        if self.enums:
            output_lines.append('# Enums and Data Classes')
            for enum_name, enum_code in self.enums.items():
                output_lines.append(enum_code)
                output_lines.append('')
        
        # Add utility functions (non-class functions)
        utility_functions = {name: func for name, func in self.functions.items() 
                           if not any(name in cls.methods for cls in self.classes.values())}
        
        if utility_functions:
            output_lines.append('# Utility Functions')
            for func_name, func_info in utility_functions.items():
                output_lines.append(func_info.source_code)
                output_lines.append('')
        
        # Add classes in dependency order
        output_lines.append('# Classes')
        
        # Simple dependency ordering: base classes first
        ordered_classes = []
        remaining_classes = list(self.classes.values())
        
        while remaining_classes:
            added_this_round = []
            for cls in remaining_classes:
                # Check if all base classes are already added
                bases_satisfied = True
                for base in cls.bases:
                    if base in [c.name for c in self.classes.values()] and base not in [c.name for c in ordered_classes]:
                        bases_satisfied = False
                        break
                
                if bases_satisfied:
                    ordered_classes.append(cls)
                    added_this_round.append(cls)
            
            if not added_this_round:
                # Add remaining classes (circular dependencies or external bases)
                ordered_classes.extend(remaining_classes)
                break
            
            for cls in added_this_round:
                remaining_classes.remove(cls)
        
        for cls in ordered_classes:
            output_lines.append(cls.source_code)
            output_lines.append('')
        
        # Add main execution example
        output_lines.extend([
            '',
            'if __name__ == "__main__":',
            '    # Example usage',
            '    print("GitHub Provider Module loaded successfully")',
            '    print("Available classes:")',
            '    for cls_name in [' + ', '.join(f'"{name}"' for name in self.classes.keys()) + ']:',
            '        print(f"  - {cls_name}")',
        ])
        
        return '\n'.join(output_lines)

    def run(self) -> str:
        """Run the extraction process"""
        print("Starting GitHub Provider extraction using tree-sitter...")
        
        # Analyze all target files
        for file_path in self.target_files:
            self.analyze_file(file_path)
        
        # Resolve additional dependencies
        self.resolve_internal_dependencies()
        
        # Generate consolidated code
        consolidated_code = self.generate_consolidated_code()
        
        print(f"\nExtraction complete!")
        print(f"Processed files: {len(self.processed_files)}")
        print(f"Extracted classes: {len(self.classes)}")
        print(f"Extracted functions: {len(self.functions)}")
        print(f"Extracted constants: {len(self.constants)}")
        print(f"Extracted enums: {len(self.enums)}")
        
        return consolidated_code


def main():
    """Main execution function"""
    if len(sys.argv) > 1:
        pr_agent_root = sys.argv[1]
    else:
        pr_agent_root = "."
    
    extractor = GitHubProviderExtractor(pr_agent_root)
    consolidated_code = extractor.run()
    
    # Write to output file
    output_file = "github_provider_standalone.py"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(consolidated_code)
    
    print(f"\nConsolidated code written to: {output_file}")
    print(f"File size: {len(consolidated_code)} characters")


if __name__ == "__main__":
    main()

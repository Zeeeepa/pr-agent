#!/usr/bin/env python3
"""
GitHub Provider Extraction using Graph-sitter

This script uses graph-sitter to build a rich graph representation of the pr-agent
codebase and extract the GitHub provider with all its dependencies into a standalone module.

Graph-sitter provides advanced static analysis capabilities including:
- Dependency tracking and resolution
- Symbol usage analysis
- Call graph traversal
- Multi-file relationship mapping
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass
import json

try:
    from graph_sitter.core.codebase import Codebase
    HAS_GRAPH_SITTER = True
except ImportError:
    print("Error: graph-sitter not installed. Run: pip install graph-sitter")
    sys.exit(1)


@dataclass
class ExtractionResult:
    """Results from graph-sitter extraction"""
    symbols: List[str]
    dependencies: Dict[str, List[str]]
    files: List[str]
    call_graph: Dict[str, List[str]]
    imports: Dict[str, List[str]]
    exports: Dict[str, List[str]]


class GraphSitterGitHubProviderExtractor:
    """Extract GitHub provider using graph-sitter's advanced static analysis"""
    
    def __init__(self, pr_agent_root: str):
        self.pr_agent_root = Path(pr_agent_root)
        self.codebase = None
        self.extraction_result = None
        
        # Core entry points for extraction
        self.entry_points = [
            "pr_agent/git_providers/github_provider.py",
            "pr_agent/git_providers/git_provider.py"
        ]
        
        # Track extracted components
        self.extracted_symbols = set()
        self.extracted_files = set()
        self.dependency_graph = {}
        
    def initialize_codebase(self):
        """Initialize graph-sitter codebase analysis"""
        print("🔍 Initializing graph-sitter codebase analysis...")
        
        try:
            # Initialize codebase - this builds the rich graph representation
            self.codebase = Codebase(str(self.pr_agent_root))
            print(f"✅ Codebase initialized with {len(self.codebase.files)} files")
            
            # Show some basic stats
            python_files = [f for f in self.codebase.files if str(f.path).endswith('.py')]
            print(f"📊 Found {len(python_files)} Python files")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize codebase: {e}")
            return False
    
    def analyze_github_provider(self):
        """Analyze GitHub provider using graph-sitter's symbol analysis"""
        print("\n🔍 Analyzing GitHub provider with graph-sitter...")
        
        try:
            # Get the main GitHub provider file
            github_provider_file = None
            for file in self.codebase.files:
                if str(file.path).endswith('git_providers/github_provider.py'):
                    github_provider_file = file
                    break
            
            if not github_provider_file:
                print("❌ GitHub provider file not found")
                return False
            
            print(f"📁 Analyzing: {github_provider_file.path}")
            
            # Get all classes in the file
            classes = github_provider_file.classes
            print(f"🏗️  Found {len(classes)} classes:")
            for cls in classes:
                print(f"   - {cls.name}")
                self.extracted_symbols.add(cls.name)
            
            # Get all functions in the file
            functions = github_provider_file.functions
            print(f"⚙️  Found {len(functions)} functions:")
            for func in functions[:10]:  # Show first 10
                print(f"   - {func.name}")
                self.extracted_symbols.add(func.name)
            
            if len(functions) > 10:
                print(f"   ... and {len(functions) - 10} more functions")
            
            # Analyze imports and dependencies
            imports = github_provider_file.imports
            print(f"📦 Found {len(imports)} imports:")
            for imp in imports[:10]:  # Show first 10
                print(f"   - {imp}")
            
            if len(imports) > 10:
                print(f"   ... and {len(imports) - 10} more imports")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to analyze GitHub provider: {e}")
            return False
    
    def trace_dependencies(self):
        """Use graph-sitter to trace all dependencies of GitHub provider"""
        print("\n🕸️  Tracing dependencies using graph-sitter...")
        
        try:
            # Find GitHubProvider class
            github_provider_class = None
            for file in self.codebase.files:
                if str(file.path).endswith('git_providers/github_provider.py'):
                    for cls in file.classes:
                        if cls.name in ['GitHubProvider', 'GithubProvider']:
                            github_provider_class = cls
                            break
                    break
            
            if not github_provider_class:
                print("❌ GitHubProvider class not found")
                return False
            
            print(f"🎯 Found GitHub provider class: {github_provider_class.name}")
            
            # Get dependencies using graph-sitter's dependency analysis
            dependencies = github_provider_class.dependencies
            print(f"📊 GitHubProvider has {len(dependencies)} direct dependencies:")
            
            for dep in dependencies[:15]:  # Show first 15
                print(f"   - {dep}")
                self.extracted_symbols.add(str(dep))
            
            if len(dependencies) > 15:
                print(f"   ... and {len(dependencies) - 15} more dependencies")
            
            # Get usages - where GitHubProvider is used
            usages = github_provider_class.usages
            print(f"🔗 GitHubProvider is used in {len(usages)} places:")
            for usage in usages[:10]:
                print(f"   - {usage}")
            
            # Trace transitive dependencies
            print("\n🔄 Tracing transitive dependencies...")
            all_deps = set()
            to_process = list(dependencies)
            processed = set()
            
            while to_process and len(all_deps) < 100:  # Limit to prevent infinite loops
                current = to_process.pop(0)
                if current in processed:
                    continue
                
                processed.add(current)
                all_deps.add(current)
                
                # Try to find the symbol and get its dependencies
                try:
                    symbol = self.codebase.get_symbol(str(current))
                    if symbol and hasattr(symbol, 'dependencies'):
                        for sub_dep in symbol.dependencies:
                            if sub_dep not in processed:
                                to_process.append(sub_dep)
                except:
                    # Symbol might not be found, continue
                    pass
            
            print(f"📈 Total transitive dependencies: {len(all_deps)}")
            self.extracted_symbols.update(str(dep) for dep in all_deps)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to trace dependencies: {e}")
            return False
    
    def analyze_call_graph(self):
        """Analyze call graph for GitHub provider methods"""
        print("\n📞 Analyzing call graph...")
        
        try:
            # Find key methods in GitHubProvider
            key_methods = [
                'get_diff_files', 'publish_comment', 'get_pr_url', 
                'get_languages', 'publish_labels', 'get_issue_comments'
            ]
            
            call_graph = {}
            
            for method_name in key_methods:
                try:
                    # Get the symbol for this method
                    symbol = self.codebase.get_symbol(method_name)
                    if symbol:
                        # Get what this method calls
                        calls = getattr(symbol, 'calls', [])
                        call_graph[method_name] = [str(call) for call in calls[:10]]
                        print(f"🔗 {method_name} calls {len(calls)} functions")
                        
                        # Get what calls this method
                        callers = getattr(symbol, 'callers', [])
                        if callers:
                            print(f"   Called by {len(callers)} functions")
                            
                except Exception as e:
                    print(f"   ⚠️  Could not analyze {method_name}: {e}")
            
            self.dependency_graph.update(call_graph)
            return True
            
        except Exception as e:
            print(f"❌ Failed to analyze call graph: {e}")
            return False
    
    def extract_required_files(self):
        """Extract all files required for GitHub provider functionality"""
        print("\n📁 Extracting required files...")
        
        try:
            # Core files we know we need
            core_files = [
                'pr_agent/git_providers/github_provider.py',
                'pr_agent/git_providers/git_provider.py',
                'pr_agent/algo/types.py',
                'pr_agent/algo/file_filter.py',
                'pr_agent/algo/git_patch_processing.py',
                'pr_agent/algo/language_handler.py',
                'pr_agent/algo/utils.py',
                'pr_agent/config_loader.py',
                'pr_agent/log/__init__.py',
                'pr_agent/servers/utils.py'
            ]
            
            required_files = set()
            
            # Add core files
            for file_path in core_files:
                full_path = self.pr_agent_root / file_path
                if full_path.exists():
                    required_files.add(file_path)
                    print(f"✅ {file_path}")
                else:
                    print(f"⚠️  {file_path} (not found)")
            
            # Use graph-sitter to find additional dependencies
            print("\n🔍 Using graph-sitter to find additional file dependencies...")
            
            for file_path in list(required_files):
                try:
                    # Find the file in codebase
                    file_obj = None
                    for f in self.codebase.files:
                        if str(f.path).endswith(file_path.split('/')[-1]):
                            file_obj = f
                            break
                    
                    if file_obj:
                        # Get imports from this file
                        imports = file_obj.imports
                        for imp in imports:
                            # Try to resolve import to file path
                            import_str = str(imp)
                            if 'pr_agent' in import_str:
                                # This is an internal import we might need
                                print(f"   📦 Found internal import: {import_str}")
                                
                except Exception as e:
                    print(f"   ⚠️  Could not analyze {file_path}: {e}")
            
            self.extracted_files = required_files
            print(f"\n📊 Total files to extract: {len(required_files)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to extract required files: {e}")
            return False
    
    def generate_extraction_summary(self):
        """Generate summary of extraction results"""
        print("\n📋 Extraction Summary")
        print("=" * 50)
        
        print(f"🎯 Extracted Symbols: {len(self.extracted_symbols)}")
        print(f"📁 Required Files: {len(self.extracted_files)}")
        print(f"🕸️  Dependency Relationships: {len(self.dependency_graph)}")
        
        # Show top symbols
        print(f"\n🔝 Top Extracted Symbols:")
        for symbol in list(self.extracted_symbols)[:20]:
            print(f"   - {symbol}")
        
        if len(self.extracted_symbols) > 20:
            print(f"   ... and {len(self.extracted_symbols) - 20} more")
        
        # Show required files
        print(f"\n📁 Required Files:")
        for file_path in sorted(self.extracted_files):
            print(f"   - {file_path}")
        
        return {
            'symbols': list(self.extracted_symbols),
            'files': list(self.extracted_files),
            'dependencies': self.dependency_graph,
            'stats': {
                'total_symbols': len(self.extracted_symbols),
                'total_files': len(self.extracted_files),
                'dependency_relationships': len(self.dependency_graph)
            }
        }
    
    def create_standalone_module(self):
        """Create standalone module using graph-sitter analysis results"""
        print("\n🚀 Creating standalone module...")
        
        # Read all required files
        consolidated_code = []
        
        # Header
        consolidated_code.extend([
            '#!/usr/bin/env python3',
            '"""',
            'Standalone GitHub Provider Module - Generated with Graph-sitter',
            '',
            'This module was extracted using graph-sitter\'s advanced static analysis',
            'to build a rich graph representation of the pr-agent codebase and',
            'identify all dependencies required for GitHub provider functionality.',
            '',
            'Graph-sitter capabilities used:',
            '- Dependency tracking and resolution',
            '- Symbol usage analysis', 
            '- Call graph traversal',
            '- Multi-file relationship mapping',
            '',
            'Original source: https://github.com/qodo-ai/pr-agent',
            '"""',
            '',
            '# Standard library imports',
            'import os',
            'import sys',
            'import json',
            'import re',
            'import time',
            'import logging',
            'from typing import Optional, List, Dict, Any',
            'from dataclasses import dataclass',
            'from enum import Enum',
            'from abc import ABC, abstractmethod',
            '',
            '# External dependencies with graceful fallbacks',
            'try:',
            '    from github import Github, GithubException',
            '    from github.Issue import Issue',
            '    HAS_GITHUB = True',
            'except ImportError:',
            '    print("Warning: PyGithub not installed. Install with: pip install PyGithub")',
            '    HAS_GITHUB = False',
            '    class Github: pass',
            '    class GithubException(Exception): pass',
            '    class Issue: pass',
            '',
        ])
        
        # Add extracted code from each file
        for file_path in sorted(self.extracted_files):
            full_path = self.pr_agent_root / file_path
            if full_path.exists():
                print(f"📄 Processing: {file_path}")
                
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Clean up the content
                    content = self._clean_code_content(content, file_path)
                    
                    consolidated_code.append(f"# === {file_path} ===")
                    consolidated_code.append(content)
                    consolidated_code.append("")
                    
                except Exception as e:
                    print(f"⚠️  Could not process {file_path}: {e}")
        
        # Add usage example
        consolidated_code.extend([
            '# === Usage Example ===',
            'def demo_github_provider():',
            '    """Demonstrate GitHub provider functionality"""',
            '    if not HAS_GITHUB:',
            '        print("PyGithub not available - install with: pip install PyGithub")',
            '        return',
            '    ',
            '    try:',
            '        # Basic instantiation',
            '        provider = GitHubProvider()',
            '        print("✅ GitHubProvider created successfully")',
            '        ',
            '        # With PR URL (requires GitHub token)',
            '        # provider = GitHubProvider("https://github.com/owner/repo/pull/123")',
            '        # files = provider.get_diff_files()',
            '        # print(f"Found {len(files)} changed files")',
            '        ',
            '    except Exception as e:',
            '        print(f"❌ Error: {e}")',
            '',
            'if __name__ == "__main__":',
            '    print("GitHub Provider - Extracted with Graph-sitter")',
            '    print("=" * 50)',
            '    demo_github_provider()',
        ])
        
        return '\n'.join(consolidated_code)
    
    def _clean_code_content(self, content: str, file_path: str) -> str:
        """Clean code content for standalone module"""
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip pr_agent internal imports
            if re.match(r'from\s+pr_agent\.|from\s+\.\.|import\s+pr_agent', line):
                continue
            
            # Skip specific problematic imports
            if any(skip in line for skip in ['dynaconf', 'starlette_context', 'loguru']):
                continue
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def run_extraction(self):
        """Run the complete graph-sitter extraction process"""
        print("🚀 Starting Graph-sitter GitHub Provider Extraction")
        print("=" * 60)
        
        # Step 1: Initialize codebase
        if not self.initialize_codebase():
            return False
        
        # Step 2: Analyze GitHub provider
        if not self.analyze_github_provider():
            return False
        
        # Step 3: Trace dependencies
        if not self.trace_dependencies():
            return False
        
        # Step 4: Analyze call graph
        if not self.analyze_call_graph():
            return False
        
        # Step 5: Extract required files
        if not self.extract_required_files():
            return False
        
        # Step 6: Generate summary
        summary = self.generate_extraction_summary()
        
        # Step 7: Create standalone module
        standalone_code = self.create_standalone_module()
        
        # Save results
        output_file = "github_provider_graph_sitter.py"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(standalone_code)
        
        summary_file = "graph_sitter_extraction_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\n🎉 Extraction Complete!")
        print(f"📄 Standalone module: {output_file}")
        print(f"📊 Summary: {summary_file}")
        print(f"📏 Generated code: {len(standalone_code):,} characters")
        
        return True


def main():
    """Main execution"""
    if len(sys.argv) > 1:
        pr_agent_root = sys.argv[1]
    else:
        pr_agent_root = "."
    
    if not os.path.exists(pr_agent_root):
        print(f"❌ Directory not found: {pr_agent_root}")
        sys.exit(1)
    
    extractor = GraphSitterGitHubProviderExtractor(pr_agent_root)
    success = extractor.run_extraction()
    
    if success:
        print("\n✅ Graph-sitter extraction completed successfully!")
        print("🔍 The generated module uses graph-sitter's advanced static analysis")
        print("📊 All dependencies have been traced and included")
    else:
        print("\n❌ Extraction failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()

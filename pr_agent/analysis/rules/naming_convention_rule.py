"""
Naming Convention Rule for PR Static Analysis.

This rule checks if files and functions in the PR follow naming conventions.
"""

import re
from typing import Dict, Any, List
from pr_agent.analysis.rule_engine import Rule
from pr_agent.analysis.analysis_context import AnalysisContext
from pr_agent.algo.types import FilePatchInfo

class NamingConventionRule(Rule):
    """
    Rule that checks if files and functions in the PR follow naming conventions.
    """
    
    def __init__(self):
        """Initialize the naming convention rule."""
        super().__init__(
            rule_id="naming_convention",
            description="Checks if files and functions follow naming conventions",
            priority=5
        )
        
        # Define naming convention patterns
        self.python_file_pattern = re.compile(r'^[a-z][a-z0-9_]*\.py$')
        self.python_function_pattern = re.compile(r'def\s+([a-z][a-z0-9_]*)\s*\(')
        self.python_class_pattern = re.compile(r'class\s+([A-Z][a-zA-Z0-9]*)\s*[:\(]')
        
        self.js_file_pattern = re.compile(r'^[a-z][a-zA-Z0-9]*\.(js|jsx|ts|tsx)$')
        self.js_function_pattern = re.compile(r'function\s+([a-z][a-zA-Z0-9]*)\s*\(')
        self.js_class_pattern = re.compile(r'class\s+([A-Z][a-zA-Z0-9]*)\s*[{\(]')
        
    def run(self, context: AnalysisContext) -> Dict[str, Any]:
        """
        Run the rule on the given context.
        
        Args:
            context: The analysis context
            
        Returns:
            Dictionary containing the rule results
        """
        self.logger.info(f"Running {self.rule_id} rule")
        
        # Get changed files
        changed_files = context.get_changed_files()
        
        # Check naming conventions
        issues = []
        for file in changed_files:
            # Check file name convention
            file_issues = self._check_file_name(file)
            issues.extend(file_issues)
            
            # Check function and class names
            if file.head_file:
                content_issues = self._check_content(file)
                issues.extend(content_issues)
                
        # Return results
        return {
            'rule_id': self.rule_id,
            'description': self.description,
            'issues': issues,
            'passed': len(issues) == 0,
        }
        
    def _check_file_name(self, file: FilePatchInfo) -> List[Dict[str, Any]]:
        """
        Check if a file name follows naming conventions.
        
        Args:
            file: The file to check
            
        Returns:
            List of issues found
        """
        issues = []
        filename = file.filename.split('/')[-1]
        
        if filename.endswith('.py') and not self.python_file_pattern.match(filename):
            issues.append({
                'file': file.filename,
                'message': f"Python file name '{filename}' does not follow snake_case convention",
                'severity': 'low',
                'line': None,
            })
        elif any(filename.endswith(ext) for ext in ['.js', '.jsx', '.ts', '.tsx']) and not self.js_file_pattern.match(filename):
            issues.append({
                'file': file.filename,
                'message': f"JavaScript/TypeScript file name '{filename}' does not follow camelCase convention",
                'severity': 'low',
                'line': None,
            })
            
        return issues
        
    def _check_content(self, file: FilePatchInfo) -> List[Dict[str, Any]]:
        """
        Check if function and class names in a file follow naming conventions.
        
        Args:
            file: The file to check
            
        Returns:
            List of issues found
        """
        issues = []
        content = file.head_file
        filename = file.filename
        
        if filename.endswith('.py'):
            # Check Python function names
            for line_num, line in enumerate(content.splitlines(), 1):
                function_matches = self.python_function_pattern.findall(line)
                for func_name in function_matches:
                    if not re.match(r'^[a-z][a-z0-9_]*$', func_name):
                        issues.append({
                            'file': file.filename,
                            'message': f"Function name '{func_name}' does not follow snake_case convention",
                            'severity': 'low',
                            'line': line_num,
                        })
                
                # Check Python class names
                class_matches = self.python_class_pattern.findall(line)
                for class_name in class_matches:
                    if not re.match(r'^[A-Z][a-zA-Z0-9]*$', class_name):
                        issues.append({
                            'file': file.filename,
                            'message': f"Class name '{class_name}' does not follow PascalCase convention",
                            'severity': 'low',
                            'line': line_num,
                        })
                        
        elif any(filename.endswith(ext) for ext in ['.js', '.jsx', '.ts', '.tsx']):
            # Check JavaScript/TypeScript function names
            for line_num, line in enumerate(content.splitlines(), 1):
                function_matches = self.js_function_pattern.findall(line)
                for func_name in function_matches:
                    if not re.match(r'^[a-z][a-zA-Z0-9]*$', func_name):
                        issues.append({
                            'file': file.filename,
                            'message': f"Function name '{func_name}' does not follow camelCase convention",
                            'severity': 'low',
                            'line': line_num,
                        })
                
                # Check JavaScript/TypeScript class names
                class_matches = self.js_class_pattern.findall(line)
                for class_name in class_matches:
                    if not re.match(r'^[A-Z][a-zA-Z0-9]*$', class_name):
                        issues.append({
                            'file': file.filename,
                            'message': f"Class name '{class_name}' does not follow PascalCase convention",
                            'severity': 'low',
                            'line': line_num,
                        })
                        
        return issues


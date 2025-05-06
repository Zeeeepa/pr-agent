"""
Rule Engine for PR Static Analysis.

This module provides the RuleEngine class for managing and applying analysis rules.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Set
from pr_agent.analysis.analysis_context import AnalysisContext
from pr_agent.log import get_logger

class Rule(ABC):
    """
    Base class for analysis rules.
    
    Rules are used to analyze PRs and identify potential issues.
    """
    
    def __init__(self, rule_id: str, description: str, priority: int = 0):
        """
        Initialize a rule.
        
        Args:
            rule_id: Unique identifier for the rule
            description: Human-readable description of the rule
            priority: Priority of the rule (higher values run first)
        """
        self.rule_id = rule_id
        self.description = description
        self.priority = priority
        self.dependencies: Set[str] = set()
        self.logger = get_logger()
        
    def add_dependency(self, rule_id: str):
        """
        Add a dependency on another rule.
        
        Args:
            rule_id: ID of the rule this rule depends on
        """
        self.dependencies.add(rule_id)
        
    def should_run(self, context: AnalysisContext) -> bool:
        """
        Determine if the rule should run on the given context.
        
        Args:
            context: The analysis context
            
        Returns:
            True if the rule should run, False otherwise
        """
        # Check if all dependencies have been run
        for dep_id in self.dependencies:
            if dep_id not in context.results:
                self.logger.debug(f"Rule {self.rule_id} skipped: dependency {dep_id} not satisfied")
                return False
        return True
    
    @abstractmethod
    def run(self, context: AnalysisContext) -> Dict[str, Any]:
        """
        Run the rule on the given context.
        
        Args:
            context: The analysis context
            
        Returns:
            Dictionary containing the rule results
        """
        pass


class RuleEngine:
    """
    Manages and applies analysis rules.
    
    Supports rule prioritization and dependencies.
    Provides extension points for custom rules.
    """
    
    def __init__(self):
        """Initialize the rule engine."""
        self.rules: List[Rule] = []
        self.rule_map: Dict[str, Rule] = {}
        self.logger = get_logger()
        
    def register_rule(self, rule: Rule):
        """
        Register a rule with the engine.
        
        Args:
            rule: The rule to register
        """
        self.rules.append(rule)
        self.rule_map[rule.rule_id] = rule
        self.logger.info(f"Registered rule: {rule.rule_id}")
        
    def get_rule(self, rule_id: str) -> Optional[Rule]:
        """
        Get a rule by ID.
        
        Args:
            rule_id: The ID of the rule
            
        Returns:
            The rule, or None if not found
        """
        return self.rule_map.get(rule_id)
        
    def run_rules(self, context: AnalysisContext) -> Dict[str, Any]:
        """
        Run all applicable rules on the given context.
        
        Args:
            context: The analysis context
            
        Returns:
            Dictionary mapping rule IDs to results
        """
        self.logger.info("Running rules")
        
        # Sort rules by priority (higher values first)
        sorted_rules = sorted(self.rules, key=lambda r: r.priority, reverse=True)
        
        results = {}
        for rule in sorted_rules:
            if rule.should_run(context):
                self.logger.info(f"Running rule: {rule.rule_id}")
                try:
                    result = rule.run(context)
                    context.add_result(rule.rule_id, result)
                    results[rule.rule_id] = result
                    self.logger.info(f"Rule {rule.rule_id} completed successfully")
                except Exception as e:
                    self.logger.error(f"Error running rule {rule.rule_id}: {str(e)}")
            else:
                self.logger.info(f"Skipping rule: {rule.rule_id}")
                
        return results


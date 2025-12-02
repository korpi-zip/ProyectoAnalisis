from typing import Dict, Any, List, Optional
from .models import *
from .knowledge_base import KnowledgeBase
import re

class Complexity:
    def __init__(self, o: str = "1", omega: str = "1", theta: str = "1"):
        self.o = o
        self.omega = omega
        self.theta = theta

    def __repr__(self):
        return f"O({self.o}), Ω({self.omega}), Θ({self.theta})"

    def to_dict(self):
        return {"O": self.o, "Omega": self.omega, "Theta": self.theta}

    @staticmethod
    def from_dict(d: Dict[str, str]):
        return Complexity(d.get("O", "1"), d.get("Omega", "1"), d.get("Theta", "1"))

    def __add__(self, other: 'Complexity') -> 'Complexity':
        # Simplistic addition: max of terms
        return Complexity(
            self._add_term(self.o, other.o),
            self._add_term(self.omega, other.omega),
            self._add_term(self.theta, other.theta)
        )

    def __mul__(self, other: 'Complexity') -> 'Complexity':
        # Simplistic multiplication
        return Complexity(
            self._mul_term(self.o, other.o),
            self._mul_term(self.omega, other.omega),
            self._mul_term(self.theta, other.theta)
        )

    def _add_term(self, t1: str, t2: str) -> str:
        if t1 == "1": return t2
        if t2 == "1": return t1
        if t1 == t2: return t1
        # Very basic comparison logic (lexicographical is bad, but sufficient for simple cases)
        # Better: parse "n", "n^2", "log n"
        # For now, just return "max(" + t1 + ", " + t2 + ")" if unknown
        # Or simple heuristic:
        if "n^" in t1 and "n^" in t2:
            p1 = int(t1.split("^")[1])
            p2 = int(t2.split("^")[1])
            return f"n^{max(p1, p2)}"
        if "n" in t1 and t2 == "1": return t1
        if "n" in t2 and t1 == "1": return t2
        return f"max({t1}, {t2})"

    def _mul_term(self, t1: str, t2: str) -> str:
        if t1 == "1": return t2
        if t2 == "1": return t1
        # n * n = n^2
        if t1 == "n" and t2 == "n": return "n^2"
        if "n^" in t1 and t2 == "n":
            p = int(t1.split("^")[1])
            return f"n^{p+1}"
        if t1 == "n" and "n^" in t2:
            p = int(t2.split("^")[1])
            return f"n^{p+1}"
        return f"{t1} * {t2}"

class Analyzer:
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb

    def analyze(self, node: ASTNode, context: Dict[str, Any] = None) -> Complexity:
        if context is None:
            context = {}

        # 1. Check Memoization
        signature = KnowledgeBase.compute_signature(node.to_dict())
        cached = self.kb.get_complexity(signature)
        if cached:
            return Complexity.from_dict(cached)

        # 2. Analyze based on type
        result = Complexity("1", "1", "1")
        
        if isinstance(node, Program):
            result = self.analyze(node.main_block, context)
        
        elif isinstance(node, Block):
            total = Complexity("1", "1", "1")
            for stmt in node.statements:
                total = total + self.analyze(stmt, context)
            result = total
            
        elif isinstance(node, Assignment):
            result = Complexity("1", "1", "1") + self.analyze(node.value, context)
            
        elif isinstance(node, IfStatement):
            cond_cost = self.analyze(node.condition, context)
            then_cost = self.analyze(node.then_block, context)
            else_cost = self.analyze(node.else_block, context) if node.else_block else Complexity("1", "1", "1")
            max_branch = then_cost + else_cost 
            result = cond_cost + max_branch
            
        elif isinstance(node, ForLoop):
            # Check for dependency
            is_dependent = self.check_dependency(node, context)
            if is_dependent:
                # Use AI for dependent loops
                from .ai_engine import AIEngine
                ai = AIEngine()
                ai_result = ai.analyze_complexity(node.to_dict())
                result = Complexity.from_dict(ai_result)
            else:
                # Independent
                # Update context with loop variable?
                new_context = context.copy()
                new_context['loop_var'] = node.variable
                
                iterations = self.estimate_iterations(node.start_value, node.end_value)
                body_cost = self.analyze(node.body, new_context)
                result = iterations * body_cost
            
        elif isinstance(node, WhileLoop):
            result = Complexity("n", "n", "n") * self.analyze(node.body, context)
            
        elif isinstance(node, RepeatLoop):
            result = Complexity("n", "n", "n") * self.analyze(node.body, context)
            
        elif isinstance(node, Call):
            result = Complexity("1", "1", "1")
            
        elif isinstance(node, Expression):
            if isinstance(node, BinaryOp):
                result = self.analyze(node.left, context) + self.analyze(node.right, context)
            elif isinstance(node, UnaryOp):
                result = self.analyze(node.operand, context)
            elif isinstance(node, Literal) or isinstance(node, Variable):
                result = Complexity("1", "1", "1")
            elif isinstance(node, ArrayAccess):
                result = self.analyze(node.index, context)
            
        # 3. Memoize
        self.kb.add_complexity(signature, result.to_dict())
        return result

    def check_dependency(self, node: ForLoop, context: Dict[str, Any]) -> bool:
        # Check if start or end value depends on a variable in context (outer loop var)
        # This is a simplified check.
        # We need to traverse start_value and end_value to see if they contain variables present in context.
        # For now, let's assume if 'i' is in context and node uses 'i', it's dependent.
        # But we need to know what variables are from outer loops.
        # Context should store outer loop variables.
        
        outer_vars = context.keys()
        
        def contains_var(expr: ASTNode, vars: List[str]) -> bool:
            if isinstance(expr, Variable):
                return expr.name in vars
            if isinstance(expr, BinaryOp):
                return contains_var(expr.left, vars) or contains_var(expr.right, vars)
            return False

        if contains_var(node.start_value, outer_vars) or contains_var(node.end_value, outer_vars):
            return True
            
        return False

    def estimate_iterations(self, start: Expression, end: Expression) -> Complexity:
        if isinstance(end, Variable) and end.name == 'n':
            return Complexity("n", "n", "n")
        return Complexity("n", "n", "n")

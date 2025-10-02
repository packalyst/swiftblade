"""
Safe Evaluator
Safe expression evaluator using AST whitelisting
Prevents code injection attacks
"""

import ast
from typing import Any, Dict

from .exceptions import SecurityError, DirectiveError
from .constants import ERROR_CONTEXT_MAX_LENGTH


class SafeEvaluator:
    """
    Safe expression evaluator using AST whitelisting
    Prevents code injection attacks
    """

    # Allowed AST nodes for eval expressions
    EVAL_ALLOWED_NODES = (
        ast.Expression,
        ast.Call,
        ast.keyword,  # Allow keyword arguments in function calls
        ast.Name,
        ast.Load,
        ast.Constant,
        ast.Dict,
        ast.List,
        ast.Tuple,
        ast.Subscript,
        ast.Index,
        ast.Slice,
        ast.Attribute,
        ast.BinOp,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.FloorDiv,
        ast.Mod,
        ast.Pow,
        ast.Compare,
        ast.Eq,
        ast.NotEq,
        ast.Lt,
        ast.LtE,
        ast.Gt,
        ast.GtE,
        ast.Is,
        ast.IsNot,
        ast.In,
        ast.NotIn,
        ast.BoolOp,
        ast.And,
        ast.Or,
        ast.UnaryOp,
        ast.Not,
        ast.USub,
        ast.UAdd,
        ast.IfExp,
    )

    # Allowed AST nodes for exec statements
    EXEC_ALLOWED_NODES = EVAL_ALLOWED_NODES + (
        ast.Module,
        ast.Expr,
        ast.Assign,
        ast.AugAssign,
        ast.Store,
        ast.If,
        ast.For,
        ast.While,
        ast.Break,
        ast.Continue,
        ast.Pass,
    )

    @classmethod
    def safe_eval(cls, expr: str, context: Dict[str, Any]) -> Any:
        """
        Safely evaluate an expression

        Args:
            expr: Python expression string
            context: Variable context

        Returns:
            Evaluated result

        Raises:
            SecurityError: If expression contains disallowed nodes
        """
        expr = expr.strip()
        if not expr:
            return None

        try:
            # Parse expression
            node = ast.parse(expr, mode='eval')

            # Validate all nodes
            for subnode in ast.walk(node):
                if not isinstance(subnode, cls.EVAL_ALLOWED_NODES):
                    raise SecurityError(
                        f"Disallowed expression: {ast.dump(subnode)}",
                        context=expr
                    )

                # Block dunder attribute access (e.g., __class__, __import__)
                if isinstance(subnode, ast.Attribute):
                    attr_name = subnode.attr
                    if attr_name.startswith('__') and attr_name.endswith('__'):
                        raise SecurityError(
                            f"Access to dunder attributes is forbidden: {attr_name}",
                            context=expr
                        )
                    # Also block _PrivateAttribute access for extra security
                    if attr_name.startswith('_'):
                        raise SecurityError(
                            f"Access to private attributes is forbidden: {attr_name}",
                            context=expr
                        )

                # Block dunder variable names (e.g., __builtins__, __import__)
                if isinstance(subnode, ast.Name):
                    var_name = subnode.id
                    if var_name.startswith('__') and var_name.endswith('__'):
                        raise SecurityError(
                            f"Access to dunder names is forbidden: {var_name}",
                            context=expr
                        )

            # Helper functions
            def isset(var_name):
                """Check if a variable is defined in the context"""
                return var_name in context and context[var_name] is not None

            def first(collection, default=None):
                """Get first item from collection"""
                try:
                    return collection[0] if collection else default
                except (IndexError, TypeError, KeyError):
                    return default

            def last(collection, default=None):
                """Get last item from collection"""
                try:
                    return collection[-1] if collection else default
                except (IndexError, TypeError, KeyError):
                    return default

            def default_or(value, default=''):
                """Return default if value is None or empty"""
                return value if value else default

            # Compile and evaluate with safe builtins
            import json

            safe_builtins = {
                # Type constructors
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "list": list,
                "dict": dict,
                "tuple": tuple,
                "set": set,

                # Iteration & ranges
                "range": range,
                "enumerate": enumerate,
                "zip": zip,

                # Higher-order functions
                "map": map,
                "filter": filter,

                # Collection operations
                "len": len,
                "sorted": sorted,
                "sum": sum,
                "min": min,
                "max": max,
                "first": first,
                "last": last,
                "count": len,  # Alias for len

                # Math
                "abs": abs,
                "round": round,

                # String operations
                "upper": str.upper,
                "lower": str.lower,
                "capitalize": str.capitalize,
                "title": str.title,
                "strip": str.strip,
                "replace": str.replace,
                "split": str.split,
                "join": str.join,

                # JSON
                "json_encode": json.dumps,
                "json_decode": json.loads,

                # Type checks
                "is_list": lambda x: isinstance(x, list),
                "is_dict": lambda x: isinstance(x, dict),
                "is_string": lambda x: isinstance(x, str),
                "is_number": lambda x: isinstance(x, (int, float)),

                # Template helpers
                "isset": isset,
                "default": default_or,
            }
            code = compile(node, '<string>', 'eval')
            return eval(code, {"__builtins__": safe_builtins}, context)

        except SecurityError:
            raise
        except Exception as e:
            raise DirectiveError(f"Error evaluating expression: {e}", context=expr)

    @classmethod
    def safe_exec(cls, code_str: str, context: Dict[str, Any]):
        """
        Safely execute Python code (@python blocks)

        Args:
            code_str: Python code string
            context: Variable context (modified in place)

        Raises:
            SecurityError: If code contains disallowed nodes
        """
        code_str = code_str.strip()
        if not code_str:
            return

        try:
            # Parse code
            node = ast.parse(code_str, mode='exec')

            # Validate all nodes
            for subnode in ast.walk(node):
                if not isinstance(subnode, cls.EXEC_ALLOWED_NODES):
                    raise SecurityError(
                        f"Disallowed statement in @python block: {ast.dump(subnode)}",
                        context=code_str[:ERROR_CONTEXT_MAX_LENGTH]
                    )

                # Block dunder attribute access (e.g., __class__, __import__)
                if isinstance(subnode, ast.Attribute):
                    attr_name = subnode.attr
                    if attr_name.startswith('__') and attr_name.endswith('__'):
                        raise SecurityError(
                            f"Access to dunder attributes is forbidden: {attr_name}",
                            context=code_str[:ERROR_CONTEXT_MAX_LENGTH]
                        )
                    # Also block _PrivateAttribute access for extra security
                    if attr_name.startswith('_'):
                        raise SecurityError(
                            f"Access to private attributes is forbidden: {attr_name}",
                            context=code_str[:ERROR_CONTEXT_MAX_LENGTH]
                        )

                # Block dunder variable names (e.g., __builtins__, __import__)
                if isinstance(subnode, ast.Name):
                    var_name = subnode.id
                    if var_name.startswith('__') and var_name.endswith('__'):
                        raise SecurityError(
                            f"Access to dunder names is forbidden: {var_name}",
                            context=code_str[:ERROR_CONTEXT_MAX_LENGTH]
                        )

            # Compile and execute
            code = compile(node, '<string>', 'exec')
            exec(code, {"__builtins__": {}}, context)

        except SecurityError:
            raise
        except Exception as e:
            raise DirectiveError(f"Error executing @python block: {e}", context=code_str[:ERROR_CONTEXT_MAX_LENGTH])

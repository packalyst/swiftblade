"""
Template Compiler
Compiles templates to optimized intermediate representation
"""

import re
import hashlib
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache


class TokenType(Enum):
    """Token types for template compilation"""
    TEXT = "text"
    VARIABLE = "variable"
    RAW_VARIABLE = "raw_variable"
    DIRECTIVE = "directive"
    COMMENT = "comment"


@dataclass
class Token:
    """Represents a parsed token"""
    type: TokenType
    content: str
    line: int
    col: int


class TemplateCompiler:
    """
    Compiles templates into token streams for faster rendering
    """

    # Regex patterns for tokenization
    PATTERNS = {
        'comment': r'\{\{--[\s\S]*?--\}\}',
        'raw_variable': r'\{!!\s*(.*?)\s*!!\}',
        'variable': r'\{\{\s*(.*?)\s*\}\}',
        'directive': r'@(\w+)(?:\((.*?)\))?',
    }

    def __init__(self):
        self.compiled_cache: Dict[str, List[Token]] = {}

    @staticmethod
    @lru_cache(maxsize=1000)
    def get_template_hash(template: str) -> str:
        """
        Generate hash for template content (cached)

        Uses LRU cache to avoid recomputing hashes for the same template.
        Especially useful when the same template is rendered multiple times.
        """
        return hashlib.sha256(template.encode()).hexdigest()

    def tokenize(self, template: str) -> List[Token]:
        """
        Tokenize template into a list of tokens

        Args:
            template: Raw template string

        Returns:
            List of tokens
        """
        template_hash = self.get_template_hash(template)

        # Return cached if available
        if template_hash in self.compiled_cache:
            return self.compiled_cache[template_hash]

        tokens = []
        pos = 0
        line = 1
        col = 1

        # Combined pattern matching all token types
        combined_pattern = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.PATTERNS.items())
        regex = re.compile(combined_pattern, re.DOTALL)

        for match in regex.finditer(template):
            start = match.start()

            # Add text before this match
            if pos < start:
                text = template[pos:start]
                if text:
                    tokens.append(Token(TokenType.TEXT, text, line, col))
                    # Update line/col
                    line += text.count('\n')
                    if '\n' in text:
                        col = len(text.split('\n')[-1]) + 1
                    else:
                        col += len(text)

            # Determine token type
            if match.lastgroup == 'comment':
                token_type = TokenType.COMMENT
                content = match.group(0)
            elif match.lastgroup == 'raw_variable':
                token_type = TokenType.RAW_VARIABLE
                content = match.group(1).strip()
            elif match.lastgroup == 'variable':
                token_type = TokenType.VARIABLE
                content = match.group(1).strip()
            elif match.lastgroup == 'directive':
                token_type = TokenType.DIRECTIVE
                directive_name = match.group(1)
                directive_args = match.group(2) if match.group(2) else ''
                content = f"{directive_name}:{directive_args}"
            else:
                continue

            tokens.append(Token(token_type, content, line, col))

            # Update position and line/col
            pos = match.end()
            matched_text = match.group(0)
            line += matched_text.count('\n')
            if '\n' in matched_text:
                col = len(matched_text.split('\n')[-1]) + 1
            else:
                col += len(matched_text)

        # Add remaining text
        if pos < len(template):
            text = template[pos:]
            if text:
                tokens.append(Token(TokenType.TEXT, text, line, col))

        # Cache compiled tokens
        self.compiled_cache[template_hash] = tokens

        return tokens

    def extract_directives(self, template: str) -> List[Tuple[str, str, int]]:
        """
        Extract all directives from template

        Returns:
            List of (directive_name, args, line_number)
        """
        directives = []
        lines = template.split('\n')

        for line_num, line in enumerate(lines, 1):
            for match in re.finditer(self.PATTERNS['directive'], line):
                directive_name = match.group(1)
                directive_args = match.group(2) if match.group(2) else ''
                directives.append((directive_name, directive_args, line_num))

        return directives

    def find_matching_end(self, tokens: List[Token], start_idx: int, start_directive: str, end_directive: str) -> int:
        """
        Find matching end directive for a start directive

        Args:
            tokens: List of tokens
            start_idx: Index of start directive
            start_directive: Start directive name (e.g., 'if')
            end_directive: End directive name (e.g., 'endif')

        Returns:
            Index of matching end directive

        Raises:
            CompilationError: If no matching end found
        """
        depth = 1
        for i in range(start_idx + 1, len(tokens)):
            if tokens[i].type == TokenType.DIRECTIVE:
                directive_name = tokens[i].content.split(':')[0]
                if directive_name == start_directive:
                    depth += 1
                elif directive_name == end_directive:
                    depth -= 1
                    if depth == 0:
                        return i

        from .exceptions import CompilationError
        raise CompilationError(
            f"No matching @{end_directive} for @{start_directive}",
            line_number=tokens[start_idx].line
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get compiler statistics"""
        return {
            "cached_templates": len(self.compiled_cache),
            "memory_usage": sum(len(str(t)) for tokens in self.compiled_cache.values() for t in tokens),
        }

    def clear_cache(self):
        """Clear compiled template cache"""
        self.compiled_cache.clear()
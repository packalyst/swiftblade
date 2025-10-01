"""
Component Base Handler
Base class for component handlers with shared logic
"""

import os
import re
from typing import Dict, Any, Optional

from .base import BaseHandler
from ..exceptions import SecurityError, TemplateNotFoundException
from ..constants import (
    VALID_TEMPLATE_EXTENSIONS,
    COMPONENT_NAME_PATTERN,
    COMPONENT_SUBDIR,
)


class ComponentBase(BaseHandler):
    """
    Base class for component handlers
    Provides shared functionality for both legacy and modern component systems
    """

    def _validate_component_name(self, name: str):
        """
        Validate component name (whitelist approach)

        Args:
            name: Component name to validate

        Raises:
            SecurityError: If name is invalid or contains path traversal
        """
        # Security: Validate component name format (whitelist)
        if not COMPONENT_NAME_PATTERN.match(name):
            raise SecurityError(
                f"Invalid component name: '{name}'. "
                f"Only alphanumeric characters, hyphens, and dots are allowed."
            )

        # Security: Additional path traversal checks
        if '..' in name or os.path.isabs(name):
            raise SecurityError(f"Invalid component name: {name}")

        if name.startswith('/') or name.startswith('\\'):
            raise SecurityError(f"Component name cannot be absolute: {name}")

    def _resolve_component_path(
        self,
        component_name: str,
        subdir: Optional[str] = None,
        add_extension: bool = True
    ) -> str:
        """
        Resolve component name to full file path

        Args:
            component_name: Name of the component
            subdir: Optional subdirectory (e.g., COMPONENT_SUBDIR for X-components)
            add_extension: Whether to auto-append file extension

        Returns:
            Full path to component file

        Raises:
            TemplateNotFoundException: If component file not found
        """
        # Validate name first
        self._validate_component_name(component_name)

        # Build path
        if subdir:
            # For X-components: convert dots to slashes for nested components
            # e.g., 'alert.danger' -> 'components/alert/danger.html'
            component_path = component_name.replace('.', '/')
            component_file = os.path.join(self.engine.template_dir, subdir, component_path)
        else:
            # For legacy components: use name as-is
            component_file = os.path.join(self.engine.template_dir, component_name)

        # Auto-append extension if not present
        if add_extension and not any(component_file.endswith(ext) for ext in VALID_TEMPLATE_EXTENSIONS):
            component_file += self.engine.file_extension

        # Check if file exists
        if not os.path.exists(component_file):
            raise TemplateNotFoundException(
                f"Component '{component_name}' not found at {component_file}",
                template_name=component_name
            )

        return component_file

    def _load_component_template(self, component_path: str) -> str:
        """
        Load component template from file

        Args:
            component_path: Full path to component file

        Returns:
            Component template content
        """
        with open(component_path, "r", encoding=self.engine.encoding) as f:
            return f.read()

    def _extract_slots_generic(
        self,
        body: str,
        slot_pattern: re.Pattern,
        context: Dict[str, Any],
        parser,
        process_content: bool = True
    ) -> Dict[str, str]:
        """
        Generic slot extraction using provided regex pattern

        Args:
            body: Component body content
            slot_pattern: Compiled regex pattern for matching slots
            context: Template context
            parser: Template parser instance
            process_content: Whether to process slot content through parser

        Returns:
            Dictionary of slot name -> content
        """
        slots = {}

        for match in slot_pattern.finditer(body):
            # Extract slot name and content based on pattern groups
            # Most patterns have: (1) quote, (2) name, (3) optional attrs, (4) content
            if match.lastindex >= 2:
                slot_name = match.group(2).strip().replace('-', '_')
                # Content is usually the last group
                slot_content = match.group(match.lastindex)

                # Process slot content if requested
                if process_content:
                    processed_content = parser.process_template(slot_content, context)
                else:
                    processed_content = slot_content

                slots[slot_name] = processed_content

        return slots

    def _extract_default_slot(self, body: str, slot_pattern: re.Pattern) -> str:
        """
        Extract default slot (content not in named slots)

        Args:
            body: Component body content
            slot_pattern: Compiled regex pattern for matching slots

        Returns:
            Default slot content (remaining after removing named slots)
        """
        # Remove all named slots
        remaining = slot_pattern.sub('', body)
        return remaining.strip()

    def _merge_component_context(
        self,
        base_context: Dict[str, Any],
        component_data: Dict[str, Any],
        slots: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Merge contexts for component rendering

        Args:
            base_context: Base template context
            component_data: Component-specific data (from props or attributes)
            slots: Extracted slots

        Returns:
            Merged context dictionary
        """
        # Create copy to avoid modifying original
        merged = base_context.copy()

        # Add component data
        merged.update(component_data)

        # Add slots
        merged.update(slots)

        return merged

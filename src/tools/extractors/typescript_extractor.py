"""
TypeScript/React code extractor for analyzing UI component files.

Extracts component props, state, event handlers, hooks, and child components
from TypeScript/React/TSX source files.
"""

import re
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from .base_extractor import (
    BaseExtractor, ExtractedData, ExtractedComponent, ExtractedProp
)


logger = logging.getLogger(__name__)


class TypeScriptExtractor(BaseExtractor):
    """Extractor for TypeScript and React/TSX source code."""
    
    def can_extract(self, file_path: Path) -> bool:
        """Check if file is a TypeScript/React source file."""
        return file_path.suffix.lower() in ['.ts', '.tsx', '.jsx', '.js']
    
    def extract(self, file_path: Path) -> ExtractedData:
        """Extract information from TypeScript/React source file."""
        logger.info(f"Extracting TypeScript data from {file_path}")
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise Exception(f"Failed to read file: {e}")
        
        # Initialize extracted data
        data = ExtractedData(language='typescript', file_path=str(file_path))
        
        try:
            # Extract component
            component = self._extract_component(content)
            if component:
                data.components = [component]
            
        except Exception as e:
            data.extraction_errors.append(f"Extraction error: {str(e)}")
            logger.error(f"Error extracting from {file_path}: {e}", exc_info=True)
        
        return data
    
    def _extract_component(self, content: str) -> Optional[ExtractedComponent]:
        """Extract React component from TypeScript code."""
        
        # Try to find component name (function or class component)
        component_name = self._find_component_name(content)
        if not component_name:
            logger.warning("Could not find component name")
            return None
        
        # Extract props interface/type
        props = self._extract_props(content, component_name)
        
        # Extract state variables
        state_variables = self._extract_state(content)
        
        # Extract event handlers
        event_handlers = self._extract_event_handlers(content)
        
        # Extract hooks used
        hooks = self._extract_hooks(content)
        
        # Extract child components
        child_components = self._extract_child_components(content)
        
        # Extract CSS classes
        css_classes = self._extract_css_classes(content)
        
        component = ExtractedComponent(
            name=component_name,
            props=props,
            state_variables=state_variables,
            event_handlers=event_handlers,
            hooks=hooks,
            child_components=child_components,
            css_classes=css_classes
        )
        
        logger.debug(f"Extracted component: {component_name} with {len(props)} props")
        
        return component
    
    def _find_component_name(self, content: str) -> Optional[str]:
        """Find the main component name in the file."""
        
        # Try function component: export default function ComponentName
        match = re.search(r'export\s+(?:default\s+)?function\s+(\w+)', content)
        if match:
            return match.group(1)
        
        # Try arrow function: export const ComponentName = () =>
        match = re.search(r'export\s+(?:default\s+)?const\s+(\w+)\s*[=:]\s*\([^)]*\)\s*=>', content)
        if match:
            return match.group(1)
        
        # Try class component: export class ComponentName
        match = re.search(r'export\s+(?:default\s+)?class\s+(\w+)', content)
        if match:
            return match.group(1)
        
        # Try named export at the bottom: export default ComponentName
        match = re.search(r'export\s+default\s+(\w+)', content)
        if match:
            return match.group(1)
        
        return None
    
    def _extract_props(self, content: str, component_name: str) -> List[ExtractedProp]:
        """Extract props interface or type definition."""
        props = []
        
        # Try to find props interface: interface ComponentNameProps
        props_interface_pattern = rf'(?:interface|type)\s+{component_name}Props\s*[={{]\s*([^}}]+)'
        match = re.search(props_interface_pattern, content, re.DOTALL)
        
        if not match:
            # Try generic Props pattern
            match = re.search(r'(?:interface|type)\s+Props\s*[={]\s*([^}]+)', content, re.DOTALL)
        
        if match:
            props_body = match.group(1)
            props = self._parse_props_interface(props_body)
        else:
            # Try inline props in function signature
            func_pattern = rf'function\s+{component_name}\s*[<(]{{[^:}}]+:\s*{{([^}}]+)}}'
            match = re.search(func_pattern, content, re.DOTALL)
            if match:
                props_body = match.group(1)
                props = self._parse_props_interface(props_body)
        
        return props
    
    def _parse_props_interface(self, props_body: str) -> List[ExtractedProp]:
        """Parse props from interface body."""
        props = []
        
        # Pattern: propName?: Type = defaultValue // description
        # or: propName: Type
        prop_pattern = r'(\w+)(\??):\s*([^;,\n]+?)(?:=([^;,\n]+?))?(?://(.*))?[;,\n]'
        
        for match in re.finditer(prop_pattern, props_body):
            prop_name = match.group(1)
            is_optional = match.group(2) == '?'
            prop_type = match.group(3).strip()
            default_value = match.group(4).strip() if match.group(4) else None
            description = match.group(5).strip() if match.group(5) else None
            
            # Skip common non-prop patterns
            if prop_name in ['extends', 'export', 'import', 'const', 'let', 'var']:
                continue
            
            prop = ExtractedProp(
                name=prop_name,
                type=prop_type,
                is_required=not is_optional,
                default_value=default_value,
                description=description
            )
            props.append(prop)
            
            logger.debug(f"Extracted prop: {prop_name}: {prop_type}")
        
        return props
    
    def _extract_state(self, content: str) -> List[Dict[str, Any]]:
        """Extract state variables (useState, useReducer)."""
        state_vars = []
        
        # Pattern: const [stateName, setStateName] = useState<Type>(initialValue)
        state_pattern = r'const\s+\[(\w+),\s*\w+\]\s*=\s*useState(?:<([^>]+)>)?\(([^)]*)\)'
        
        for match in re.finditer(state_pattern, content):
            state_name = match.group(1)
            state_type = match.group(2) or 'unknown'
            initial_value = match.group(3).strip()
            
            state_vars.append({
                'name': state_name,
                'type': state_type,
                'initial_value': initial_value,
                'hook': 'useState'
            })
            
            logger.debug(f"Extracted state: {state_name}: {state_type}")
        
        # Pattern: const [state, dispatch] = useReducer(reducer, initialState)
        reducer_pattern = r'const\s+\[(\w+),\s*\w+\]\s*=\s*useReducer'
        
        for match in re.finditer(reducer_pattern, content):
            state_name = match.group(1)
            
            state_vars.append({
                'name': state_name,
                'type': 'reducer state',
                'hook': 'useReducer'
            })
            
            logger.debug(f"Extracted reducer state: {state_name}")
        
        return state_vars
    
    def _extract_event_handlers(self, content: str) -> List[str]:
        """Extract event handler functions."""
        handlers = []
        
        # Pattern: const handleEventName = (...) =>
        handler_pattern = r'const\s+(handle\w+|on\w+)\s*=\s*(?:\([^)]*\)\s*=>|function)'
        
        for match in re.finditer(handler_pattern, content):
            handler_name = match.group(1)
            handlers.append(handler_name)
            
            logger.debug(f"Extracted handler: {handler_name}")
        
        # Pattern: function handleEventName(...)
        func_handler_pattern = r'function\s+(handle\w+|on\w+)\s*\('
        
        for match in re.finditer(func_handler_pattern, content):
            handler_name = match.group(1)
            if handler_name not in handlers:
                handlers.append(handler_name)
                logger.debug(f"Extracted handler: {handler_name}")
        
        return handlers
    
    def _extract_hooks(self, content: str) -> List[str]:
        """Extract React hooks used in the component."""
        hooks = set()
        
        # Common hooks
        hook_names = [
            'useState', 'useEffect', 'useContext', 'useReducer', 'useCallback',
            'useMemo', 'useRef', 'useImperativeHandle', 'useLayoutEffect',
            'useDebugValue', 'useId', 'useDeferredValue', 'useTransition',
            'useSyncExternalStore', 'useQuery', 'useMutation'
        ]
        
        for hook in hook_names:
            if re.search(rf'\b{hook}\s*\(', content):
                hooks.add(hook)
                logger.debug(f"Extracted hook: {hook}")
        
        # Custom hooks: use* pattern
        custom_hook_pattern = r'(use[A-Z]\w+)\s*\('
        for match in re.finditer(custom_hook_pattern, content):
            hook_name = match.group(1)
            if hook_name not in hook_names:  # Skip if already counted
                hooks.add(hook_name)
                logger.debug(f"Extracted custom hook: {hook_name}")
        
        return sorted(list(hooks))
    
    def _extract_child_components(self, content: str) -> List[str]:
        """Extract child components used in JSX."""
        components = set()
        
        # Pattern: <ComponentName> or <ComponentName/>
        component_pattern = r'<([A-Z]\w+)[\s/>]'
        
        for match in re.finditer(component_pattern, content):
            comp_name = match.group(1)
            # Skip HTML elements (lowercase) and common React elements
            if comp_name[0].isupper() and comp_name not in ['React', 'Fragment']:
                components.add(comp_name)
                logger.debug(f"Extracted child component: {comp_name}")
        
        return sorted(list(components))
    
    def _extract_css_classes(self, content: str) -> List[str]:
        """Extract CSS classes used in className."""
        classes = set()
        
        # Pattern: className="class-name" or className={styles.className}
        # Simple string className
        simple_pattern = r'className=["\']([^"\']+)["\']'
        for match in re.finditer(simple_pattern, content):
            class_names = match.group(1).split()
            classes.update(class_names)
        
        # CSS Modules: styles.className
        module_pattern = r'styles\.(\w+)'
        for match in re.finditer(module_pattern, content):
            class_name = match.group(1)
            classes.add(f"styles.{class_name}")
        
        # Template literals with classes
        template_pattern = r'className=\{`([^`]*)`\}'
        for match in re.finditer(template_pattern, content):
            template_content = match.group(1)
            # Extract static class names from template
            static_classes = re.findall(r'[\w-]+', template_content)
            for cls in static_classes:
                if not cls.startswith('$'):  # Exclude template variables
                    classes.add(cls)
        
        if classes:
            logger.debug(f"Extracted {len(classes)} CSS classes")
        
        return sorted(list(classes))

"""Frontend Agent for UI generation and user experience.

The Frontend Agent is responsible for:
- Generating responsive UI components
- Ensuring accessibility standards
- Creating modern, aesthetic designs
- Implementing client-side logic
- Optimizing user experience
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import litellm
import structlog

from noode.core.base_agent import Action, BaseAgent, Result

logger = structlog.get_logger()


class UIFramework(Enum):
    """Supported UI frameworks."""
    
    REACT = "react"
    VUE = "vue"
    SVELTE = "svelte"
    VANILLA = "vanilla"
    HTMX = "htmx"


class ComponentType(Enum):
    """Types of UI components."""
    
    PAGE = "page"
    LAYOUT = "layout"
    FORM = "form"
    TABLE = "table"
    CARD = "card"
    MODAL = "modal"
    NAVIGATION = "navigation"
    BUTTON = "button"
    INPUT = "input"
    CUSTOM = "custom"


@dataclass
class UIComponent:
    """A generated UI component."""
    
    name: str
    component_type: ComponentType
    framework: UIFramework
    code: str
    styles: str
    props: dict[str, str]
    children: list[str] = field(default_factory=list)
    accessibility_notes: list[str] = field(default_factory=list)


@dataclass
class DesignSpec:
    """Design specification for UI generation."""
    
    description: str
    color_scheme: dict[str, str] = field(default_factory=dict)
    typography: dict[str, str] = field(default_factory=dict)
    spacing: str = "relaxed"
    style: str = "modern"
    dark_mode: bool = True


@dataclass
class UIGenerationResult:
    """Result of UI generation."""
    
    components: list[UIComponent]
    main_file: str
    style_file: str
    dependencies: list[str]
    preview_html: str


class FrontendAgent(BaseAgent):
    """Agent specialized in frontend development.
    
    Creates beautiful, accessible, and responsive user interfaces
    following modern design principles.
    """
    
    # Design tokens for consistent styling
    DEFAULT_DESIGN_TOKENS = {
        "colors": {
            "primary": "#6366f1",
            "secondary": "#8b5cf6",
            "background": "#0f172a",
            "surface": "#1e293b",
            "text": "#f8fafc",
            "muted": "#94a3b8",
            "success": "#22c55e",
            "warning": "#eab308",
            "error": "#ef4444",
        },
        "spacing": {
            "xs": "0.25rem",
            "sm": "0.5rem",
            "md": "1rem",
            "lg": "1.5rem",
            "xl": "2rem",
        },
        "radius": {
            "sm": "0.25rem",
            "md": "0.5rem",
            "lg": "1rem",
            "full": "9999px",
        },
    }
    
    def __init__(
        self,
        name: str = "frontend_agent",
        model: str = "gpt-4o",
        framework: UIFramework = UIFramework.REACT,
    ) -> None:
        """Initialize the frontend agent.
        
        Args:
            name: Agent name
            model: LLM model to use
            framework: Default UI framework
        """
        super().__init__(
            name=name,
            role="Frontend Development and UI/UX Specialist",
            capabilities=[
                "ui component generation",
                "responsive design",
                "accessibility compliance",
                "animation and transitions",
                "state management",
                "styling and theming",
            ],
            model=model,
            confidence_threshold=0.7,
        )
        self.framework = framework
        self.design_tokens = self.DEFAULT_DESIGN_TOKENS.copy()
    
    async def act(self, action: Action) -> Result:
        """Execute a frontend action.
        
        Args:
            action: The action to execute
            
        Returns:
            Result of the frontend generation
        """
        start_time = datetime.now()
        
        try:
            if action.action_type == "generate_component":
                component = await self.generate_component(
                    description=action.parameters.get("description", ""),
                    component_type=ComponentType(
                        action.parameters.get("type", "custom")
                    ),
                    design_spec=action.parameters.get("design_spec"),
                )
                return Result(
                    success=True,
                    output=component,
                    duration_ms=(datetime.now() - start_time).total_seconds() * 1000,
                )
            
            elif action.action_type == "generate_page":
                result = await self.generate_page(
                    description=action.parameters.get("description", ""),
                    sections=action.parameters.get("sections", []),
                    design_spec=action.parameters.get("design_spec"),
                )
                return Result(
                    success=True,
                    output=result,
                    duration_ms=(datetime.now() - start_time).total_seconds() * 1000,
                )
            
            elif action.action_type == "improve_accessibility":
                improved = await self.improve_accessibility(
                    code=action.parameters.get("code", ""),
                    framework=action.parameters.get("framework", "react"),
                )
                return Result(
                    success=True,
                    output=improved,
                    duration_ms=(datetime.now() - start_time).total_seconds() * 1000,
                )
            
            else:
                return Result(
                    success=False,
                    output=None,
                    error=f"Unknown action type: {action.action_type}",
                )
                
        except Exception as e:
            logger.error("frontend_action_failed", error=str(e))
            return Result(
                success=False,
                output=None,
                error=str(e),
                duration_ms=(datetime.now() - start_time).total_seconds() * 1000,
            )
    
    async def generate_component(
        self,
        description: str,
        component_type: ComponentType,
        design_spec: DesignSpec | None = None,
    ) -> UIComponent:
        """Generate a UI component.
        
        Args:
            description: What the component should do
            component_type: Type of component
            design_spec: Design specification
            
        Returns:
            Generated UI component
        """
        design_spec = design_spec or DesignSpec(description=description)
        
        logger.info(
            "generating_component",
            type=component_type.value,
            description=description[:50],
        )
        
        response = await litellm.acompletion(
            model=self.model,
            messages=[{
                "role": "system",
                "content": f"""{self.system_prompt}

You are generating a {self.framework.value.upper()} component.
Follow these design principles:
- Modern, clean aesthetic with glassmorphism accents
- Dark mode by default with proper contrast
- Responsive layout using CSS Grid/Flexbox
- Smooth transitions (0.2s ease)
- Accessible (WCAG 2.1 AA compliant)

Design tokens:
{self.design_tokens}""",
            }, {
                "role": "user",
                "content": f"""Generate a {component_type.value} component:

Description: {description}

Design style: {design_spec.style}
Color scheme: {design_spec.color_scheme or 'Use default tokens'}
Dark mode: {design_spec.dark_mode}

Provide:
1. Complete component code
2. CSS/styles (use CSS modules or styled-components)
3. Props interface
4. Accessibility features added""",
            }],
            temperature=0.7,
        )
        
        content = response.choices[0].message.content or ""
        
        # Parse component from response
        code, styles, props = self._parse_component_response(content)
        
        return UIComponent(
            name=self._generate_component_name(description),
            component_type=component_type,
            framework=self.framework,
            code=code,
            styles=styles,
            props=props,
            accessibility_notes=self._extract_accessibility_notes(content),
        )
    
    async def generate_page(
        self,
        description: str,
        sections: list[str],
        design_spec: DesignSpec | None = None,
    ) -> UIGenerationResult:
        """Generate a complete page with multiple components.
        
        Args:
            description: Page description
            sections: List of sections to include
            design_spec: Design specification
            
        Returns:
            Complete UI generation result
        """
        logger.info("generating_page", description=description[:50])
        
        components: list[UIComponent] = []
        
        # Generate layout component first
        layout = await self.generate_component(
            description=f"Page layout for: {description}",
            component_type=ComponentType.LAYOUT,
            design_spec=design_spec,
        )
        components.append(layout)
        
        # Generate each section
        for section in sections:
            component = await self.generate_component(
                description=section,
                component_type=ComponentType.CUSTOM,
                design_spec=design_spec,
            )
            components.append(component)
        
        # Compose main file
        main_file = self._compose_page(components)
        style_file = self._compose_styles(components)
        
        return UIGenerationResult(
            components=components,
            main_file=main_file,
            style_file=style_file,
            dependencies=self._get_dependencies(),
            preview_html=self._generate_preview_html(main_file, style_file),
        )
    
    async def improve_accessibility(
        self,
        code: str,
        framework: str = "react",
    ) -> dict[str, Any]:
        """Improve accessibility of existing code.
        
        Args:
            code: Existing component code
            framework: UI framework
            
        Returns:
            Improved code with changes documented
        """
        response = await litellm.acompletion(
            model=self.model,
            messages=[{
                "role": "system",
                "content": """You are an accessibility expert. Improve code to meet 
WCAG 2.1 AA standards. Focus on:
- Semantic HTML elements
- ARIA labels and roles
- Keyboard navigation
- Focus management
- Color contrast
- Screen reader compatibility""",
            }, {
                "role": "user",
                "content": f"""Improve the accessibility of this {framework} code:

```
{code}
```

Provide:
1. Improved code
2. List of changes made
3. Any remaining concerns""",
            }],
            temperature=0.3,
        )
        
        content = response.choices[0].message.content or ""
        
        return {
            "improved_code": self._extract_code_block(content),
            "changes": self._extract_list(content, "changes"),
            "concerns": self._extract_list(content, "concerns"),
        }
    
    async def generate_css_variables(
        self,
        design_spec: DesignSpec,
    ) -> str:
        """Generate CSS custom properties from design spec."""
        colors = design_spec.color_scheme or self.design_tokens["colors"]
        
        css_vars = [":root {"]
        for name, value in colors.items():
            css_vars.append(f"  --color-{name}: {value};")
        
        for name, value in self.design_tokens["spacing"].items():
            css_vars.append(f"  --spacing-{name}: {value};")
        
        for name, value in self.design_tokens["radius"].items():
            css_vars.append(f"  --radius-{name}: {value};")
        
        css_vars.append("}")
        
        return "\n".join(css_vars)
    
    def _parse_component_response(
        self,
        content: str,
    ) -> tuple[str, str, dict[str, str]]:
        """Parse component code, styles, and props from LLM response."""
        code = self._extract_code_block(content, "tsx") or \
               self._extract_code_block(content, "jsx") or \
               self._extract_code_block(content, "javascript") or ""
        
        styles = self._extract_code_block(content, "css") or ""
        
        # Extract props
        props = {}
        if "Props" in content or "props" in content:
            lines = content.split("\n")
            for line in lines:
                if ":" in line and ("string" in line or "number" in line or "boolean" in line):
                    parts = line.split(":")
                    if len(parts) >= 2:
                        prop_name = parts[0].strip().replace("- ", "")
                        prop_type = parts[1].strip().split()[0]
                        props[prop_name] = prop_type
        
        return code, styles, props
    
    def _extract_code_block(
        self,
        content: str,
        language: str = "",
    ) -> str:
        """Extract code block from markdown response."""
        import re
        
        if language:
            pattern = rf"```{language}\n(.*?)```"
        else:
            pattern = r"```\w*\n(.*?)```"
        
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else ""
    
    def _extract_list(self, content: str, section: str) -> list[str]:
        """Extract a list from content after a section header."""
        lines = content.split("\n")
        items = []
        in_section = False
        
        for line in lines:
            if section.lower() in line.lower():
                in_section = True
                continue
            
            if in_section:
                if line.strip().startswith(("-", "*", "•")) or (
                    len(line) > 2 and line[0].isdigit()
                ):
                    items.append(line.strip().lstrip("-*•0123456789.) "))
                elif line.strip() and not line.startswith(" "):
                    break
        
        return items
    
    def _extract_accessibility_notes(self, content: str) -> list[str]:
        """Extract accessibility-related notes from response."""
        notes = []
        keywords = ["aria", "role=", "tabindex", "keyboard", "screen reader", "label"]
        
        for line in content.split("\n"):
            if any(kw in line.lower() for kw in keywords):
                notes.append(line.strip())
        
        return notes[:5]
    
    def _generate_component_name(self, description: str) -> str:
        """Generate a component name from description."""
        words = description.split()[:3]
        return "".join(w.capitalize() for w in words if w.isalnum())
    
    def _compose_page(self, components: list[UIComponent]) -> str:
        """Compose a page from multiple components."""
        imports = []
        jsx_parts = []
        
        for comp in components:
            imports.append(f"import {comp.name} from './{comp.name}';")
            jsx_parts.append(f"      <{comp.name} />")
        
        return f"""import React from 'react';
{chr(10).join(imports)}
import './styles.css';

export default function Page() {{
  return (
    <div className="page">
{chr(10).join(jsx_parts)}
    </div>
  );
}}
"""
    
    def _compose_styles(self, components: list[UIComponent]) -> str:
        """Compose styles from multiple components."""
        styles = [self._generate_base_styles()]
        
        for comp in components:
            if comp.styles:
                styles.append(f"/* {comp.name} */")
                styles.append(comp.styles)
        
        return "\n\n".join(styles)
    
    def _generate_base_styles(self) -> str:
        """Generate base CSS with design tokens."""
        return f"""/* Base Styles */
:root {{
  --color-primary: {self.design_tokens['colors']['primary']};
  --color-secondary: {self.design_tokens['colors']['secondary']};
  --color-background: {self.design_tokens['colors']['background']};
  --color-surface: {self.design_tokens['colors']['surface']};
  --color-text: {self.design_tokens['colors']['text']};
}}

* {{
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}}

body {{
  font-family: 'Inter', system-ui, sans-serif;
  background: var(--color-background);
  color: var(--color-text);
  line-height: 1.6;
}}

.page {{
  min-height: 100vh;
  padding: 2rem;
}}
"""
    
    def _get_dependencies(self) -> list[str]:
        """Get required dependencies for the framework."""
        deps = {
            UIFramework.REACT: ["react", "react-dom"],
            UIFramework.VUE: ["vue"],
            UIFramework.SVELTE: ["svelte"],
            UIFramework.VANILLA: [],
            UIFramework.HTMX: ["htmx.org"],
        }
        return deps.get(self.framework, [])
    
    def _generate_preview_html(self, main_file: str, style_file: str) -> str:
        """Generate preview HTML for the page."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Preview</title>
  <style>{style_file}</style>
</head>
<body>
  <div id="root"></div>
  <script type="module">
    // Preview would render here
  </script>
</body>
</html>
"""

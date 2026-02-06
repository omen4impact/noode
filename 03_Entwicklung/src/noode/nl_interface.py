"""Natural Language Interface for task interpretation.

Converts user natural language input into structured agent tasks.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import litellm
import structlog

logger = structlog.get_logger()


class TaskIntent(Enum):
    """Detected user intent."""
    
    CREATE_PROJECT = "create_project"
    GENERATE_UI = "generate_ui"
    GENERATE_API = "generate_api"
    MODIFY_CODE = "modify_code"
    FIX_BUG = "fix_bug"
    ADD_FEATURE = "add_feature"
    SECURITY_REVIEW = "security_review"
    EXPLAIN = "explain"
    RESEARCH = "research"
    UNKNOWN = "unknown"


@dataclass
class ParsedTask:
    """A parsed task from natural language."""
    
    intent: TaskIntent
    description: str
    entities: dict[str, str] = field(default_factory=dict)
    parameters: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    suggested_agents: list[str] = field(default_factory=list)
    clarification_needed: str | None = None


@dataclass
class Conversation:
    """Tracks conversation context."""
    
    messages: list[dict[str, str]] = field(default_factory=list)
    current_project: str | None = None
    current_file: str | None = None
    pending_task: ParsedTask | None = None


class NaturalLanguageInterface:
    """Parse and interpret natural language commands.
    
    Provides a conversational interface for non-technical users
    to interact with the Noode agent system.
    """
    
    # Intent detection keywords
    INTENT_KEYWORDS = {
        TaskIntent.CREATE_PROJECT: ["erstelle projekt", "create project", "neues projekt", "new project", "starte projekt"],
        TaskIntent.GENERATE_UI: ["ui", "seite", "page", "formular", "form", "button", "modal", "component", "frontend"],
        TaskIntent.GENERATE_API: ["api", "endpoint", "backend", "service", "datenbank", "database"],
        TaskIntent.FIX_BUG: ["bug", "fehler", "fix", "repariere", "funktioniert nicht", "broken", "error"],
        TaskIntent.ADD_FEATURE: ["feature", "funktion", "hinzufügen", "add", "erweitere", "neu"],
        TaskIntent.SECURITY_REVIEW: ["sicherheit", "security", "prüfe", "review", "audit", "vulnerability"],
        TaskIntent.EXPLAIN: ["erkläre", "explain", "was ist", "what is", "wie funktioniert", "how does"],
        TaskIntent.RESEARCH: ["recherche", "research", "best practice", "wie sollte", "empfehlung"],
    }
    
    def __init__(
        self,
        model: str = "gpt-4o",
    ) -> None:
        """Initialize the NL interface.
        
        Args:
            model: LLM model to use
        """
        self.model = model
        self.conversation = Conversation()
    
    async def parse(self, user_input: str) -> ParsedTask:
        """Parse natural language input into a structured task.
        
        Args:
            user_input: Raw user input
            
        Returns:
            Parsed task with intent and parameters
        """
        logger.info("parsing_input", input=user_input[:50])
        
        # Quick intent detection from keywords
        quick_intent = self._detect_intent_keywords(user_input)
        
        # LLM-based parsing for detailed understanding
        parsed = await self._llm_parse(user_input, quick_intent)
        
        # Add to conversation history
        self.conversation.messages.append({
            "role": "user",
            "content": user_input,
        })
        
        return parsed
    
    async def clarify(self, question: str) -> str:
        """Ask a clarification question.
        
        Args:
            question: Question to ask user
            
        Returns:
            Formatted question
        """
        self.conversation.messages.append({
            "role": "assistant",
            "content": question,
        })
        return question
    
    async def respond(self, task_result: Any) -> str:
        """Generate a natural language response for task result.
        
        Args:
            task_result: Result from task execution
            
        Returns:
            Natural language response
        """
        response = await litellm.acompletion(
            model=self.model,
            messages=[{
                "role": "system",
                "content": """Du bist Noode, ein freundlicher AI-Entwicklungsassistent.
Erkläre Ergebnisse verständlich für nicht-technische Nutzer.
Verwende einfache Sprache und Emojis.
Sei prägnant aber informativ.""",
            }, {
                "role": "user",
                "content": f"Erkläre dieses Ergebnis dem Nutzer:\n{task_result}",
            }],
            temperature=0.7,
        )
        
        content = response.choices[0].message.content or ""
        
        self.conversation.messages.append({
            "role": "assistant",
            "content": content,
        })
        
        return content
    
    def _detect_intent_keywords(self, text: str) -> TaskIntent:
        """Quick intent detection using keywords."""
        text_lower = text.lower()
        
        for intent, keywords in self.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return intent
        
        return TaskIntent.UNKNOWN
    
    async def _llm_parse(
        self,
        user_input: str,
        quick_intent: TaskIntent,
    ) -> ParsedTask:
        """Use LLM for detailed parsing."""
        
        # Build context from conversation
        context = ""
        if self.conversation.current_project:
            context += f"Current project: {self.conversation.current_project}\n"
        if self.conversation.current_file:
            context += f"Current file: {self.conversation.current_file}\n"
        
        response = await litellm.acompletion(
            model=self.model,
            messages=[{
                "role": "system",
                "content": """Du bist ein Task-Parser für eine AI-Entwicklungsplattform.
Analysiere die Nutzeranfrage und extrahiere:
1. Intent (was will der Nutzer?)
2. Entitäten (Namen, Typen, Dateien)
3. Parameter (Details, Anforderungen)
4. Welche Agents sollten die Aufgabe bearbeiten?

Antworte im Format:
INTENT: [intent]
ENTITIES: [key=value, ...]
PARAMETERS: [key=value, ...]
AGENTS: [agent1, agent2]
CONFIDENCE: [0.0-1.0]
CLARIFICATION: [frage wenn unklar, sonst leer]""",
            }, {
                "role": "user",
                "content": f"""Kontext: {context}

Nutzeranfrage: {user_input}

Vorläufiger Intent (aus Keywords): {quick_intent.value}""",
            }],
            temperature=0.3,
        )
        
        content = response.choices[0].message.content or ""
        
        return self._parse_llm_response(content, user_input, quick_intent)
    
    def _parse_llm_response(
        self,
        response: str,
        original_input: str,
        fallback_intent: TaskIntent,
    ) -> ParsedTask:
        """Parse structured response from LLM."""
        
        intent = fallback_intent
        entities: dict[str, str] = {}
        parameters: dict[str, Any] = {}
        agents: list[str] = []
        confidence = 0.5
        clarification = None
        
        for line in response.split("\n"):
            line = line.strip()
            
            if line.startswith("INTENT:"):
                intent_str = line.split(":", 1)[1].strip().lower()
                for ti in TaskIntent:
                    if ti.value in intent_str or intent_str in ti.value:
                        intent = ti
                        break
            
            elif line.startswith("ENTITIES:"):
                parts = line.split(":", 1)[1].strip()
                for part in parts.split(","):
                    if "=" in part:
                        k, v = part.split("=", 1)
                        entities[k.strip()] = v.strip()
            
            elif line.startswith("PARAMETERS:"):
                parts = line.split(":", 1)[1].strip()
                for part in parts.split(","):
                    if "=" in part:
                        k, v = part.split("=", 1)
                        parameters[k.strip()] = v.strip()
            
            elif line.startswith("AGENTS:"):
                agents_str = line.split(":", 1)[1].strip()
                agents = [a.strip() for a in agents_str.split(",") if a.strip()]
            
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.split(":", 1)[1].strip())
                except ValueError:
                    pass
            
            elif line.startswith("CLARIFICATION:"):
                clarification = line.split(":", 1)[1].strip()
                if not clarification or clarification.lower() in ["none", "leer", "-"]:
                    clarification = None
        
        # Suggest agents if not specified
        if not agents:
            agents = self._suggest_agents(intent)
        
        return ParsedTask(
            intent=intent,
            description=original_input,
            entities=entities,
            parameters=parameters,
            confidence=confidence,
            suggested_agents=agents,
            clarification_needed=clarification,
        )
    
    def _suggest_agents(self, intent: TaskIntent) -> list[str]:
        """Suggest agents based on intent."""
        
        suggestions = {
            TaskIntent.CREATE_PROJECT: ["research", "backend", "frontend"],
            TaskIntent.GENERATE_UI: ["frontend", "security"],
            TaskIntent.GENERATE_API: ["backend", "security"],
            TaskIntent.MODIFY_CODE: ["backend", "frontend", "security"],
            TaskIntent.FIX_BUG: ["research", "backend", "frontend"],
            TaskIntent.ADD_FEATURE: ["research", "backend", "frontend", "security"],
            TaskIntent.SECURITY_REVIEW: ["security"],
            TaskIntent.EXPLAIN: ["research"],
            TaskIntent.RESEARCH: ["research"],
            TaskIntent.UNKNOWN: ["research"],
        }
        
        return suggestions.get(intent, ["research"])
    
    def set_context(
        self,
        project: str | None = None,
        file: str | None = None,
    ) -> None:
        """Set conversation context.
        
        Args:
            project: Current project name
            file: Current file being edited
        """
        if project:
            self.conversation.current_project = project
        if file:
            self.conversation.current_file = file
    
    def clear_context(self) -> None:
        """Clear conversation context."""
        self.conversation = Conversation()

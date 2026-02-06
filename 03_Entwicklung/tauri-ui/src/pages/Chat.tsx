import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Send,
  Bot,
  User,
  Loader2,
  FileCode,
  Sparkles,
  Copy,
  Check,
  AlertCircle,
} from "lucide-react";
import { useAgents } from "../api/hooks";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  agent?: string;
  timestamp: Date;
  code?: string;
  error?: boolean;
}

export function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Willkommen bei Noode! Ich bin dein AI-Entwicklungsteam. Beschreibe mir dein Projekt und ich werde es für dich umsetzen.",
      agent: "orchestrator",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { data: agents } = useAgents();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      // Build conversation history
      const conversationHistory = messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
      }));

      // Add current user message
      conversationHistory.push({
        role: "user",
        content: input,
      });

      // System prompt
      const messagesWithSystem = [
        {
          role: "system",
          content: "Du bist Noode, ein AI-Entwicklungsteam. Du hilfst beim Erstellen von Software-Projekten. Wenn du Code generierst, füge ihn in Code-Blöcken hinzu. Sei konkret und praktisch.",
        },
        ...conversationHistory,
      ];

      // Call backend API
      const response = await fetch("http://localhost:8000/api/v1/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          messages: messagesWithSystem,
        }),
      });

      if (!response.ok) {
        throw new Error("API request failed");
      }

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      // Extract code blocks from response
      let content = data.content;
      let code: string | undefined;

      const codeBlockMatch = content.match(/```(?:\w+)?\n?([\s\S]*?)```/);
      if (codeBlockMatch) {
        code = codeBlockMatch[1].trim();
        // Remove code block from content for cleaner display
        content = content.replace(/```(?:\w+)?\n?[\s\S]*?```/, "[Code wurde generiert]");
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: content,
        agent: data.provider || "assistant",
        timestamp: new Date(),
        code: code,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Chat error:", error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Entschuldigung, es gab einen Fehler bei der Verarbeitung deiner Anfrage. Bitte überprüfe:\n\n1. Ist das Backend gestartet? (python -m uvicorn noode.api.server:app)\n2. Ist ein API-Key konfiguriert? (Einstellungen → API Keys)",
        agent: "system",
        timestamp: new Date(),
        error: true,
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const copyCode = (code: string, id: string) => {
    navigator.clipboard.writeText(code);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const getAgentName = (agentId?: string) => {
    if (!agentId) return "Noode Team";
    const names: Record<string, string> = {
      openai: "OpenAI (GPT-4)",
      anthropic: "Anthropic (Claude)",
      google: "Google (Gemini)",
      openrouter: "OpenRouter",
      orchestrator: "Orchestrator",
      requirements_agent: "Requirements Agent",
      research_agent: "Research Agent",
      frontend_agent: "Frontend Agent",
      backend_agent: "Backend Agent",
      database_agent: "Database Agent",
      security_agent: "Security Agent",
      testing_agent: "Testing Agent",
      system: "System",
    };
    return names[agentId] || agentId;
  };

  const getAgentColor = (agentId?: string) => {
    const colors: Record<string, string> = {
      openai: "bg-green-500",
      anthropic: "bg-orange-500",
      google: "bg-blue-500",
      openrouter: "bg-purple-500",
      orchestrator: "bg-purple-500",
      requirements_agent: "bg-blue-500",
      research_agent: "bg-green-500",
      frontend_agent: "bg-pink-500",
      backend_agent: "bg-orange-500",
      database_agent: "bg-cyan-500",
      security_agent: "bg-red-500",
      testing_agent: "bg-yellow-500",
      system: "bg-gray-500",
    };
    return colors[agentId || ""] || "bg-primary";
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="flex flex-col h-full"
    >
      {/* Header */}
      <div className="border-b border-border p-4 bg-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-text-primary flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-primary" />
              AI Development Chat
            </h2>
            <p className="text-sm text-text-muted">
              Beschreibe dein Projekt und lass die Agenten arbeiten
            </p>
          </div>
          
          {/* Active Agents */}
          {agents && (
            <div className="flex gap-2">
              {agents.slice(0, 4).map((agent) => (
                <div
                  key={agent.name}
                  className={`w-8 h-8 rounded-full ${getAgentColor(agent.name)} flex items-center justify-center text-white text-xs font-bold`}
                  title={getAgentName(agent.name)}
                >
                  {agent.name.charAt(0).toUpperCase()}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className={`flex gap-3 ${
                message.role === "user" ? "flex-row-reverse" : ""
              }`}
            >
              {/* Avatar */}
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                  message.role === "user"
                    ? "bg-primary text-white"
                    : message.error
                    ? "bg-red-500 text-white"
                    : getAgentColor(message.agent)
                }`}
              >
                {message.role === "user" ? (
                  <User className="w-5 h-5" />
                ) : message.error ? (
                  <AlertCircle className="w-5 h-5" />
                ) : (
                  <Bot className="w-5 h-5 text-white" />
                )}
              </div>

              {/* Message Content */}
              <div
                className={`max-w-[80%] ${
                  message.role === "user" ? "items-end" : "items-start"
                }`}
              >
                {/* Agent Name */}
                {message.role === "assistant" && (
                  <span className={`text-xs mb-1 block ${
                    message.error ? "text-red-500" : "text-text-muted"
                  }`}>
                    {getAgentName(message.agent)}
                  </span>
                )}

                {/* Message Bubble */}
                <div
                  className={`rounded-2xl p-4 ${
                    message.role === "user"
                      ? "bg-primary text-white rounded-br-md"
                      : message.error
                      ? "bg-red-50 border border-red-200 text-red-800 rounded-bl-md"
                      : "bg-white border border-border rounded-bl-md"
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>

                  {/* Code Block */}
                  {message.code && (
                    <div className="mt-3 bg-gray-900 rounded-lg overflow-hidden">
                      <div className="flex items-center justify-between px-3 py-2 bg-gray-800 border-b border-gray-700">
                        <div className="flex items-center gap-2 text-gray-400 text-xs">
                          <FileCode className="w-4 h-4" />
                          <span>Generierter Code</span>
                        </div>
                        <button
                          onClick={() => copyCode(message.code!, message.id)}
                          className="text-gray-400 hover:text-white transition-colors"
                        >
                          {copiedId === message.id ? (
                            <Check className="w-4 h-4 text-green-400" />
                          ) : (
                            <Copy className="w-4 h-4" />
                          )}
                        </button>
                      </div>
                      <pre className="p-3 text-xs text-green-400 font-mono overflow-x-auto">
                        <code>{message.code}</code>
                      </pre>
                    </div>
                  )}
                </div>

                {/* Timestamp */}
                <span className="text-xs text-text-muted mt-1 block">
                  {message.timestamp.toLocaleTimeString("de-DE", {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Loading Indicator */}
        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex gap-3"
          >
            <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
              <Loader2 className="w-5 h-5 text-primary animate-spin" />
            </div>
            <div className="bg-white border border-border rounded-2xl rounded-bl-md p-4">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-border p-4 bg-white">
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Beschreibe dein Projekt... (z.B. 'Ich brauche eine React App mit Login')"
              className="w-full px-4 py-3 pr-12 bg-background-sidebar border-2 border-border rounded-xl text-text-primary placeholder:text-text-muted focus:border-primary focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all resize-none"
              rows={3}
              disabled={isLoading}
            />
            <div className="absolute right-3 bottom-3 text-xs text-text-muted">
              {input.length} / 1000
            </div>
          </div>
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="btn-primary self-end flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                <Send className="w-5 h-5" />
                <span>Senden</span>
              </>
            )}
          </button>
        </div>
        <p className="text-xs text-text-muted mt-2">
          Drücke Enter zum Senden, Shift+Enter für neue Zeile
        </p>
      </div>
    </motion.div>
  );
}

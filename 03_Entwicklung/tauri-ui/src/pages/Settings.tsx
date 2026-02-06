import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Key,
  Check,
  X,
  AlertCircle,
  Eye,
  EyeOff,
  TestTube,
  Loader2,
  ChevronDown,
  Bot,
} from "lucide-react";

interface Model {
  id: string;
  name: string;
  description: string;
  context: number;
}

interface Provider {
  name: string;
  available: boolean;
  configured: boolean;
}

interface ProviderConfig {
  provider: string;
  model: string;
  temperature: number;
  max_tokens: number;
}

export function Settings() {
  const [providers, setProviders] = useState<Provider[]>([]);
  const [models, setModels] = useState<Record<string, Model[]>>({});
  const [configs, setConfigs] = useState<Record<string, ProviderConfig>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState<string | null>(null);
  const [testing, setTesting] = useState<string | null>(null);
  const [apiKeys, setApiKeys] = useState<Record<string, string>>({});
  const [showKeys, setShowKeys] = useState<Record<string, boolean>>({});
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const [expandedProvider, setExpandedProvider] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      // Fetch providers
      const providersRes = await fetch("http://localhost:8000/api/v1/chat/providers");
      const providersData = await providersRes.json();
      setProviders(providersData);

      // Fetch models for each provider
      const modelsData: Record<string, Model[]> = {};
      for (const provider of providersData) {
        try {
          const res = await fetch(`http://localhost:8000/api/v1/chat/providers/${provider.name}/models`);
          if (res.ok) {
            modelsData[provider.name] = await res.json();
          }
        } catch (e) {
          console.error(`Failed to fetch models for ${provider.name}`);
        }
      }
      setModels(modelsData);

      // Initialize configs
      const initialConfigs: Record<string, ProviderConfig> = {};
      for (const provider of providersData) {
        initialConfigs[provider.name] = {
          provider: provider.name,
          model: modelsData[provider.name]?.[0]?.id || "",
          temperature: 0.7,
          max_tokens: 4000,
        };
      }
      setConfigs(initialConfigs);
    } catch (error) {
      console.error("Failed to fetch data:", error);
      setMessage({ type: "error", text: "Fehler beim Laden der Daten" });
    } finally {
      setLoading(false);
    }
  };

  const saveApiKey = async (provider: string) => {
    const key = apiKeys[provider];
    if (!key) return;

    setSaving(provider);
    setMessage(null);

    try {
      const response = await fetch(`http://localhost:8000/api/v1/chat/providers/${provider}/key`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ api_key: key }),
      });

      if (response.ok) {
        setMessage({ type: "success", text: `${getProviderLabel(provider)} API Key gespeichert` });
        setApiKeys((prev) => ({ ...prev, [provider]: "" }));
        fetchData(); // Refresh status
      } else {
        setMessage({ type: "error", text: "Fehler beim Speichern" });
      }
    } catch (error) {
      setMessage({ type: "error", text: "Netzwerkfehler" });
    } finally {
      setSaving(null);
    }
  };

  const testProvider = async (provider: string) => {
    setTesting(provider);
    setMessage(null);

    try {
      const response = await fetch(`http://localhost:8000/api/v1/chat/providers/${provider}/test`, {
        method: "POST",
      });

      const data = await response.json();

      if (data.success) {
        setMessage({ type: "success", text: `${getProviderLabel(provider)} funktioniert!` });
      } else {
        setMessage({ type: "error", text: `${getProviderLabel(provider)} Test fehlgeschlagen` });
      }
    } catch (error) {
      setMessage({ type: "error", text: "Test fehlgeschlagen" });
    } finally {
      setTesting(null);
    }
  };

  const toggleShowKey = (provider: string) => {
    setShowKeys((prev) => ({ ...prev, [provider]: !prev[provider] }));
  };

  const toggleExpand = (provider: string) => {
    setExpandedProvider(expandedProvider === provider ? null : provider);
  };

  const updateConfig = (provider: string, field: keyof ProviderConfig, value: any) => {
    setConfigs((prev) => ({
      ...prev,
      [provider]: { ...prev[provider], [field]: value },
    }));
  };

  const getProviderLabel = (name: string) => {
    const labels: Record<string, string> = {
      openai: "OpenAI",
      anthropic: "Anthropic (Claude)",
      google: "Google (Gemini)",
      openrouter: "OpenRouter",
    };
    return labels[name] || name;
  };

  const getProviderIcon = (name: string) => {
    const icons: Record<string, string> = {
      openai: "🤖",
      anthropic: "🧠",
      google: "🔍",
      openrouter: "🌐",
    };
    return icons[name] || "🔑";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="p-8 max-w-5xl"
    >
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-text-primary mb-2 flex items-center gap-3">
          <Key className="w-8 h-8 text-primary" />
          LLM Provider Einstellungen
        </h2>
        <p className="text-text-secondary">
          Konfiguriere deine API Keys und wähle die besten Modelle für Coding
        </p>
      </div>

      {/* Status Message */}
      {message && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className={`mb-6 p-4 rounded-xl flex items-center gap-3 ${
            message.type === "success"
              ? "bg-green-50 border border-green-200 text-green-700"
              : "bg-red-50 border border-red-200 text-red-700"
          }`}
        >
          {message.type === "success" ? <Check className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
          {message.text}
        </motion.div>
      )}

      {/* Providers Grid */}
      <div className="grid grid-cols-1 gap-6">
        {providers.map((provider) => (
          <motion.div
            key={provider.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card overflow-hidden"
          >
            {/* Provider Header */}
            <div
              className="flex items-center justify-between p-6 cursor-pointer hover:bg-background-sidebar/50 transition-colors"
              onClick={() => toggleExpand(provider.name)}
            >
              <div className="flex items-center gap-4">
                <div className="text-3xl">{getProviderIcon(provider.name)}</div>
                <div>
                  <h3 className="font-semibold text-text-primary text-lg">
                    {getProviderLabel(provider.name)}
                  </h3>
                  <div className="flex items-center gap-2 mt-1">
                    {provider.configured ? (
                      <span className="badge badge-success flex items-center gap-1">
                        <Check className="w-3 h-3" /> Konfiguriert
                      </span>
                    ) : (
                      <span className="badge badge-warning flex items-center gap-1">
                        <X className="w-3 h-3" /> Nicht konfiguriert
                      </span>
                    )}
                    {provider.available && <span className="badge badge-info">Aktiv</span>}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3">
                {provider.configured && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      testProvider(provider.name);
                    }}
                    disabled={testing === provider.name}
                    className="btn-secondary text-sm flex items-center gap-2"
                  >
                    {testing === provider.name ? <Loader2 className="w-4 h-4 animate-spin" /> : <TestTube className="w-4 h-4" />}
                    Testen
                  </button>
                )}
                <ChevronDown
                  className={`w-5 h-5 text-text-muted transition-transform ${
                    expandedProvider === provider.name ? "rotate-180" : ""
                  }`}
                />
              </div>
            </div>

            {/* Expanded Content */}
            {expandedProvider === provider.name && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="border-t border-border p-6 space-y-6"
              >
                {/* API Key Section */}
                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">
                    API Key
                  </label>
                  <div className="flex gap-3">
                    <div className="flex-1 relative">
                      <input
                        type={showKeys[provider.name] ? "text" : "password"}
                        value={apiKeys[provider.name] || ""}
                        onChange={(e) =>
                          setApiKeys((prev) => ({ ...prev, [provider.name]: e.target.value }))
                        }
                        placeholder={`${getProviderLabel(provider.name)} API Key...`}
                        className="input-field pr-10"
                      />
                      <button
                        onClick={() => toggleShowKey(provider.name)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-primary"
                      >
                        {showKeys[provider.name] ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                      </button>
                    </div>
                    <button
                      onClick={() => saveApiKey(provider.name)}
                      disabled={!apiKeys[provider.name] || saving === provider.name}
                      className="btn-primary flex items-center gap-2 disabled:opacity-50"
                    >
                      {saving === provider.name ? <Loader2 className="w-4 h-4 animate-spin" /> : <Key className="w-4 h-4" />}
                      Speichern
                    </button>
                  </div>
                </div>

                {/* Model Selection */}
                {models[provider.name] && models[provider.name].length > 0 && (
                  <div>
                    <label className="block text-sm font-medium text-text-primary mb-2 flex items-center gap-2">
                      <Bot className="w-4 h-4" />
                      Modell auswählen
                    </label>
                    <select
                      value={configs[provider.name]?.model || ""}
                      onChange={(e) => updateConfig(provider.name, "model", e.target.value)}
                      className="input-field"
                    >
                      {models[provider.name].map((model) => (
                        <option key={model.id} value={model.id}>
                          {model.name} - {model.description} ({model.context.toLocaleString()} Tokens)
                        </option>
                      ))}
                    </select>
                    <p className="text-xs text-text-muted mt-1">
                      Wähle das beste Modell für deine Coding-Aufgaben
                    </p>
                  </div>
                )}

                {/* Advanced Settings */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-text-primary mb-2">
                      Temperatur: {configs[provider.name]?.temperature || 0.7}
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.1"
                      value={configs[provider.name]?.temperature || 0.7}
                      onChange={(e) => updateConfig(provider.name, "temperature", parseFloat(e.target.value))}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-text-muted mt-1">
                      <span>Präzise (0.0)</span>
                      <span>Kreativ (1.0)</span>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-text-primary mb-2">
                      Max Tokens
                    </label>
                    <input
                      type="number"
                      value={configs[provider.name]?.max_tokens || 4000}
                      onChange={(e) => updateConfig(provider.name, "max_tokens", parseInt(e.target.value))}
                      min="100"
                      max="8000"
                      step="100"
                      className="input-field"
                    />
                  </div>
                </div>
              </motion.div>
            )}
          </motion.div>
        ))}
      </div>

      {/* Tips */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl">
          <h4 className="font-semibold text-blue-900 mb-2">💡 Empfohlene Modelle für Coding</h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• <strong>OpenAI:</strong> GPT-4 Turbo (beste Code-Qualität)</li>
            <li>• <strong>Anthropic:</strong> Claude 3 Opus (lange Kontexte)</li>
            <li>• <strong>OpenRouter:</strong> Kimi K2.5 (exzellent für Coding)</li>
            <li>• <strong>Google:</strong> Gemini 1.5 Pro (1M Kontext)</li>
          </ul>
        </div>

        <div className="p-4 bg-green-50 border border-green-200 rounded-xl">
          <h4 className="font-semibold text-green-900 mb-2">🔒 Sicherheit</h4>
          <ul className="text-sm text-green-800 space-y-1">
            <li>• API Keys werden lokal verschlüsselt</li>
            <li>• Keine Übertragung an Dritte</li>
            <li>• Keys niemals in Logs</li>
            <li>• File-Berechtigungen: 0600</li>
          </ul>
        </div>
      </div>
    </motion.div>
  );
}

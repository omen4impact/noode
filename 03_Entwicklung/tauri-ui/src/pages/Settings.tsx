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
} from "lucide-react";

interface Provider {
  name: string;
  label: string;
  description: string;
  available: boolean;
  configured: boolean;
}

export function Settings() {
  const [providers, setProviders] = useState<Provider[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState<string | null>(null);
  const [testing, setTesting] = useState<string | null>(null);
  const [apiKeys, setApiKeys] = useState<Record<string, string>>({});
  const [showKeys, setShowKeys] = useState<Record<string, boolean>>({});
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  useEffect(() => {
    fetchProviders();
  }, []);

  const fetchProviders = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/chat/providers");
      const data = await response.json();
      setProviders(data);
    } catch (error) {
      console.error("Failed to fetch providers:", error);
      setMessage({ type: "error", text: "Fehler beim Laden der Provider" });
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
        setMessage({ type: "success", text: `${provider} API Key gespeichert` });
        setApiKeys((prev) => ({ ...prev, [provider]: "" }));
        fetchProviders(); // Refresh status
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
        setMessage({ type: "success", text: `${provider} funktioniert!` });
      } else {
        setMessage({ type: "error", text: `${provider} Test fehlgeschlagen` });
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

  const getProviderIcon = (name: string) => {
    const icons: Record<string, string> = {
      openai: "🤖",
      anthropic: "🧠",
      google: "🔍",
      openrouter: "🌐",
    };
    return icons[name] || "🔑";
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
      className="p-8 max-w-4xl"
    >
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-text-primary mb-2 flex items-center gap-3">
          <Key className="w-8 h-8 text-primary" />
          API Einstellungen
        </h2>
        <p className="text-text-secondary">
          Konfiguriere deine LLM Provider API-Keys
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
          {message.type === "success" ? (
            <Check className="w-5 h-5" />
          ) : (
            <AlertCircle className="w-5 h-5" />
          )}
          {message.text}
        </motion.div>
      )}

      {/* Providers */}
      <div className="space-y-6">
        {providers.map((provider) => (
          <motion.div
            key={provider.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="text-2xl">{getProviderIcon(provider.name)}</div>
                <div>
                  <h3 className="font-semibold text-text-primary">
                    {getProviderLabel(provider.name)}
                  </h3>
                  <div className="flex items-center gap-2 mt-1">
                    {provider.configured ? (
                      <span className="badge badge-success flex items-center gap-1">
                        <Check className="w-3 h-3" />
                        Konfiguriert
                      </span>
                    ) : (
                      <span className="badge badge-warning flex items-center gap-1">
                        <X className="w-3 h-3" />
                        Nicht konfiguriert
                      </span>
                    )}
                    {provider.available && (
                      <span className="badge badge-info">Verfügbar</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Test Button */}
              {provider.configured && (
                <button
                  onClick={() => testProvider(provider.name)}
                  disabled={testing === provider.name}
                  className="btn-secondary text-sm flex items-center gap-2"
                >
                  {testing === provider.name ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <TestTube className="w-4 h-4" />
                  )}
                  Testen
                </button>
              )}
            </div>

            {/* API Key Input */}
            <div className="flex gap-3">
              <div className="flex-1 relative">
                <input
                  type={showKeys[provider.name] ? "text" : "password"}
                  value={apiKeys[provider.name] || ""}
                  onChange={(e) =>
                    setApiKeys((prev) => ({
                      ...prev,
                      [provider.name]: e.target.value,
                    }))
                  }
                  placeholder={`${getProviderLabel(provider.name)} API Key eingeben...`}
                  className="input-field pr-10"
                />
                <button
                  onClick={() => toggleShowKey(provider.name)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-primary"
                >
                  {showKeys[provider.name] ? (
                    <EyeOff className="w-5 h-5" />
                  ) : (
                    <Eye className="w-5 h-5" />
                  )}
                </button>
              </div>
              <button
                onClick={() => saveApiKey(provider.name)}
                disabled={!apiKeys[provider.name] || saving === provider.name}
                className="btn-primary flex items-center gap-2 disabled:opacity-50"
              >
                {saving === provider.name ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    <Key className="w-4 h-4" />
                    Speichern
                  </>
                )}
              </button>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Info Box */}
      <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-xl">
        <h4 className="font-semibold text-blue-900 mb-2">💡 Hinweis</h4>
        <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
          <li>API Keys werden lokal verschlüsselt gespeichert</li>
          <li>Keys werden niemals an Dritte weitergegeben</li>
          <li>Du benötigst mindestens einen konfigurierten Provider</li>
          <li>OpenRouter unterstützt alle Modelle (OpenAI, Anthropic, etc.)</li>
        </ul>
      </div>
    </motion.div>
  );
}

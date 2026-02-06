import { useState } from "react";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  FolderKanban,
  Code,
  FileCode,
  Settings,
  Play,
  Terminal,
  Save,
  Plus,
  Trash2,
  Loader2,
} from "lucide-react";
import { useProject } from "../api/hooks";
import type { Project } from "../types";

interface ProjectDetailProps {
  projectId: string;
  onBack: () => void;
}

export function ProjectDetail({ projectId, onBack }: ProjectDetailProps) {
  const { data: project, isLoading } = useProject(projectId);
  const [activeTab, setActiveTab] = useState<"overview" | "files" | "settings">("overview");
  const [code, setCode] = useState(`// Willkommen bei Noode!
// Hier kannst du Code für dein Projekt schreiben.

function main() {
  console.log("Hello from Noode!");
}

main();
`);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!project) {
    return (
      <div className="flex flex-col items-center justify-center h-full">
        <p className="text-text-muted">Projekt nicht gefunden</p>
        <button onClick={onBack} className="btn-primary mt-4">
          Zurück
        </button>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="p-8 h-full flex flex-col"
    >
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <button
          onClick={onBack}
          className="p-2 hover:bg-background-sidebar rounded-lg transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-text-secondary" />
        </button>
        <div>
          <h2 className="text-2xl font-bold text-text-primary flex items-center gap-3">
            <FolderKanban className="w-6 h-6 text-primary" />
            {project.name}
          </h2>
          <p className="text-text-muted text-sm">
            {project.description || "Keine Beschreibung"}
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-border pb-4">
        {[
          { id: "overview", label: "Übersicht", icon: FolderKanban },
          { id: "files", label: "Dateien", icon: FileCode },
          { id: "settings", label: "Einstellungen", icon: Settings },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
              activeTab === tab.id
                ? "bg-primary text-white"
                : "text-text-secondary hover:bg-background-sidebar"
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto">
        {activeTab === "overview" && (
          <div className="space-y-6">
            {/* Project Info */}
            <div className="card">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Projektinformationen
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm text-text-muted">Projekt ID</label>
                  <p className="text-text-primary font-mono">{project.project_id}</p>
                </div>
                <div>
                  <label className="text-sm text-text-muted">Template</label>
                  <p className="text-text-primary capitalize">{project.template}</p>
                </div>
                <div>
                  <label className="text-sm text-text-muted">Erstellt am</label>
                  <p className="text-text-primary">
                    {new Date(project.created_at).toLocaleDateString('de-DE')}
                  </p>
                </div>
                <div>
                  <label className="text-sm text-text-muted">Status</label>
                  <span className="badge badge-info">{project.status}</span>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="card">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Schnellaktionen
              </h3>
              <div className="flex gap-3">
                <button className="btn-primary flex items-center gap-2">
                  <Code className="w-4 h-4" />
                  Code generieren
                </button>
                <button className="btn-secondary flex items-center gap-2">
                  <Terminal className="w-4 h-4" />
                  Terminal öffnen
                </button>
                <button className="btn-secondary flex items-center gap-2">
                  <Play className="w-4 h-4" />
                  Projekt starten
                </button>
              </div>
            </div>

            {/* Code Editor */}
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-text-primary">
                  main.js
                </h3>
                <button className="btn-secondary text-sm flex items-center gap-2">
                  <Save className="w-4 h-4" />
                  Speichern
                </button>
              </div>
              <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                className="w-full h-64 p-4 bg-gray-900 text-green-400 font-mono text-sm rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary"
                spellCheck={false}
              />
            </div>
          </div>
        )}

        {activeTab === "files" && (
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-text-primary">Projektdateien</h3>
              <button className="btn-primary text-sm flex items-center gap-2">
                <Plus className="w-4 h-4" />
                Neue Datei
              </button>
            </div>
            <div className="space-y-2">
              {[
                { name: "main.js", type: "code" },
                { name: "README.md", type: "markdown" },
                { name: "package.json", type: "json" },
                { name: ".gitignore", type: "text" },
              ].map((file) => (
                <div
                  key={file.name}
                  className="flex items-center justify-between p-3 bg-background-sidebar rounded-lg hover:bg-background-main transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <FileCode className="w-5 h-5 text-primary" />
                    <span className="text-text-primary font-mono text-sm">
                      {file.name}
                    </span>
                  </div>
                  <button className="text-red-500 hover:text-red-700 p-1">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === "settings" && (
          <div className="card max-w-2xl">
            <h3 className="text-lg font-semibold text-text-primary mb-6">
              Projekteinstellungen
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Projektname
                </label>
                <input
                  type="text"
                  defaultValue={project.name}
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Beschreibung
                </label>
                <textarea
                  defaultValue={project.description || ""}
                  rows={3}
                  className="input-field resize-none"
                />
              </div>
              <div className="flex gap-3 pt-4">
                <button className="btn-primary">Speichern</button>
                <button className="btn-secondary text-red-600 border-red-200 hover:bg-red-50">
                  Projekt löschen
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}

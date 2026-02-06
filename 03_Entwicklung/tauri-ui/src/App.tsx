import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard,
  FolderKanban,
  PlusCircle,
  Settings,
  Search,
  Rocket,
  Smartphone,
  Plug,
  Bot,
  BarChart3,
  Gamepad2,
  Loader2,
  AlertCircle,
  CheckCircle,
  BookOpen,
} from "lucide-react";
import { useProjects, useCreateProject, useAgents } from "./api/hooks";
import { Knowledge } from "./pages/Knowledge";
import { ProjectDetail } from "./pages/ProjectDetail";

// Navigation Items
const navItems = [
  { icon: LayoutDashboard, label: "Dashboard", id: "dashboard" },
  { icon: PlusCircle, label: "Neues Projekt", id: "new-project" },
  { icon: FolderKanban, label: "Projekte", id: "projects" },
];

const toolItems = [
  { icon: Search, label: "Research", id: "research" },
  { icon: Smartphone, label: "Design", id: "design" },
  { icon: Rocket, label: "Code Review", id: "review" },
  { icon: Settings, label: "Security", id: "security" },
  { icon: BookOpen, label: "Knowledge", id: "knowledge" },
];

// Quick Actions
const quickActions = [
  { icon: Rocket, title: "Web App", desc: "Webanwendung erstellen", color: "from-blue-500 to-indigo-600", template: "web-app" },
  { icon: Smartphone, title: "Mobile", desc: "Mobile Anwendung", color: "from-purple-500 to-pink-600", template: "mobile" },
  { icon: Plug, title: "API", desc: "REST API erstellen", color: "from-green-500 to-teal-600", template: "api" },
  { icon: Bot, title: "Chatbot", desc: "KI-Assistent bauen", color: "from-orange-500 to-red-600", template: "chatbot" },
  { icon: BarChart3, title: "Dashboard", desc: "Daten-Dashboard", color: "from-cyan-500 to-blue-600", template: "dashboard" },
  { icon: Gamepad2, title: "Spiel", desc: "Browsergame erstellen", color: "from-pink-500 to-rose-600", template: "game" },
];

function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [selectedProject, setSelectedProject] = useState<string | null>(null);

  return (
    <div className="flex h-screen bg-background-main">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-border flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b border-border">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-primary to-primary-dark bg-clip-text text-transparent">
            Noode
          </h1>
          <p className="text-xs text-text-muted mt-1">AI Development Platform</p>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1">
          <div className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3 px-4">
            Hauptmenü
          </div>
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`sidebar-item w-full ${activeTab === item.id ? "active" : ""}`}
            >
              <item.icon className="w-5 h-5" />
              <span>{item.label}</span>
            </button>
          ))}

          <div className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3 mt-8 px-4">
            Werkzeuge
          </div>
          {toolItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`sidebar-item w-full ${activeTab === item.id ? "active" : ""}`}
            >
              <item.icon className="w-5 h-5" />
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-border">
          <button className="sidebar-item w-full">
            <Settings className="w-5 h-5" />
            <span>Einstellungen</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <AnimatePresence mode="wait">
          {selectedProject ? (
            <ProjectDetail
              key="project-detail"
              projectId={selectedProject}
              onBack={() => setSelectedProject(null)}
            />
          ) : (
            <>
              {activeTab === "dashboard" && <Dashboard key="dashboard" onNavigate={setActiveTab} />}
              {activeTab === "new-project" && <NewProject key="new-project" />}
              {activeTab === "projects" && <Projects key="projects" onSelectProject={setSelectedProject} />}
              {activeTab === "knowledge" && <Knowledge key="knowledge" />}
            </>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

// Dashboard Component
function Dashboard({ onNavigate }: { onNavigate: (tab: string) => void }) {
  const { data: projects, isLoading, error } = useProjects();
  const { data: agents } = useAgents();

  const createProject = useCreateProject();

  const handleQuickAction = async (template: string, title: string) => {
    try {
      await createProject.mutateAsync({
        name: `${title} Project`,
        template,
      });
      onNavigate("projects");
    } catch (err) {
      console.error("Failed to create project:", err);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="p-8"
    >
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-header rounded-2xl p-8 mb-8"
      >
        <h2 className="text-3xl font-bold text-white mb-2">
          Willkommen bei Noode
        </h2>
        <p className="text-white/80">
          Was möchtest du heute entwickeln?
        </p>
      </motion.div>

      {/* Agent Status */}
      {agents && (
        <div className="mb-8">
          <h3 className="text-lg font-bold text-text-primary mb-4">Agent Status</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {agents.map((agent, index) => (
              <motion.div
                key={agent.name}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className="card flex items-center gap-3"
              >
                <div className={`w-3 h-3 rounded-full ${
                  agent.status === 'idle' ? 'bg-green-500' : 
                  agent.status === 'busy' ? 'bg-yellow-500' : 'bg-red-500'
                }`} />
                <div>
                  <div className="font-semibold text-text-primary">{agent.name}</div>
                  <div className="text-xs text-text-muted capitalize">{agent.status}</div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="mb-8">
        <h3 className="text-lg font-bold text-text-primary mb-4">Schnellstart</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {quickActions.map((action, index) => (
            <motion.button
              key={action.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
              onClick={() => handleQuickAction(action.template, action.title)}
              disabled={createProject.isPending}
              className="card card-hover text-left group disabled:opacity-50"
            >
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${action.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                {createProject.isPending && createProject.variables?.template === action.template ? (
                  <Loader2 className="w-6 h-6 text-white animate-spin" />
                ) : (
                  <action.icon className="w-6 h-6 text-white" />
                )}
              </div>
              <h4 className="font-bold text-text-primary mb-1">{action.title}</h4>
              <p className="text-sm text-text-muted">{action.desc}</p>
            </motion.button>
          ))}
        </div>
      </div>

      {/* Recent Projects */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-text-primary">Letzte Projekte</h3>
          <button 
            onClick={() => onNavigate("projects")}
            className="text-primary font-medium hover:underline"
          >
            Alle anzeigen
          </button>
        </div>

        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        )}

        {error && (
          <div className="card bg-red-50 border-red-200 flex items-center gap-3 text-red-700">
            <AlertCircle className="w-5 h-5" />
            <div>
              <div className="font-semibold">Fehler beim Laden</div>
              <div className="text-sm">Ist das Backend gestartet?</div>
            </div>
          </div>
        )}

        {projects && projects.length === 0 && (
          <div className="card text-center py-12">
            <FolderKanban className="w-12 h-12 text-text-muted mx-auto mb-4" />
            <h4 className="font-semibold text-text-primary mb-1">Noch keine Projekte</h4>
            <p className="text-text-muted text-sm mb-4">Erstelle dein erstes Projekt!</p>
            <button 
              onClick={() => onNavigate("new-project")}
              className="btn-primary"
            >
              Projekt erstellen
            </button>
          </div>
        )}

        {projects && projects.length > 0 && (
          <div className="space-y-3">
            {projects.slice(0, 3).map((project, i) => (
              <motion.div
                key={project.project_id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + i * 0.1 }}
                className="card flex items-center justify-between"
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-lg bg-background-sidebar flex items-center justify-center">
                    <FolderKanban className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-text-primary">{project.name}</h4>
                    <p className="text-sm text-text-muted">
                      {new Date(project.updated_at).toLocaleDateString('de-DE')}
                    </p>
                  </div>
                </div>
                <span className={`badge ${
                  project.status === 'active' ? "badge-success" : 
                  project.status === 'development' ? "badge-info" : "badge-warning"
                }`}>
                  {project.status}
                </span>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}

// New Project Component
function NewProject() {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [selectedTemplate, setSelectedTemplate] = useState("web-app");

  const createProject = useCreateProject();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    try {
      await createProject.mutateAsync({
        name,
        description,
        template: selectedTemplate,
      });
      // Reset form
      setName("");
      setDescription("");
    } catch (err) {
      console.error("Failed to create project:", err);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="p-8"
    >
      <div className="max-w-2xl">
        <h2 className="text-3xl font-bold text-text-primary mb-2">
          Neues Projekt erstellen
        </h2>
        <p className="text-text-secondary mb-8">
          Beschreibe dein Projekt in eigenen Worten. Unsere AI-Agents kümmern sich um den Rest.
        </p>

        {createProject.isSuccess && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="card bg-green-50 border-green-200 flex items-center gap-3 text-green-700 mb-6"
          >
            <CheckCircle className="w-5 h-5" />
            <div>
              <div className="font-semibold">Projekt erstellt!</div>
              <div className="text-sm">Das Projekt wurde erfolgreich angelegt.</div>
            </div>
          </motion.div>
        )}

        <form onSubmit={handleSubmit} className="card">
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-semibold text-text-primary mb-2">
                Projektname *
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="z.B. Meine Webapp"
                className="input-field"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-text-primary mb-2">
                Beschreibung
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Ich möchte eine Webanwendung die..."
                rows={4}
                className="input-field resize-none"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-text-primary mb-2">
                Vorlage
              </label>
              <div className="grid grid-cols-2 gap-3">
                {quickActions.slice(0, 4).map((action) => (
                  <button
                    key={action.template}
                    type="button"
                    onClick={() => setSelectedTemplate(action.template)}
                    className={`p-4 border-2 rounded-xl text-left transition-colors ${
                      selectedTemplate === action.template 
                        ? "border-primary bg-primary/5" 
                        : "border-border hover:border-primary"
                    }`}
                  >
                    <action.icon className={`w-6 h-6 mb-2 ${
                      selectedTemplate === action.template ? "text-primary" : "text-text-muted"
                    }`} />
                    <div className="font-semibold text-text-primary">{action.title}</div>
                    <div className="text-xs text-text-muted">{action.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            <div className="flex gap-3 pt-4">
              <button 
                type="button" 
                className="btn-secondary flex-1"
                onClick={() => window.history.back()}
              >
                Abbrechen
              </button>
              <button 
                type="submit" 
                className="btn-primary flex-1 flex items-center justify-center gap-2"
                disabled={createProject.isPending || !name.trim()}
              >
                {createProject.isPending && <Loader2 className="w-5 h-5 animate-spin" />}
                Projekt erstellen
              </button>
            </div>
          </div>
        </form>
      </div>
    </motion.div>
  );
}

// Projects Component
function Projects({ onSelectProject }: { onSelectProject: (id: string) => void }) {
  const { data: projects, isLoading, error } = useProjects();
  const [searchTerm, setSearchTerm] = useState("");
  const deleteProject = useDeleteProject();

  const filteredProjects = projects?.filter(project =>
    project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    project.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="p-8"
    >
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-3xl font-bold text-text-primary mb-1">
            Meine Projekte
          </h2>
          <p className="text-text-secondary">
            Alle deine Projekte auf einen Blick
          </p>
        </div>
        <button 
          onClick={() => {}}
          className="btn-primary flex items-center gap-2"
        >
          <PlusCircle className="w-5 h-5" />
          Neues Projekt
        </button>
      </div>

      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-text-muted" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Projekte durchsuchen..."
            className="input-field pl-12"
          />
        </div>
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      )}

      {error && (
        <div className="card bg-red-50 border-red-200 flex items-center gap-3 text-red-700">
          <AlertCircle className="w-5 h-5" />
          <div>
            <div className="font-semibold">Fehler beim Laden</div>
            <div className="text-sm">Ist das Backend gestartet?</div>
          </div>
        </div>
      )}

      {filteredProjects && filteredProjects.length === 0 && (
        <div className="card text-center py-12">
          <FolderKanban className="w-12 h-12 text-text-muted mx-auto mb-4" />
          <h4 className="font-semibold text-text-primary mb-1">
            {searchTerm ? "Keine Projekte gefunden" : "Noch keine Projekte"}
          </h4>
          <p className="text-text-muted text-sm">
            {searchTerm ? "Versuche einen anderen Suchbegriff" : "Erstelle dein erstes Projekt!"}
          </p>
        </div>
      )}

      {filteredProjects && filteredProjects.length > 0 && (
        <div className="space-y-3">
          {filteredProjects.map((project) => (
            <div
              key={project.project_id}
              className="card flex items-center justify-between hover:border-primary transition-colors"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary/20 to-primary/10 flex items-center justify-center">
                  <FolderKanban className="w-6 h-6 text-primary" />
                </div>
                <div>
                  <h4 className="font-semibold text-text-primary">{project.name}</h4>
                  <p className="text-sm text-text-muted">
                    {project.description || "Keine Beschreibung"}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <span className="text-sm text-text-muted">
                  {new Date(project.created_at).toLocaleDateString('de-DE')}
                </span>
                <span className={`badge ${
                  project.status === 'active' ? "badge-success" : 
                  project.status === 'development' ? "badge-info" : "badge-warning"
                }`}>
                  {project.status}
                </span>
                <button 
                  onClick={() => onSelectProject(project.project_id)}
                  className="text-primary font-medium hover:underline"
                >
                  Öffnen
                </button>
                <button 
                  onClick={() => deleteProject.mutate(project.project_id)}
                  className="text-red-500 hover:text-red-700"
                  disabled={deleteProject.isPending}
                >
                  Löschen
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </motion.div>
  );
}

// Import missing hook
import { useDeleteProject } from "./api/hooks";

export default App;

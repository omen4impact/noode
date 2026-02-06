import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  BookOpen,
  Search,
  Plus,
  Trash2,
  FileText,
  Code,
  FileCode,
  Braces,
  Loader2,
  AlertCircle,
  Database,
  CheckCircle,
} from "lucide-react";
import {
  useKnowledgeStats,
  useSearchDocuments,
  useAddDocument,
  useDeleteDocument,
} from "../api/hooks";
import type { Document } from "../types";

export function Knowledge() {
  const [activeTab, setActiveTab] = useState<"search" | "add">("search");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);

  const { data: stats } = useKnowledgeStats();
  const searchMutation = useSearchDocuments();
  const addMutation = useAddDocument();
  const deleteMutation = useDeleteDocument();

  // Add document form state
  const [newDoc, setNewDoc] = useState<Partial<Document>>({
    content: "",
    doc_type: "text",
    metadata: {},
  });

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    try {
      const results = await searchMutation.mutateAsync({
        query: searchQuery,
        top_k: 10,
      });
      setSearchResults(results);
    } catch (err) {
      console.error("Search failed:", err);
    }
  };

  const handleAddDocument = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newDoc.content?.trim()) return;

    try {
      await addMutation.mutateAsync({
        content: newDoc.content,
        doc_type: newDoc.doc_type || "text",
        metadata: newDoc.metadata || {},
      });
      setNewDoc({ content: "", doc_type: "text", metadata: {} });
      setActiveTab("search");
    } catch (err) {
      console.error("Failed to add document:", err);
    }
  };

  const handleDelete = async (docId: string) => {
    try {
      await deleteMutation.mutateAsync(docId);
      setSearchResults((prev) => prev.filter((r) => r.id !== docId));
    } catch (err) {
      console.error("Failed to delete document:", err);
    }
  };

  const getDocTypeIcon = (type: string) => {
    switch (type) {
      case "code":
        return <Code className="w-5 h-5" />;
      case "markdown":
        return <FileText className="w-5 h-5" />;
      case "json":
        return <Braces className="w-5 h-5" />;
      default:
        return <FileCode className="w-5 h-5" />;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="p-8"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-3xl font-bold text-text-primary mb-1 flex items-center gap-3">
            <BookOpen className="w-8 h-8 text-primary" />
            Knowledge Base
          </h2>
          <p className="text-text-secondary">
            Durchsuche und verwalte deine Wissensdatenbank
          </p>
        </div>

        {/* Stats */}
        {stats && (
          <div className="flex items-center gap-4">
            <div className="card flex items-center gap-3 py-3 px-4">
              <Database className="w-5 h-5 text-primary" />
              <div>
                <div className="text-2xl font-bold text-text-primary">
                  {stats.total_documents}
                </div>
                <div className="text-xs text-text-muted">Dokumente</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setActiveTab("search")}
          className={`flex items-center gap-2 px-6 py-3 rounded-xl font-semibold transition-all ${
            activeTab === "search"
              ? "bg-primary text-white shadow-lg shadow-primary/30"
              : "bg-white text-text-secondary hover:bg-background-sidebar"
          }`}
        >
          <Search className="w-5 h-5" />
          Suchen
        </button>
        <button
          onClick={() => setActiveTab("add")}
          className={`flex items-center gap-2 px-6 py-3 rounded-xl font-semibold transition-all ${
            activeTab === "add"
              ? "bg-primary text-white shadow-lg shadow-primary/30"
              : "bg-white text-text-secondary hover:bg-background-sidebar"
          }`}
        >
          <Plus className="w-5 h-5" />
          Dokument hinzufügen
        </button>
      </div>

      {/* Content */}
      <AnimatePresence mode="wait">
        {activeTab === "search" ? (
          <motion.div
            key="search"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Search Form */}
            <form onSubmit={handleSearch} className="flex gap-3">
              <div className="relative flex-1">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-text-muted" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Durchsuche Knowledge Base..."
                  className="w-full pl-12 pr-4 py-4 bg-white border-2 border-border rounded-xl text-text-primary placeholder:text-text-muted focus:border-primary focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all"
                />
              </div>
              <button
                type="submit"
                disabled={searchMutation.isPending || !searchQuery.trim()}
                className="btn-primary flex items-center gap-2 disabled:opacity-50"
              >
                {searchMutation.isPending ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Search className="w-5 h-5" />
                )}
                Suchen
              </button>
            </form>

            {/* Search Results */}
            {searchResults.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-lg font-semibold text-text-primary">
                  Suchergebnisse ({searchResults.length})
                </h3>
                {searchResults.map((result, index) => (
                  <motion.div
                    key={result.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="card"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex items-start gap-3 flex-1">
                        <div className="p-2 bg-primary/10 rounded-lg text-primary">
                          {getDocTypeIcon(result.doc_type)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-medium px-2 py-1 bg-background-sidebar rounded-full text-text-secondary uppercase">
                              {result.doc_type}
                            </span>
                            <span className="text-xs text-text-muted">
                              Score: {(result.score * 100).toFixed(1)}%
                            </span>
                          </div>
                          <p className="text-text-primary text-sm line-clamp-3">
                            {result.content}
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => handleDelete(result.id)}
                        disabled={deleteMutation.isPending}
                        className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                        title="Löschen"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}

            {searchResults.length === 0 && searchQuery && !searchMutation.isPending && (
              <div className="card text-center py-12">
                <Search className="w-12 h-12 text-text-muted mx-auto mb-4" />
                <h4 className="font-semibold text-text-primary mb-1">
                  Keine Ergebnisse
                </h4>
                <p className="text-text-muted">
                  Versuche einen anderen Suchbegriff
                </p>
              </div>
            )}
          </motion.div>
        ) : (
          <motion.div
            key="add"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <form onSubmit={handleAddDocument} className="card max-w-3xl">
              <div className="space-y-6">
                {/* Document Type */}
                <div>
                  <label className="block text-sm font-semibold text-text-primary mb-2">
                    Dokumenttyp
                  </label>
                  <div className="grid grid-cols-4 gap-3">
                    {["text", "code", "markdown", "json"].map((type) => (
                      <button
                        key={type}
                        type="button"
                        onClick={() =>
                          setNewDoc((prev) => ({ ...prev, doc_type: type as any }))
                        }
                        className={`flex items-center gap-2 p-3 border-2 rounded-xl transition-all ${
                          newDoc.doc_type === type
                            ? "border-primary bg-primary/5 text-primary"
                            : "border-border hover:border-primary text-text-secondary"
                        }`}
                      >
                        {getDocTypeIcon(type)}
                        <span className="capitalize font-medium">{type}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Content */}
                <div>
                  <label className="block text-sm font-semibold text-text-primary mb-2">
                    Inhalt *
                  </label>
                  <textarea
                    value={newDoc.content}
                    onChange={(e) =>
                      setNewDoc((prev) => ({ ...prev, content: e.target.value }))
                    }
                    placeholder="Füge hier den Inhalt des Dokuments ein..."
                    rows={10}
                    className="input-field resize-none font-mono text-sm"
                    required
                  />
                </div>

                {/* Success Message */}
                {addMutation.isSuccess && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex items-center gap-3 p-4 bg-green-50 border border-green-200 rounded-xl text-green-700"
                  >
                    <CheckCircle className="w-5 h-5" />
                    <span>Dokument erfolgreich hinzugefügt!</span>
                  </motion.div>
                )}

                {/* Error Message */}
                {addMutation.isError && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700"
                  >
                    <AlertCircle className="w-5 h-5" />
                    <span>Fehler beim Hinzufügen des Dokuments</span>
                  </motion.div>
                )}

                {/* Submit */}
                <div className="flex gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setActiveTab("search")}
                    className="btn-secondary flex-1"
                  >
                    Abbrechen
                  </button>
                  <button
                    type="submit"
                    disabled={addMutation.isPending || !newDoc.content?.trim()}
                    className="btn-primary flex-1 flex items-center justify-center gap-2 disabled:opacity-50"
                  >
                    {addMutation.isPending ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <Plus className="w-5 h-5" />
                    )}
                    Dokument hinzufügen
                  </button>
                </div>
              </div>
            </form>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

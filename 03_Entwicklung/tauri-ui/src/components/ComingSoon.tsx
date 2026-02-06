import { motion } from "framer-motion";
import { Construction, Clock, Rocket } from "lucide-react";

interface ComingSoonProps {
  title: string;
  description?: string;
}

export function ComingSoon({ title, description }: ComingSoonProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="flex flex-col items-center justify-center h-full p-8"
    >
      <motion.div
        initial={{ scale: 0.9 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.1 }}
        className="text-center max-w-md"
      >
        <div className="relative inline-block mb-6">
          <div className="absolute inset-0 bg-primary/20 rounded-full blur-xl" />
          <div className="relative w-24 h-24 bg-gradient-to-br from-primary to-primary-dark rounded-2xl flex items-center justify-center shadow-lg shadow-primary/30">
            <Construction className="w-12 h-12 text-white" />
          </div>
        </div>
        
        <h2 className="text-3xl font-bold text-text-primary mb-3">
          {title}
        </h2>
        
        <p className="text-text-secondary mb-6">
          {description || "Diese Funktion wird in einer zukünftigen Version verfügbar sein."}
        </p>
        
        <div className="flex items-center justify-center gap-2 text-text-muted">
          <Clock className="w-4 h-4" />
          <span className="text-sm">Coming Soon</span>
        </div>
        
        <div className="mt-8 p-4 bg-background-sidebar rounded-xl">
          <div className="flex items-center gap-3 text-text-secondary">
            <Rocket className="w-5 h-5 text-primary" />
            <span className="text-sm">
              Beta v0.5.0 - Wir arbeiten daran!
            </span>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}

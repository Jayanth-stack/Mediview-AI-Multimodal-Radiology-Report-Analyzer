import { motion, AnimatePresence } from "framer-motion";

export default function FindingsDrawer({ isOpen, findings, onHover }) {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ x: "100%" }}
          animate={{ x: 0 }}
          exit={{ x: "100%" }}
          transition={{ type: "spring", damping: 20 }}
          className="absolute right-0 top-0 h-full w-80 bg-white shadow-xl overflow-auto"
        >
          <ul>
            {findings.map((f, i) => (
              <motion.li
                key={i}
                whileHover={{ scale: 1.05, backgroundColor: "#f0f0f0" }}
                onHoverStart={() => onHover(f.id, true)}  // Pulse box on canvas
                onHoverEnd={() => onHover(f.id, false)}
                className="p-4 border-b"
              >
                {f.label} ({f.confidence}%)
              </motion.li>
            ))}
          </ul>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

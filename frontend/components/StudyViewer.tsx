import { motion } from "framer-motion";
import { useState } from "react";
import FindingsDrawer from "./FindingsDrawer";

export default function StudyViewer({ imageSrc, findings }) {
  const [hoveredId, setHoveredId] = useState(null);

  const onHover = (id, isHovering) => {
    setHoveredId(isHovering ? id : null);
  };

  return (
    <div className="relative inline-block w-full h-96">
      <img src={imageSrc} className="max-w-full h-full object-contain" />
      <svg className="absolute inset-0 w-full h-full pointer-events-none">
        {findings.map((f) => (
          <motion.rect
            key={f.id}
            x={f.bbox.x}
            y={f.bbox.y}
            width={f.bbox.width}
            height={f.bbox.height}
            stroke="lime"
            fill="none"
            strokeWidth={2}
            animate={{
              scale: hoveredId === f.id ? [1, 1.1, 1] : 1,
              opacity: hoveredId === f.id ? [0.5, 1, 0.5] : 1,
            }}
            transition={{ duration: 0.5, repeat: Infinity, repeatType: "reverse" }}
          />
        ))}
      </svg>
      <FindingsDrawer isOpen={true} findings={findings} onHover={onHover} />
    </div>
  );
}

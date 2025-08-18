import { motion } from "framer-motion";
import { useState } from "react";
import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch";
import FindingsDrawer from "./FindingsDrawer";

interface Finding {
  id: number;
  label: string;
  confidence: number;
  bbox: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

interface StudyViewerProps {
  imageSrc: string;
  findings: Finding[];
}

export default function StudyViewer({ imageSrc, findings }: StudyViewerProps) {
  const [hoveredId, setHoveredId] = useState<number | null>(null);

  const onHover = (id: number, isHovering: boolean) => {
    setHoveredId(isHovering ? id : null);
  };

  return (
    <div className="flex h-[600px]">
      <TransformWrapper>
        <TransformComponent
          wrapperClass="!w-full !h-full"
          contentClass="relative !w-full !h-full"
        >
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
        </TransformComponent>
      </TransformWrapper>
      <FindingsDrawer isOpen={true} findings={findings} onHover={onHover} />
    </div>
  );
}

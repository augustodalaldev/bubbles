import { motion } from "framer-motion";

interface BubbleConfig {
  id: number;
  size: number;
  left: string;
  duration: number;
  delay: number;
  opacity: number;
}

const BUBBLES: BubbleConfig[] = [
  { id: 1, size: 90, left: "8%", duration: 18, delay: 0, opacity: 0.35 },
  { id: 2, size: 45, left: "18%", duration: 14, delay: 3, opacity: 0.25 },
  { id: 3, size: 140, left: "32%", duration: 24, delay: 5, opacity: 0.2 },
  { id: 4, size: 60, left: "48%", duration: 16, delay: 1, opacity: 0.3 },
  { id: 5, size: 110, left: "64%", duration: 22, delay: 4, opacity: 0.25 },
  { id: 6, size: 50, left: "78%", duration: 15, delay: 2, opacity: 0.35 },
  { id: 7, size: 130, left: "88%", duration: 20, delay: 6, opacity: 0.2 },
  { id: 8, size: 70, left: "94%", duration: 17, delay: 8, opacity: 0.25 },
];

export const AmbientBubbles = () => {
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
      {/* Light Caustics / Sunbeam gradient */}
      <div 
        className="absolute -top-32 left-1/4 w-[700px] h-[500px] rounded-full blur-3xl opacity-40 mix-blend-screen pointer-events-none"
        style={{
          background: "radial-gradient(circle, rgba(78, 226, 242, 0.45) 0%, rgba(184, 242, 248, 0.2) 50%, transparent 80%)"
        }}
      />
      <div 
        className="absolute top-1/3 -right-24 w-[600px] h-[600px] rounded-full blur-3xl opacity-30 mix-blend-screen pointer-events-none"
        style={{
          background: "radial-gradient(circle, rgba(238, 91, 155, 0.35) 0%, rgba(250, 162, 194, 0.15) 50%, transparent 80%)"
        }}
      />
      <div 
        className="absolute -bottom-20 left-10 w-[800px] h-[500px] rounded-full blur-3xl opacity-45 mix-blend-screen pointer-events-none"
        style={{
          background: "radial-gradient(circle, rgba(8, 196, 219, 0.35) 0%, rgba(23, 162, 184, 0.15) 60%, transparent 85%)"
        }}
      />

      {/* Floating Ambient Spheres */}
      {BUBBLES.map((b) => (
        <motion.div
          key={b.id}
          className="absolute rounded-full"
          style={{
            width: b.size,
            height: b.size,
            left: b.left,
            bottom: -150,
            opacity: b.opacity,
            background: "radial-gradient(circle at 35% 30%, rgba(255,255,255,0.85) 0%, rgba(184,242,248,0.5) 35%, rgba(8,196,219,0.3) 70%, rgba(238,91,155,0.2) 90%, rgba(255,255,255,0.6) 100%)",
            border: "1.5px solid rgba(255, 255, 255, 0.6)",
            boxShadow: "inset -4px -6px 12px rgba(4,86,97,0.2), inset 3px 4px 8px rgba(255,255,255,0.8), 0 8px 24px rgba(8,196,219,0.2)",
          }}
          animate={{
            y: ["0vh", "-120vh"],
            x: [0, 25, -20, 15, 0],
            rotate: [0, 90, 180, 270, 360],
          }}
          transition={{
            y: {
              repeat: Infinity,
              duration: b.duration,
              delay: b.delay,
              ease: "linear",
            },
            x: {
              repeat: Infinity,
              duration: b.duration * 0.7,
              delay: b.delay,
              ease: "easeInOut",
            },
            rotate: {
              repeat: Infinity,
              duration: b.duration * 1.2,
              ease: "linear",
            },
          }}
        >
          {/* Internal specular highlight */}
          <div 
            className="absolute rounded-full bg-white/70"
            style={{
              top: "14%",
              left: "22%",
              width: "35%",
              height: "22%",
              transform: "rotate(-30deg)",
              filter: "blur(0.5px)",
            }}
          />
        </motion.div>
      ))}
    </div>
  );
};

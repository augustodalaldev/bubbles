import { Sparkles, Droplets } from "lucide-react";

export default function App() {
  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="glass-card max-w-lg w-full p-8 rounded-4xl text-center relative overflow-hidden">
        {/* Specular gloss reflection */}
        <div className="bubble-reflection" />
        
        <div className="w-20 h-20 mx-auto bubble-sphere flex items-center justify-center mb-6 shadow-bubble">
          <Droplets className="w-10 h-10 text-white drop-shadow-[0_2px_4px_rgba(4,86,97,0.4)]" />
        </div>

        <h1 className="text-3xl font-extrabold text-bubble-900 tracking-tight flex items-center justify-center gap-2">
          Bubbles <Sparkles className="w-6 h-6 text-soap-400 animate-spin" style={{ animationDuration: "8s" }} />
        </h1>
        <p className="text-bubble-700 mt-2 font-medium">
          Frontend Frutiger Aero & Liquid Glass configurado com sucesso!
        </p>

        <div className="mt-6 p-4 glass-card-subtle rounded-2xl text-sm text-bubble-800">
          Pronto para o <strong>Passo 3: MVP da Tela de Perfil</strong> com bolhas interativas, física de arraste e layout estilo Orkut.
        </div>
      </div>
    </div>
  );
}

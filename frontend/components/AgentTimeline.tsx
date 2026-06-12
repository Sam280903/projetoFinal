"use client";

type AgentStatus = "idle" | "running" | "done" | "error";

interface Agent {
  id: string;
  label: string;
  description: string;
  phase: number;
  color: string;
}

const AGENTS: Agent[] = [
  { id: "market", label: "Market Agent", description: "Pesquisando tamanho de mercado e tendências", phase: 1, color: "indigo" },
  { id: "competitor", label: "Competitor Agent", description: "Mapeando concorrentes e gaps", phase: 1, color: "blue" },
  { id: "audience", label: "Audience Agent", description: "Definindo perfil do cliente ideal", phase: 1, color: "cyan" },
  { id: "risk", label: "Risk Agent", description: "Avaliando riscos e barreiras", phase: 1, color: "orange" },
  { id: "advocate", label: "Advocate Agent", description: "Construindo o caso a favor",         phase: 2, color: "green" },
  { id: "devil",    label: "Devil's Advocate", description: "Desafiando premissas e riscos",     phase: 2, color: "red" },
  { id: "score",    label: "Score Agent",      description: "Calculando score de viabilidade",   phase: 2, color: "yellow" },
  { id: "mediator", label: "Mediator Agent",   description: "Arbitrando o debate estratégico",   phase: 2, color: "purple" },
  { id: "synthesis", label: "Synthesis Agent", description: "Consolidando relatório final",      phase: 3, color: "pink" },
];

const COLOR_MAP: Record<string, string> = {
  indigo:  "border-indigo-500 bg-indigo-500/10 text-indigo-400",
  blue:    "border-blue-500 bg-blue-500/10 text-blue-400",
  cyan:    "border-cyan-500 bg-cyan-500/10 text-cyan-400",
  orange:  "border-orange-500 bg-orange-500/10 text-orange-400",
  green:   "border-green-500 bg-green-500/10 text-green-400",
  red:     "border-red-500 bg-red-500/10 text-red-400",
  purple:  "border-purple-500 bg-purple-500/10 text-purple-400",
  pink:    "border-pink-500 bg-pink-500/10 text-pink-400",
  yellow:  "border-yellow-500 bg-yellow-500/10 text-yellow-400",
};

const DOT_MAP: Record<string, string> = {
  indigo:  "bg-indigo-400",
  blue:    "bg-blue-400",
  cyan:    "bg-cyan-400",
  orange:  "bg-orange-400",
  green:   "bg-green-400",
  red:     "bg-red-400",
  purple:  "bg-purple-400",
  pink:    "bg-pink-400",
  yellow:  "bg-yellow-400",
};

interface Props {
  statuses: Record<string, AgentStatus>;
}

export default function AgentTimeline({ statuses }: Props) {
  const phases = [
    { label: "Fase 1 — Pesquisa Paralela", agents: AGENTS.filter((a) => a.phase === 1) },
    { label: "Fase 2 — Debate Estratégico", agents: AGENTS.filter((a) => a.phase === 2) },
    { label: "Fase 3 — Síntese", agents: AGENTS.filter((a) => a.phase === 3) },
  ];

  return (
    <div className="space-y-6">
      {phases.map((phase) => (
        <div key={phase.label}>
          <p className="text-xs text-zinc-500 uppercase tracking-widest mb-3">{phase.label}</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {phase.agents.map((agent) => {
              const status = statuses[agent.id] || "idle";
              const isRunning = status === "running";
              const isDone = status === "done";
              const colorClass = isDone || isRunning ? COLOR_MAP[agent.color] : "border-zinc-700 bg-zinc-800/30 text-zinc-500";
              const dotClass = isDone || isRunning ? DOT_MAP[agent.color] : "bg-zinc-600";

              return (
                <div
                  key={agent.id}
                  className={`flex items-start gap-3 border rounded-xl p-3 transition-all duration-500 ${colorClass}`}
                >
                  <div className="mt-1 flex-shrink-0">
                    {isDone ? (
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    ) : (
                      <span className={`block w-3 h-3 rounded-full ${dotClass} ${isRunning ? "agent-pulse" : ""}`} />
                    )}
                  </div>
                  <div className="min-w-0">
                    <p className="font-semibold text-sm leading-none mb-1">{agent.label}</p>
                    <p className="text-xs opacity-70 leading-relaxed">{agent.description}</p>
                    {isRunning && (
                      <p className="text-xs mt-1 opacity-50 italic">Processando...</p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}

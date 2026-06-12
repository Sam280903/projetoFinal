"use client";

interface Props {
  advocate: string;
  devil: string;
  mediator: string;
}

export default function DebateView({ advocate, devil, mediator }: Props) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold text-white mb-2">Debate Estratégico</h2>

      {advocate && (
        <div className="border border-green-500/30 bg-green-500/5 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <span className="w-2 h-2 rounded-full bg-green-400" />
            <span className="text-green-400 font-semibold text-sm">Advocate Agent — Em defesa da ideia</span>
          </div>
          <p className="text-zinc-300 text-sm leading-relaxed whitespace-pre-line">{advocate}</p>
        </div>
      )}

      {devil && (
        <div className="border border-red-500/30 bg-red-500/5 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <span className="w-2 h-2 rounded-full bg-red-400" />
            <span className="text-red-400 font-semibold text-sm">Devil's Advocate — Contra-argumentos</span>
          </div>
          <p className="text-zinc-300 text-sm leading-relaxed whitespace-pre-line">{devil}</p>
        </div>
      )}

      {mediator && (
        <div className="border border-purple-500/30 bg-purple-500/5 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <span className="w-2 h-2 rounded-full bg-purple-400" />
            <span className="text-purple-400 font-semibold text-sm">Mediator Agent — Veredicto</span>
          </div>
          <p className="text-zinc-300 text-sm leading-relaxed whitespace-pre-line">{mediator}</p>
        </div>
      )}
    </div>
  );
}

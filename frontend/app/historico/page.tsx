"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface SessionSummary {
  session_id: string;
  idea: string;
  score: number | null;
  timestamp: string;
}

function ScoreBadge({ score }: { score: number | null }) {
  if (score === null) return <span className="text-zinc-500 text-sm">—</span>;
  const color =
    score >= 70 ? "text-green-400 bg-green-400/10 border-green-400/30" :
    score >= 50 ? "text-yellow-400 bg-yellow-400/10 border-yellow-400/30" :
                  "text-red-400 bg-red-400/10 border-red-400/30";
  return (
    <span className={`text-sm font-bold px-2.5 py-0.5 rounded-full border ${color}`}>
      {score}/100
    </span>
  );
}

function formatDate(iso: string) {
  if (!iso) return "";
  try {
    return new Date(iso).toLocaleString("pt-BR", {
      day: "2-digit", month: "short", year: "numeric",
      hour: "2-digit", minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

export default function HistoricoPage() {
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    fetch(`${API_URL}/sessions`)
      .then((r) => r.json())
      .then((data) => setSessions(data.sessions || []))
      .catch(() => setError("Não foi possível carregar o histórico."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="min-h-screen px-4 py-10 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <a href="/" className="text-zinc-500 hover:text-white text-sm mb-3 inline-block transition-colors">
            ← Nova análise
          </a>
          <h1 className="text-3xl font-bold text-white">Histórico de Análises</h1>
          <p className="text-zinc-400 mt-1">
            {sessions.length > 0
              ? `${sessions.length} ideia${sessions.length !== 1 ? "s" : ""} analisada${sessions.length !== 1 ? "s" : ""}`
              : "Suas análises salvas aparecerão aqui"}
          </p>
        </div>
        <div className="text-right">
          <div className="inline-flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/20 rounded-full px-4 py-1.5 text-indigo-400 text-sm">
            <span className="w-2 h-2 rounded-full bg-indigo-400" />
            Base de conhecimento RAG
          </div>
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-20">
          <div className="w-8 h-8 border-2 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin" />
        </div>
      )}

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-400">
          {error}
        </div>
      )}

      {!loading && !error && sessions.length === 0 && (
        <div className="glass-card rounded-2xl p-12 text-center">
          <div className="text-5xl mb-4">💡</div>
          <h2 className="text-xl font-semibold text-white mb-2">Nenhuma análise ainda</h2>
          <p className="text-zinc-400 mb-6">
            Analise sua primeira ideia de negócio para começar a construir sua base de conhecimento.
          </p>
          <a
            href="/"
            className="inline-flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold px-6 py-3 rounded-xl transition-all duration-200"
          >
            Analisar uma ideia →
          </a>
        </div>
      )}

      {!loading && sessions.length > 0 && (
        <div className="space-y-3">
          {sessions.map((s, idx) => (
            <div
              key={s.session_id}
              className="glass-card rounded-xl p-5 hover:border-indigo-500/40 transition-all duration-200 cursor-pointer group"
              onClick={() => router.push(`/resultado/${s.session_id}`)}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-3 flex-1 min-w-0">
                  <span className="text-zinc-600 text-xs font-mono mt-1 shrink-0">
                    #{String(sessions.length - idx).padStart(2, "0")}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-white font-medium leading-snug line-clamp-2 group-hover:text-indigo-300 transition-colors">
                      {s.idea}
                    </p>
                    <p className="text-zinc-500 text-xs mt-1.5">
                      {formatDate(s.timestamp)}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <ScoreBadge score={s.score} />
                  <svg className="w-4 h-4 text-zinc-600 group-hover:text-indigo-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* RAG explanation card */}
      {!loading && sessions.length > 0 && (
        <div className="mt-8 bg-indigo-500/5 border border-indigo-500/20 rounded-xl p-5">
          <div className="flex items-start gap-3">
            <div className="text-indigo-400 text-xl mt-0.5">🧠</div>
            <div>
              <h3 className="text-indigo-300 font-semibold text-sm mb-1">Base de conhecimento ativa</h3>
              <p className="text-zinc-400 text-sm leading-relaxed">
                Cada análise salva é indexada com embeddings vetoriais. Quando você analisa uma nova ideia,
                o sistema busca automaticamente ideias similares e usa esse contexto para enriquecer
                o relatório — isso é <strong className="text-zinc-300">RAG (Retrieval-Augmented Generation)</strong>.
              </p>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}

"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import ReportCard from "@/components/ReportCard";
import ScoreRadar from "@/components/ScoreRadar";
import DebateView from "@/components/DebateView";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface Similar {
  session_id: string;
  idea: string;
  score: number | null;
  similarity: number;
  timestamp: string;
}

export default function ResultadoClient() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();

  const [session, setSession] = useState<any>(null);
  const [score, setScore] = useState<any>(null);
  const [similar, setSimilar] = useState<Similar[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"report" | "debate" | "score">("report");

  useEffect(() => {
    if (!id) return;
    fetch(`${API_URL}/session/${id}`)
      .then((r) => r.json())
      .then((data) => {
        setSession(data);
        if (data.score) {
          try {
            const parsed = typeof data.score === "string" ? JSON.parse(data.score) : data.score;
            if (parsed?.overall) setScore(parsed);
          } catch {}
        }
      })
      .catch(() => router.push("/historico"))
      .finally(() => setLoading(false));

    fetch(`${API_URL}/similar/${id}`)
      .then((r) => r.json())
      .then((data) => setSimilar(data.similar || []))
      .catch(() => {});
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin" />
      </div>
    );
  }

  if (!session) return null;

  const debate = session.debate || {};

  return (
    <main className="min-h-screen px-4 py-10 max-w-5xl mx-auto">
      <div className="mb-6">
        <a href="/historico" className="text-zinc-500 hover:text-white text-sm mb-3 inline-block transition-colors">
          ← Histórico
        </a>
        <h1 className="text-2xl font-bold text-white mb-1">Resultado da Análise</h1>
        <p className="text-zinc-400 italic">"{session.idea}"</p>
      </div>

      {similar.length > 0 && (
        <div className="mb-6 bg-indigo-500/5 border border-indigo-500/20 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-indigo-400">🧠</span>
            <h3 className="text-indigo-300 font-semibold text-sm">
              Ideias similares na base de conhecimento
            </h3>
          </div>
          <div className="space-y-2">
            {similar.map((s) => (
              <div
                key={s.session_id}
                className="flex items-center justify-between bg-zinc-900/60 rounded-lg px-4 py-2.5 cursor-pointer hover:bg-zinc-800/60 transition-colors"
                onClick={() => router.push(`/resultado/${s.session_id}`)}
              >
                <div className="flex-1 min-w-0">
                  <p className="text-zinc-300 text-sm truncate">{s.idea}</p>
                </div>
                <div className="flex items-center gap-3 ml-4 shrink-0">
                  <span className="text-xs text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded-full">
                    {Math.round(s.similarity * 100)}% similar
                  </span>
                  {s.score && (
                    <span className={`text-xs font-bold ${
                      s.score >= 70 ? "text-green-400" :
                      s.score >= 50 ? "text-yellow-400" : "text-red-400"
                    }`}>
                      {s.score}/100
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="flex gap-1 bg-zinc-900 rounded-xl p-1 mb-6">
        {[
          { id: "report", label: "Relatório", available: !!session.report },
          { id: "debate", label: "Debate", available: !!(debate.advocate && debate.devil) },
          { id: "score", label: "Score", available: !!score },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => tab.available && setActiveTab(tab.id as typeof activeTab)}
            className={`flex-1 py-2 text-sm font-medium rounded-lg transition-colors ${
              activeTab === tab.id
                ? "bg-indigo-600 text-white"
                : tab.available
                ? "text-zinc-400 hover:text-white"
                : "text-zinc-600 cursor-not-allowed"
            }`}
          >
            {tab.label}
            {!tab.available && <span className="ml-1 text-xs opacity-50">—</span>}
          </button>
        ))}
      </div>

      {activeTab === "report" && session.report && (
        <ReportCard report={session.report} sessionId={id} />
      )}
      {activeTab === "debate" && (
        <DebateView
          advocate={debate.advocate || ""}
          devil={debate.devil || ""}
          mediator={debate.mediator || ""}
        />
      )}
      {activeTab === "score" && score && (
        <ScoreRadar overall={score.overall} dimensions={score.dimensions} />
      )}
    </main>
  );
}

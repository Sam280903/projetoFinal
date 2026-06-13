"use client";

import { useEffect, useRef, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import AgentTimeline from "@/components/AgentTimeline";
import DebateView from "@/components/DebateView";
import ReportCard from "@/components/ReportCard";
import ScoreRadar from "@/components/ScoreRadar";

type AgentStatus = "idle" | "running" | "done" | "error";

interface DebateData {
  advocate: string;
  devil: string;
  mediator: string;
}

interface ScoreData {
  overall: number;
  dimensions: Record<string, number>;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function AnalysisContent() {
  const params = useSearchParams();
  const idea = params.get("idea") || "";

  const [statuses, setStatuses] = useState<Record<string, AgentStatus>>({});
  const [report, setReport] = useState<string | null>(null);
  const [debate, setDebate] = useState<DebateData>({ advocate: "", devil: "", mediator: "" });
  const [score, setScore] = useState<ScoreData | null>(null);
  const [sessionId, setSessionId] = useState<string>("");
  const [qaQuestion, setQaQuestion] = useState("");
  const [qaAnswer, setQaAnswer] = useState("");
  const [qaLoading, setQaLoading] = useState(false);
  const [phase, setPhase] = useState<"streaming" | "done">("streaming");
  const [activeTab, setActiveTab] = useState<"report" | "debate" | "score">("report");
  const [error, setError] = useState<string | null>(null);
  const [warming, setWarming] = useState(false);
  const [similarIdeas, setSimilarIdeas] = useState<Array<{ session_id: string; idea: string; score: number | null; similarity: number }>>([]);

  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!idea) return;

    const url = `${API_URL}/analyze`;
    const warmTimeout = setTimeout(() => setWarming(true), 5000);
    fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ idea }),
      signal: AbortSignal.timeout(120000),
    }).then((res) => {
      clearTimeout(warmTimeout);
      setWarming(false);
      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      function processLine(line: string) {
        if (!line.startsWith("data: ")) return;
        try {
          const payload = JSON.parse(line.slice(6));
          const { agent, status, data } = payload;

          if (agent === "session" && status === "start") {
            setSessionId(data);
            return;
          }

          if (agent === "pipeline" && status === "complete") {
            setPhase("done");
            return;
          }

          if (agent === "rag" && status === "done" && data) {
            try {
              const parsed = JSON.parse(data);
              if (Array.isArray(parsed) && parsed.length > 0) setSimilarIdeas(parsed);
            } catch {}
            return;
          }

          setStatuses((prev) => ({ ...prev, [agent]: status as AgentStatus }));

          if (status === "done" && data) {
            if (agent === "synthesis") {
              setReport(data);
              // Fallback: tenta extrair score do relatório se score agent não retornou
              const match = data.match(/```json\s*([\s\S]*?)```/);
              if (match) {
                try {
                  const parsed = JSON.parse(match[1]);
                  setScore((prev) => prev ?? parsed);
                } catch {}
              }
            }
            // Score agent separado — aparece muito antes da synthesis
            if (agent === "score") {
              try {
                const cleaned = data.replace(/```json\s*/g, "").replace(/```/g, "").trim();
                const parsed = JSON.parse(cleaned);
                if (parsed.overall && parsed.dimensions) setScore(parsed);
              } catch {}
            }
            if (agent === "advocate") setDebate((p) => ({ ...p, advocate: data }));
            if (agent === "devil") setDebate((p) => ({ ...p, devil: data }));
            if (agent === "mediator") setDebate((p) => ({ ...p, mediator: data }));
          }
        } catch {}
      }

      function pump() {
        reader.read().then(({ value, done }) => {
          if (done) return;
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";
          lines.forEach(processLine);
          pump();
        }).catch((e) => {
          setError("Erro na conexão com o servidor.");
        });
      }

      pump();
    }).catch(() => {
      clearTimeout(warmTimeout);
      setWarming(false);
      setError("Não foi possível conectar ao servidor. Verifique se o backend está rodando.");
    });
  }, [idea]);

  async function handleQA(e: React.FormEvent) {
    e.preventDefault();
    if (!qaQuestion.trim() || !sessionId || qaLoading) return;
    setQaLoading(true);
    setQaAnswer("");
    try {
      const res = await fetch(`${API_URL}/qa`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, question: qaQuestion }),
      });
      const data = await res.json();
      setQaAnswer(data.answer || data.detail || "Sem resposta.");
    } catch {
      setQaAnswer("Erro ao consultar o agente.");
    } finally {
      setQaLoading(false);
    }
  }

  const doneCount = Object.values(statuses).filter((s) => s === "done").length;
  const runningAgents = Object.entries(statuses).filter(([, s]) => s === "running").map(([id]) => id);

  return (
    <main className="min-h-screen px-4 py-10 max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <a href="/" className="text-zinc-500 hover:text-white text-sm mb-4 inline-block transition-colors">
          ← Nova análise
        </a>
        <h1 className="text-2xl font-bold text-white mb-2">Analisando sua ideia</h1>
        <p className="text-zinc-400 italic">"{idea}"</p>
      </div>

      {warming && !error && (
        <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4 mb-6 text-yellow-400 flex items-center gap-3">
          <svg className="animate-spin h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
          </svg>
          Aquecendo o servidor (primeira requisição pode levar até 30s)...
        </div>
      )}

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 mb-6 text-red-400">
          {error}
        </div>
      )}

      {/* Progress */}
      {phase === "streaming" && (
        <div className="glass-card rounded-xl p-4 mb-6">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm text-zinc-400">
              {runningAgents.length > 0
                ? `${runningAgents.length} agente(s) ativos...`
                : doneCount === 0
                ? "Iniciando agentes..."
                : "Processando..."}
            </span>
            <span className="text-sm text-zinc-500">{doneCount}/9 concluídos</span>
          </div>
          <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all duration-500"
              style={{ width: `${(doneCount / 9) * 100}%` }}
            />
          </div>
        </div>
      )}

      {/* Banner RAG: aparece assim que ideias similares chegam */}
      {similarIdeas.length > 0 && (
        <div className="bg-indigo-500/5 border border-indigo-500/20 rounded-xl p-4 mb-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-indigo-400">🧠</span>
            <span className="text-indigo-300 text-sm font-semibold">
              {similarIdeas.length} ideia{similarIdeas.length > 1 ? "s similares" : " similar"} encontrada{similarIdeas.length > 1 ? "s" : ""} na base de conhecimento
            </span>
          </div>
          <div className="space-y-1.5">
            {similarIdeas.map((s) => (
              <a
                key={s.session_id}
                href={`/resultado/${s.session_id}`}
                className="flex items-center justify-between bg-zinc-900/60 rounded-lg px-3 py-2 hover:bg-zinc-800/60 transition-colors"
              >
                <span className="text-zinc-300 text-xs truncate flex-1">{s.idea}</span>
                <span className="text-indigo-400 text-xs ml-3 shrink-0">{Math.round(s.similarity * 100)}% similar</span>
                {s.score && (
                  <span className={`text-xs font-bold ml-2 shrink-0 ${s.score >= 70 ? "text-green-400" : s.score >= 50 ? "text-yellow-400" : "text-red-400"}`}>
                    {s.score}/100
                  </span>
                )}
              </a>
            ))}
          </div>
        </div>
      )}

      {phase === "done" && (
        <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-4 mb-6 text-green-400 flex items-center gap-2">
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
          Análise completa! Todos os 9 agentes finalizaram.
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Agent Timeline */}
        <div className="lg:col-span-1">
          <AgentTimeline statuses={statuses} />
        </div>

        {/* Right: Results */}
        <div className="lg:col-span-2 space-y-6">
          {/* Score aparece assim que a fase 2 termina, antes do relatório */}
          {score && !report && (
            <div className="space-y-3">
              <div className="bg-indigo-500/10 border border-indigo-500/30 rounded-xl p-3 text-indigo-400 text-sm flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-indigo-400 agent-pulse inline-block" />
                Score pronto! Aguardando síntese final do relatório...
              </div>
              <ScoreRadar overall={score.overall} dimensions={score.dimensions} />
            </div>
          )}

          {(report || (debate.advocate && debate.devil)) && (
            <>
              {/* Tabs */}
              <div className="flex gap-1 bg-zinc-900 rounded-xl p-1">
                {[
                  { id: "report", label: "Relatório", available: !!report },
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
                    {!tab.available && <span className="ml-1 text-xs opacity-50">...</span>}
                  </button>
                ))}
              </div>

              {activeTab === "report" && report && <ReportCard report={report} sessionId={sessionId} />}
              {activeTab === "report" && !report && (
                <div className="glass-card rounded-xl p-8 text-center">
                  <div className="w-6 h-6 border-2 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin mx-auto mb-3" />
                  <p className="text-zinc-400 text-sm">Gerando relatório completo...</p>
                </div>
              )}
              {activeTab === "debate" && <DebateView {...debate} />}
              {activeTab === "score" && score && (
                <ScoreRadar overall={score.overall} dimensions={score.dimensions} />
              )}

              {/* Q&A Agent */}
              {phase === "done" && (
                <div className="glass-card rounded-xl p-5">
                  <h3 className="font-bold text-white mb-1">Q&A Agent</h3>
                  <p className="text-zinc-500 text-xs mb-4">
                    Faça perguntas específicas sobre o relatório gerado.
                  </p>
                  <form onSubmit={handleQA} className="flex gap-2">
                    <input
                      type="text"
                      value={qaQuestion}
                      onChange={(e) => setQaQuestion(e.target.value)}
                      placeholder="Ex: Como me diferenciar do concorrente X?"
                      className="flex-1 bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-2 text-sm text-white placeholder-zinc-500 outline-none focus:border-indigo-500"
                    />
                    <button
                      type="submit"
                      disabled={qaLoading || !qaQuestion.trim()}
                      className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white text-sm px-4 py-2 rounded-lg transition-colors"
                    >
                      {qaLoading ? "..." : "Perguntar"}
                    </button>
                  </form>
                  {qaAnswer && (
                    <div className="mt-4 bg-zinc-900 rounded-lg p-4 text-zinc-300 text-sm leading-relaxed">
                      {qaAnswer}
                    </div>
                  )}
                </div>
              )}
            </>
          )}

          {!score && !debate.advocate && phase === "streaming" && (
            <div className="glass-card rounded-xl p-8 text-center">
              <div className="w-8 h-8 border-2 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin mx-auto mb-4" />
              <p className="text-zinc-400">Os agentes estão pesquisando...</p>
              <p className="text-zinc-600 text-sm mt-1">Score e debate aparecerão aqui em breve</p>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

export default function AnalysisPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin" />
      </div>
    }>
      <AnalysisContent />
    </Suspense>
  );
}

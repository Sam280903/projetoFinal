"use client";

import { useState } from "react";

interface Props {
  report: string;
  sessionId?: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ReportCard({ report, sessionId }: Props) {
  const [copied, setCopied] = useState(false);
  const [downloading, setDownloading] = useState(false);

  function copyReport() {
    navigator.clipboard.writeText(report);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  async function downloadPDF() {
    if (!sessionId) return;
    setDownloading(true);
    try {
      const res = await fetch(`${API_URL}/export-pdf/${sessionId}`);
      if (!res.ok) throw new Error("Erro ao gerar PDF");
      const disposition = res.headers.get("Content-Disposition") || "";
      const match = disposition.match(/filename="?([^"]+)"?/);
      const filename = match ? match[1] : "pitchiq-relatorio.pdf";
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      alert("Não foi possível gerar o PDF.");
    } finally {
      setDownloading(false);
    }
  }

  // Remove the JSON block at the end (it's used for the score radar)
  const cleanReport = report.replace(/```json[\s\S]*?```/g, "").trim();

  // Split into sections by markdown headers
  const sections = cleanReport.split(/(?=^#{1,2} )/m).filter(Boolean);

  function renderSection(text: string, i: number) {
    const lines = text.split("\n");
    const header = lines[0];
    const body = lines.slice(1).join("\n").trim();
    const title = header.replace(/^#+\s*/, "");

    return (
      <div key={i} className="glass-card rounded-xl p-5">
        <h3 className="font-bold text-white mb-3 flex items-center gap-2">
          <span className="text-indigo-400 text-sm font-mono">{String(i + 1).padStart(2, "0")}</span>
          {title}
        </h3>
        <div className="text-zinc-300 text-sm leading-relaxed whitespace-pre-line">{body}</div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-white">Relatório Completo</h2>
        <div className="flex gap-2">
          {sessionId && (
            <button
              onClick={downloadPDF}
              disabled={downloading}
              className="text-sm text-indigo-400 hover:text-white border border-indigo-700 hover:border-indigo-500 px-3 py-1.5 rounded-lg transition-colors disabled:opacity-40 flex items-center gap-1.5"
            >
              {downloading ? (
                <><span className="w-3 h-3 border border-indigo-400/40 border-t-indigo-400 rounded-full animate-spin" /> Gerando...</>
              ) : (
                <>
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3M3 17V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
                  </svg>
                  Baixar PDF
                </>
              )}
            </button>
          )}
          <button
            onClick={copyReport}
            className="text-sm text-zinc-400 hover:text-white border border-zinc-700 hover:border-zinc-500 px-3 py-1.5 rounded-lg transition-colors"
          >
            {copied ? "Copiado!" : "Copiar"}
          </button>
        </div>
      </div>
      <div className="space-y-3">
        {sections.length > 1 ? sections.map(renderSection) : (
          <div className="glass-card rounded-xl p-5">
            <p className="text-zinc-300 text-sm leading-relaxed whitespace-pre-line">{cleanReport}</p>
          </div>
        )}
      </div>
    </div>
  );
}

"use client";

import { useState } from "react";

interface Props {
  report: string;
  sessionId?: string;
}

export default function ReportCard({ report }: Props) {
  const [copied, setCopied] = useState(false);

  function copyReport() {
    navigator.clipboard.writeText(report);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
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

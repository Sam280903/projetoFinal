"use client";

import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer } from "recharts";

interface Props {
  overall: number;
  dimensions: Record<string, number>;
}

const LABELS: Record<string, string> = {
  mercado: "Mercado",
  competicao: "Competição",
  execucao: "Execução",
  timing: "Timing",
  monetizacao: "Monetização",
  inovacao: "Inovação",
};

function scoreColor(score: number) {
  if (score >= 70) return "text-green-400";
  if (score >= 50) return "text-yellow-400";
  return "text-red-400";
}

export default function ScoreRadar({ overall, dimensions }: Props) {
  const data = Object.entries(dimensions).map(([key, value]) => ({
    subject: LABELS[key] || key,
    value,
    fullMark: 100,
  }));

  return (
    <div className="glass-card rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="font-bold text-white text-lg">Score de Viabilidade</h3>
        <div className="text-center">
          <div className={`text-4xl font-bold ${scoreColor(overall)}`}>{overall}</div>
          <div className="text-zinc-500 text-xs">/ 100</div>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={240}>
        <RadarChart data={data}>
          <PolarGrid stroke="#ffffff15" />
          <PolarAngleAxis
            dataKey="subject"
            tick={{ fill: "#9ca3af", fontSize: 12 }}
          />
          <Radar
            name="Score"
            dataKey="value"
            stroke="#6366f1"
            fill="#6366f1"
            fillOpacity={0.3}
          />
        </RadarChart>
      </ResponsiveContainer>

      <div className="grid grid-cols-3 gap-2 mt-4">
        {Object.entries(dimensions).map(([key, value]) => (
          <div key={key} className="text-center">
            <div className={`text-xl font-bold ${scoreColor(value)}`}>{value}</div>
            <div className="text-zinc-500 text-xs">{LABELS[key] || key}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

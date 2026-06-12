import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PitchIQ — Validação Estratégica de Negócios com IA",
  description: "Uma equipe de 9 agentes de IA analisa, debate e valida sua ideia de negócio em minutos.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" className="h-full antialiased">
      <body className="min-h-full flex flex-col bg-[#0a0a0f] text-[#e8e8f0]">
        {children}
      </body>
    </html>
  );
}

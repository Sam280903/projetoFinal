"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const EXAMPLES = [
  "Aplicativo de delivery de refeições saudáveis focado em academias",
  "Plataforma SaaS de gestão financeira para MEIs e pequenas empresas",
  "Marketplace de serviços domésticos com pagamento recorrente",
  "App de telemedicina para cidades do interior do Brasil",
];

export default function Home() {
  const [idea, setIdea] = useState("");
  const [loading, setLoading] = useState(false);
  const [image, setImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [analyzingImage, setAnalyzingImage] = useState(false);
  const [listening, setListening] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const recognitionRef = useRef<any>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  useEffect(() => {
    setSpeechSupported(!!(typeof window !== "undefined" && ((window as any).SpeechRecognition || (window as any).webkitSpeechRecognition)));
  }, []);

  function toggleVoice() {
    if (listening) {
      recognitionRef.current?.stop();
      setListening(false);
      return;
    }
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = "pt-BR";
    recognition.continuous = true;
    recognition.interimResults = true;
    let finalTranscript = idea;
    recognition.onresult = (e: any) => {
      let interim = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        if (e.results[i].isFinal) finalTranscript += e.results[i][0].transcript;
        else interim = e.results[i][0].transcript;
      }
      setIdea(finalTranscript + interim);
    };
    recognition.onend = () => setListening(false);
    recognition.onerror = () => setListening(false);
    recognitionRef.current = recognition;
    recognition.start();
    setListening(true);
  }

  function handleImageChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setImage(file);
    setImagePreview(URL.createObjectURL(file));
  }

  function removeImage() {
    setImage(null);
    setImagePreview(null);
    if (fileRef.current) fileRef.current.value = "";
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!idea.trim() || loading) return;
    setLoading(true);

    let imageContext = "";

    // Se houver imagem, analisa com Vision Agent primeiro
    if (image) {
      setAnalyzingImage(true);
      try {
        const formData = new FormData();
        formData.append("file", image);
        const res = await fetch(`${API_URL}/analyze-image`, {
          method: "POST",
          body: formData,
        });
        if (res.ok) {
          const data = await res.json();
          imageContext = data.description || "";
        }
      } catch {}
      setAnalyzingImage(false);
    }

    // Guarda image_context no sessionStorage para a página de análise
    if (imageContext) {
      sessionStorage.setItem("image_context", imageContext);
      sessionStorage.setItem("image_preview", imagePreview || "");
    } else {
      sessionStorage.removeItem("image_context");
      sessionStorage.removeItem("image_preview");
    }

    const encoded = encodeURIComponent(idea.trim());
    router.push(`/analysis?idea=${encoded}`);
  }

  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4 py-16">
      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 flex justify-end px-6 py-4 z-10">
        <a
          href="/historico"
          className="text-sm text-zinc-400 hover:text-white flex items-center gap-1.5 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Histórico
        </a>
      </nav>

      {/* Header */}
      <div className="text-center mb-12 max-w-2xl">
        <div className="inline-flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/20 rounded-full px-4 py-1.5 text-indigo-400 text-sm mb-6">
          <span className="w-2 h-2 rounded-full bg-indigo-400 agent-pulse inline-block" />
          9 agentes de IA trabalhando em paralelo
        </div>
        <h1 className="text-5xl font-bold mb-4 leading-tight">
          <span className="gradient-text">PitchIQ</span>
        </h1>
        <p className="text-xl text-zinc-400 leading-relaxed">
          Descreva sua ideia de negócio. Uma equipe de agentes de IA vai
          debater, pesquisar e analisar — em 3 minutos você sabe se ela tem futuro.
        </p>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="w-full max-w-2xl">
        <div className="glass-card rounded-2xl p-1">
          <textarea
            value={idea}
            onChange={(e) => setIdea(e.target.value)}
            placeholder="Ex: Aplicativo de gestão financeira para MEIs com IA integrada..."
            className="w-full bg-transparent text-white placeholder-zinc-500 text-lg p-5 rounded-xl outline-none resize-none min-h-[120px]"
            rows={4}
            disabled={loading}
          />

          {/* Upload de imagem */}
          <div className="px-4 pb-2">
            {imagePreview ? (
              <div className="flex items-center gap-3 bg-zinc-800/60 rounded-xl p-3">
                <img src={imagePreview} alt="Preview" className="w-16 h-16 object-cover rounded-lg border border-zinc-700" />
                <div className="flex-1 min-w-0">
                  <p className="text-zinc-300 text-sm font-medium truncate">{image?.name}</p>
                  <p className="text-zinc-500 text-xs mt-0.5">
                    {analyzingImage ? (
                      <span className="text-indigo-400 flex items-center gap-1">
                        <span className="w-3 h-3 border border-indigo-400/30 border-t-indigo-400 rounded-full animate-spin inline-block" />
                        Analisando imagem com GPT-4o Vision...
                      </span>
                    ) : "Imagem será analisada pelo Vision Agent"}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={removeImage}
                  className="text-zinc-500 hover:text-red-400 transition-colors p-1"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => fileRef.current?.click()}
                className="flex items-center gap-2 text-sm text-zinc-500 hover:text-indigo-400 transition-colors py-1"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                Adicionar imagem do produto/logo (opcional)
              </button>
            )}
            <input
              ref={fileRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              className="hidden"
              onChange={handleImageChange}
            />
          </div>

          <div className="flex items-center justify-between px-4 pb-3">
            <div className="flex items-center gap-3">
              <span className="text-zinc-500 text-sm">{idea.length} caracteres</span>
              {speechSupported && (
                <button
                  type="button"
                  onClick={toggleVoice}
                  title={listening ? "Parar gravação" : "Falar ideia"}
                  className={`flex items-center gap-1.5 text-sm px-3 py-1.5 rounded-lg border transition-all duration-200 ${
                    listening
                      ? "bg-red-500/20 border-red-500/50 text-red-400 animate-pulse"
                      : "border-zinc-700 text-zinc-400 hover:border-indigo-500 hover:text-indigo-400"
                  }`}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                  </svg>
                  {listening ? "Gravando..." : "Falar"}
                </button>
              )}
            </div>
            <button
              type="submit"
              disabled={!idea.trim() || loading}
              className="flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold px-6 py-2.5 rounded-xl transition-all duration-200"
            >
              {loading ? (
                <>
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  {analyzingImage ? "Analisando imagem..." : "Iniciando..."}
                </>
              ) : (
                "Analisar ideia →"
              )}
            </button>
          </div>
        </div>
      </form>

      {/* Examples */}
      <div className="mt-8 max-w-2xl w-full">
        <p className="text-zinc-500 text-sm mb-3 text-center">Ou experimente com um exemplo:</p>
        <div className="flex flex-wrap gap-2 justify-center">
          {EXAMPLES.map((ex) => (
            <button
              key={ex}
              onClick={() => setIdea(ex)}
              className="text-sm text-zinc-400 border border-zinc-700 hover:border-indigo-500 hover:text-indigo-400 rounded-full px-4 py-1.5 transition-colors"
            >
              {ex.length > 50 ? ex.slice(0, 50) + "..." : ex}
            </button>
          ))}
        </div>
      </div>

      {/* How it works */}
      <div className="mt-16 max-w-3xl w-full">
        <h2 className="text-center text-zinc-400 text-sm uppercase tracking-widest mb-8">
          Como funciona
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            {
              step: "01",
              title: "Pesquisa em paralelo",
              desc: "4 agentes especializados buscam dados reais: mercado, concorrentes, perfil de cliente e riscos.",
              color: "indigo",
            },
            {
              step: "02",
              title: "Debate adversarial",
              desc: "Um agente defende a ideia com força. Outro tenta destruí-la. Um terceiro arbitra o resultado.",
              color: "purple",
            },
            {
              step: "03",
              title: "Relatório + Score",
              desc: "Relatório executivo completo com SWOT, go-to-market e score de viabilidade de 0-100.",
              color: "pink",
            },
          ].map((item) => (
            <div key={item.step} className="glass-card rounded-xl p-5">
              <div className={`text-${item.color}-400 text-xs font-mono mb-2`}>{item.step}</div>
              <h3 className="font-semibold text-white mb-2">{item.title}</h3>
              <p className="text-zinc-400 text-sm leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}

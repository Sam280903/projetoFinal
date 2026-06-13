// Server Component — exporta generateStaticParams para o build estático
import ResultadoClient from "./ResultadoClient";

export function generateStaticParams() {
  return [{ id: "placeholder" }];
}

export default function ResultadoPage() {
  return <ResultadoClient />;
}

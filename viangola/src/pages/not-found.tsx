import { Link } from "wouter";
import { MapPin } from "lucide-react";

export default function NotFound() {
  return (
    <div className="flex min-h-[70dvh] flex-col items-center justify-center px-5 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[hsl(var(--accent))] text-[hsl(var(--primary))]">
        <MapPin className="h-7 w-7" />
      </div>
      <p className="mt-6 font-mono text-[10px] uppercase tracking-[.22em] text-[hsl(var(--muted-foreground))]">
        Erro 404
      </p>
      <h1 className="mt-2 font-display text-3xl font-bold tracking-tight text-[hsl(var(--foreground))]">
        Esta rota não existe
      </h1>
      <p className="mt-3 max-w-md text-sm leading-6 text-[hsl(var(--muted-foreground))]">
        A página que procura foi desviada ou nunca esteve no mapa. Volte ao
        início para continuar a viagem.
      </p>
      <Link
        href="/"
        data-testid="link-back-home"
        className="mt-7 inline-flex items-center gap-2 rounded-xl bg-[hsl(var(--primary))] px-5 py-3 text-sm font-bold text-[hsl(var(--primary-foreground))] transition-transform hover:-translate-y-0.5"
      >
        Voltar ao início
      </Link>
    </div>
  );
}

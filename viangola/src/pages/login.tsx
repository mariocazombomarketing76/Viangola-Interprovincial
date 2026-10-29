import { useState, type FormEvent } from 'react';
import { Link, Redirect, useLocation, useSearch } from 'wouter';
import { Navigation } from 'lucide-react';
import { useLogin } from '@workspace/api-client-react';
import { landingPathFor, setSession, useAuth } from '@/lib/auth';

function Brand() {
  return (
    <div className="flex items-center justify-center gap-3">
      <div className="relative flex h-10 w-10 items-center justify-center overflow-hidden rounded-[13px] bg-[hsl(var(--accent))] text-[hsl(var(--primary))]">
        <Navigation className="relative z-10 h-5 w-5 -rotate-45" />
      </div>
      <div>
        <div className="font-display text-[17px] font-bold tracking-tight">viangola</div>
        <div className="font-mono text-[9px] tracking-[.16em] opacity-60">INTERPROVINCIAL</div>
      </div>
    </div>
  );
}

export default function Login() {
  const { session } = useAuth();
  const [, navigate] = useLocation();
  const search = useSearch();
  const login = useLogin();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const nextParam = new URLSearchParams(search).get('next');
  const target = nextParam && nextParam.startsWith('/') ? nextParam : null;

  if (session) return <Redirect to={target ?? landingPathFor(session.user.role)} />;

  const errorStatus = (login.error as { status?: number } | null)?.status;
  const errorMessage =
    errorStatus === 401
      ? 'Email ou password incorretos.'
      : 'Não foi possível iniciar sessão. Tente novamente.';

  const submit = (event: FormEvent) => {
    event.preventDefault();
    login.mutate(
      { data: { email, password } },
      {
        onSuccess: (tokens) => {
          setSession(tokens);
          navigate(target ?? landingPathFor(tokens.user.role));
        },
      },
    );
  };

  return (
    <div className="mx-auto flex min-h-[100dvh] max-w-md flex-col justify-center px-5 py-12">
      <Brand />
      <div className="mt-8 rounded-[24px] border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-7">
        <p className="font-mono text-[10px] uppercase tracking-[.22em] text-[hsl(var(--muted-foreground))]">
          Área de acesso
        </p>
        <h1 className="mt-2 font-display text-2xl font-bold tracking-tight">Entrar na sua conta</h1>
        <form onSubmit={submit} className="mt-6 space-y-4">
          <label className="block text-xs font-bold text-[hsl(var(--muted-foreground))]">
            Email
            <input
              data-testid="input-login-email"
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="nome@email.ao"
              className="mt-1 w-full rounded-xl border border-[hsl(var(--input))] bg-[hsl(var(--background))] px-4 py-3 text-sm font-normal text-[hsl(var(--foreground))] outline-none focus:border-[hsl(var(--accent))]"
            />
          </label>
          <label className="block text-xs font-bold text-[hsl(var(--muted-foreground))]">
            Password
            <input
              data-testid="input-login-password"
              type="password"
              required
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="••••••••"
              className="mt-1 w-full rounded-xl border border-[hsl(var(--input))] bg-[hsl(var(--background))] px-4 py-3 text-sm font-normal text-[hsl(var(--foreground))] outline-none focus:border-[hsl(var(--accent))]"
            />
          </label>
          {login.isError && (
            <p
              data-testid="status-login-error"
              className="rounded-xl bg-[#f9dfda] p-3 text-sm font-bold text-[#a13d34]"
            >
              {errorMessage}
            </p>
          )}
          <button
            data-testid="button-submit-login"
            type="submit"
            disabled={login.isPending}
            className="w-full rounded-xl bg-[hsl(var(--primary))] py-3 text-sm font-bold text-[hsl(var(--primary-foreground))] transition-transform hover:-translate-y-0.5 disabled:opacity-60"
          >
            {login.isPending ? 'A entrar…' : 'Entrar'}
          </button>
        </form>
        <p className="mt-5 text-center text-sm text-[hsl(var(--muted-foreground))]">
          Ainda não tem conta?{' '}
          <Link
            href="/register"
            data-testid="link-goto-register"
            className="font-bold text-[hsl(var(--primary))] hover:underline"
          >
            Registar
          </Link>
        </p>
      </div>
      <div
        data-testid="hint-demo-accounts"
        className="mt-5 rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--muted))] p-4 text-xs leading-6 text-[hsl(var(--muted-foreground))]"
      >
        <p className="font-bold text-[hsl(var(--foreground))]">Contas de demonstração</p>
        <p>Admin · admin@viangola.ao · Admin123!</p>
        <p>Motorista · driver@viangola.ao · Driver123!</p>
        <p>Passageiro · maria@viangola.ao · Passenger123!</p>
      </div>
    </div>
  );
}

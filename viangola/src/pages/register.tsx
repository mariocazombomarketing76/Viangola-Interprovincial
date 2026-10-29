import { useState, type FormEvent } from 'react';
import { Link, Redirect, useLocation } from 'wouter';
import { Navigation } from 'lucide-react';
import { useRegister, type RegisterInput } from '@workspace/api-client-react';
import { landingPathFor, setSession, useAuth } from '@/lib/auth';

const roleOptions: { value: RegisterInput['role']; label: string; hint: string }[] = [
  { value: 'passenger', label: 'Passageiro', hint: 'Reservar lugares e viajar' },
  { value: 'driver', label: 'Motorista', hint: 'Gerir as minhas viagens' },
];

export default function Register() {
  const { session } = useAuth();
  const [, navigate] = useLocation();
  const register = useRegister();
  const [form, setForm] = useState({
    fullName: '',
    email: '',
    phone: '',
    password: '',
    role: 'passenger' as RegisterInput['role'],
  });

  if (session) return <Redirect to={landingPathFor(session.user.role)} />;

  const errorStatus = (register.error as { status?: number } | null)?.status;
  const errorMessage =
    errorStatus === 409
      ? 'Este email ou telefone já está registado.'
      : errorStatus === 422
        ? 'Verifique os dados: password mínimo de 8 caracteres e campos obrigatórios.'
        : 'Não foi possível criar a conta. Tente novamente.';

  const submit = (event: FormEvent) => {
    event.preventDefault();
    register.mutate(
      {
        data: {
          fullName: form.fullName,
          email: form.email,
          password: form.password,
          ...(form.phone ? { phone: form.phone } : {}),
          role: form.role,
        },
      },
      {
        onSuccess: (tokens) => {
          setSession(tokens);
          navigate(landingPathFor(tokens.user.role));
        },
      },
    );
  };

  const field =
    'mt-1 w-full rounded-xl border border-[hsl(var(--input))] bg-[hsl(var(--background))] px-4 py-3 text-sm font-normal text-[hsl(var(--foreground))] outline-none focus:border-[hsl(var(--accent))]';

  return (
    <div className="mx-auto flex min-h-[100dvh] max-w-md flex-col justify-center px-5 py-12">
      <div className="flex items-center justify-center gap-3">
        <div className="relative flex h-10 w-10 items-center justify-center overflow-hidden rounded-[13px] bg-[hsl(var(--accent))] text-[hsl(var(--primary))]">
          <Navigation className="relative z-10 h-5 w-5 -rotate-45" />
        </div>
        <div>
          <div className="font-display text-[17px] font-bold tracking-tight">viangola</div>
          <div className="font-mono text-[9px] tracking-[.16em] opacity-60">INTERPROVINCIAL</div>
        </div>
      </div>
      <div className="mt-8 rounded-[24px] border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-7">
        <p className="font-mono text-[10px] uppercase tracking-[.22em] text-[hsl(var(--muted-foreground))]">
          Nova conta
        </p>
        <h1 className="mt-2 font-display text-2xl font-bold tracking-tight">Criar a sua conta</h1>
        <form onSubmit={submit} className="mt-6 space-y-4">
          <label className="block text-xs font-bold text-[hsl(var(--muted-foreground))]">
            Nome completo
            <input
              data-testid="input-register-fullname"
              required
              minLength={2}
              autoComplete="name"
              value={form.fullName}
              onChange={(event) => setForm({ ...form, fullName: event.target.value })}
              placeholder="O seu nome"
              className={field}
            />
          </label>
          <label className="block text-xs font-bold text-[hsl(var(--muted-foreground))]">
            Email
            <input
              data-testid="input-register-email"
              type="email"
              required
              autoComplete="email"
              value={form.email}
              onChange={(event) => setForm({ ...form, email: event.target.value })}
              placeholder="nome@email.ao"
              className={field}
            />
          </label>
          <label className="block text-xs font-bold text-[hsl(var(--muted-foreground))]">
            Telefone (opcional)
            <input
              data-testid="input-register-phone"
              type="tel"
              autoComplete="tel"
              value={form.phone}
              onChange={(event) => setForm({ ...form, phone: event.target.value })}
              placeholder="+244 9…"
              className={field}
            />
          </label>
          <label className="block text-xs font-bold text-[hsl(var(--muted-foreground))]">
            Password
            <input
              data-testid="input-register-password"
              type="password"
              required
              minLength={8}
              autoComplete="new-password"
              value={form.password}
              onChange={(event) => setForm({ ...form, password: event.target.value })}
              placeholder="Mínimo 8 caracteres"
              className={field}
            />
          </label>
          <div>
            <p className="text-xs font-bold text-[hsl(var(--muted-foreground))]">Tipo de conta</p>
            <div className="mt-2 grid gap-2 sm:grid-cols-2">
              {roleOptions.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  data-testid={`button-role-${option.value}`}
                  onClick={() => setForm({ ...form, role: option.value })}
                  className={`rounded-xl border p-3 text-left transition-colors ${
                    form.role === option.value
                      ? 'border-[hsl(var(--accent))] bg-[hsl(var(--accent))]/20'
                      : 'border-[hsl(var(--border))] bg-[hsl(var(--background))] hover:border-[hsl(var(--muted-foreground))]'
                  }`}
                >
                  <span className="block text-sm font-bold text-[hsl(var(--foreground))]">
                    {option.label}
                  </span>
                  <span className="mt-0.5 block text-[11px] text-[hsl(var(--muted-foreground))]">
                    {option.hint}
                  </span>
                </button>
              ))}
            </div>
          </div>
          {register.isError && (
            <p
              data-testid="status-register-error"
              className="rounded-xl bg-[#f9dfda] p-3 text-sm font-bold text-[#a13d34]"
            >
              {errorMessage}
            </p>
          )}
          <button
            data-testid="button-submit-register"
            type="submit"
            disabled={register.isPending}
            className="w-full rounded-xl bg-[hsl(var(--primary))] py-3 text-sm font-bold text-[hsl(var(--primary-foreground))] transition-transform hover:-translate-y-0.5 disabled:opacity-60"
          >
            {register.isPending ? 'A criar conta…' : 'Criar conta'}
          </button>
        </form>
        <p className="mt-5 text-center text-sm text-[hsl(var(--muted-foreground))]">
          Já tem conta?{' '}
          <Link
            href="/login"
            data-testid="link-goto-login"
            className="font-bold text-[hsl(var(--primary))] hover:underline"
          >
            Entrar
          </Link>
        </p>
      </div>
    </div>
  );
}

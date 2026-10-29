import { Link, useLocation } from 'wouter';
import { BadgeCheck, LogOut, Mail, Phone, ShieldCheck, UserRound } from 'lucide-react';
import { getGetMeQueryKey, useGetMe } from '@workspace/api-client-react';
import { useAuth } from '@/lib/auth';

const roleLabels: Record<string, string> = {
  admin: 'Administrador',
  driver: 'Motorista',
  passenger: 'Passageiro',
};

const dateTime = (value?: string | null) =>
  value
    ? new Intl.DateTimeFormat('pt-PT', {
        day: '2-digit',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      }).format(new Date(value))
    : '—';

export default function Profile() {
  const { session, logout } = useAuth();
  const [, navigate] = useLocation();
  const me = useGetMe({ query: { enabled: !!session, queryKey: getGetMeQueryKey() } });
  const user = me.data ?? session?.user;

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="mx-auto max-w-2xl">
      <p className="font-mono text-[10px] font-medium uppercase tracking-[.22em] text-[hsl(var(--muted-foreground))]">
        Conta
      </p>
      <h1 className="mt-2 font-display text-3xl font-bold tracking-tight md:text-4xl">O meu perfil</h1>
      <p className="mt-2 text-sm leading-6 text-[hsl(var(--muted-foreground))]">
        Dados da sua conta Viangola e gestão da sessão.
      </p>

      <div className="mt-7 rounded-[24px] border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6">
        <div className="flex items-center gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-[hsl(var(--accent))] font-display text-lg font-extrabold text-[hsl(var(--primary))]">
            {(user?.fullName || '?')
              .split(' ')
              .map((part) => part[0])
              .slice(0, 2)
              .join('')}
          </div>
          <div className="min-w-0">
            <p data-testid="profile-fullname" className="truncate font-display text-xl font-bold">
              {me.isLoading ? '…' : user?.fullName ?? '—'}
            </p>
            <span
              data-testid="profile-role"
              className="mt-1 inline-flex items-center gap-1.5 rounded-full bg-[#e4f2e8] px-2.5 py-1 text-[11px] font-bold text-[#277145]"
            >
              <ShieldCheck className="h-3 w-3" />
              {roleLabels[user?.role ?? ''] ?? user?.role ?? '—'}
            </span>
          </div>
        </div>

        <dl className="mt-6 grid gap-3 sm:grid-cols-2">
          <div className="rounded-xl bg-[hsl(var(--muted))] p-4">
            <dt className="font-mono text-[9px] uppercase tracking-wider text-[hsl(var(--muted-foreground))]">
              <Mail className="mr-1 inline h-3 w-3" /> Email
            </dt>
            <dd data-testid="profile-email" className="mt-1 break-all text-sm font-bold">
              {user?.email ?? '—'}
            </dd>
          </div>
          <div className="rounded-xl bg-[hsl(var(--muted))] p-4">
            <dt className="font-mono text-[9px] uppercase tracking-wider text-[hsl(var(--muted-foreground))]">
              <Phone className="mr-1 inline h-3 w-3" /> Telefone
            </dt>
            <dd data-testid="profile-phone" className="mt-1 text-sm font-bold">
              {user?.phone ?? '—'}
            </dd>
          </div>
          <div className="rounded-xl bg-[hsl(var(--muted))] p-4">
            <dt className="font-mono text-[9px] uppercase tracking-wider text-[hsl(var(--muted-foreground))]">
              <UserRound className="mr-1 inline h-3 w-3" /> Último acesso
            </dt>
            <dd data-testid="profile-lastlogin" className="mt-1 text-sm font-bold">
              {dateTime(user?.lastLogin)}
            </dd>
          </div>
          <div className="rounded-xl bg-[hsl(var(--muted))] p-4">
            <dt className="font-mono text-[9px] uppercase tracking-wider text-[hsl(var(--muted-foreground))]">
              <BadgeCheck className="mr-1 inline h-3 w-3" /> Conta criada
            </dt>
            <dd data-testid="profile-created" className="mt-1 text-sm font-bold">
              {dateTime(user?.createdAt)}
            </dd>
          </div>
        </dl>

        <div className="mt-6 flex flex-wrap gap-3">
          <button
            data-testid="button-logout-profile"
            onClick={handleLogout}
            className="inline-flex items-center gap-2 rounded-xl bg-[hsl(var(--primary))] px-5 py-3 text-sm font-bold text-[hsl(var(--primary-foreground))] transition-transform hover:-translate-y-0.5"
          >
            <LogOut className="h-4 w-4" /> Terminar sessão
          </button>
          <Link
            href="/"
            className="inline-flex items-center gap-2 rounded-xl border border-[hsl(var(--border))] px-5 py-3 text-sm font-bold transition-colors hover:border-[hsl(var(--primary))]"
          >
            Voltar ao início
          </Link>
        </div>
        {me.isError && (
          <p
            data-testid="status-profile-error"
            className="mt-4 rounded-xl bg-[#f9dfda] p-3 text-sm font-bold text-[#a13d34]"
          >
            Não foi possível carregar o perfil — tente de novo.
          </p>
        )}
      </div>
    </div>
  );
}

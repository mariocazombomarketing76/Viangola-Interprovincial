import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useSyncExternalStore,
  type ReactNode,
} from 'react';
import { useQueryClient } from '@tanstack/react-query';
import {
  setAuthTokenGetter,
  useLogout,
  type TokenOutput,
  type UserOutput,
} from '@workspace/api-client-react';

export type Session = TokenOutput;

const STORAGE_KEY = 'viangola.session.v1';
// Renova o access token quando faltam menos de 15s para expirar.
const REFRESH_MARGIN_MS = 15_000;

// --------------------------------------------------------------------------
// Armazenamento da sessão (localStorage + subscriptions)
// --------------------------------------------------------------------------

function loadSession(): Session | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as Session;
    return parsed && parsed.accessToken && parsed.refreshToken && parsed.user ? parsed : null;
  } catch {
    return null;
  }
}

let session: Session | null = loadSession();
const listeners = new Set<() => void>();

function persist() {
  try {
    if (session) localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
    else localStorage.removeItem(STORAGE_KEY);
  } catch {
    // Storage indisponível (modo privado) — a sessão vive só em memória.
  }
}

export function getSession(): Session | null {
  return session;
}

export function setSession(next: Session | null): void {
  session = next;
  persist();
  listeners.forEach((listener) => listener());
}

function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

// --------------------------------------------------------------------------
// Refresh proativo do access token
// --------------------------------------------------------------------------

function tokenExpiresAt(token: string): number {
  try {
    const payload = JSON.parse(
      atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')),
    ) as { exp?: number };
    return typeof payload.exp === 'number' ? payload.exp * 1000 : 0;
  } catch {
    return 0;
  }
}

let refreshInFlight: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const current = session;
  if (!current) return null;
  const response = await fetch('/api/auth/refresh', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ refreshToken: current.refreshToken }),
  });
  if (!response.ok) throw new Error('Refresh token inválido ou expirado');
  const next = (await response.json()) as Session;
  setSession(next);
  return next.accessToken;
}

export async function getFreshAccessToken(): Promise<string | null> {
  if (!session) return null;
  if (tokenExpiresAt(session.accessToken) - Date.now() > REFRESH_MARGIN_MS) {
    return session.accessToken;
  }
  if (!refreshInFlight) {
    refreshInFlight = refreshAccessToken()
      .catch(() => {
        // Sessão irrecuperável — limpa e deixa o utilizador voltar ao login.
        setSession(null);
        return null;
      })
      .finally(() => {
        refreshInFlight = null;
      });
  }
  return refreshInFlight;
}

// Todos os pedidos do client gerado saem com `Authorization: Bearer`.
setAuthTokenGetter(getFreshAccessToken);

// --------------------------------------------------------------------------
// Contexto React
// --------------------------------------------------------------------------

type AuthContextValue = {
  session: Session | null;
  user: UserOutput | null;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const current = useSyncExternalStore(subscribe, getSession, getSession);
  const logoutMutation = useLogout();
  const seenUserId = useRef<number | null>(null);
  const firstRun = useRef(true);

  // Ao mudar de identidade (login/logout), descarta caches de queries —
  // dados privados de uma conta nunca ficam visíveis a outra.
  useEffect(() => {
    const id = current?.user.id ?? null;
    if (firstRun.current) {
      firstRun.current = false;
      seenUserId.current = id;
      return;
    }
    if (seenUserId.current !== id) {
      queryClient.clear();
      seenUserId.current = id;
    }
  }, [current, queryClient]);

  const logout = useCallback(() => {
    const active = getSession();
    // Limpa a sessão local de imediato; o revogar do refresh token é
    // fire-and-forget (mesmo que o pedido falhe, o utilizador sai na mesma).
    setSession(null);
    if (active) {
      logoutMutation.mutate({ data: { refreshToken: active.refreshToken } });
    }
  }, [logoutMutation]);

  return (
    <AuthContext.Provider value={{ session: current, user: current?.user ?? null, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth deve ser usado dentro de <AuthProvider>');
  return context;
}

/** Destino por omissão após autenticação, conforme o papel. */
export function landingPathFor(role: string): string {
  if (role === 'admin') return '/dashboard';
  if (role === 'driver') return '/bookings';
  return '/';
}

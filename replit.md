# Viangola Interprovincial

Plataforma para pesquisar viagens interprovinciais em Angola, reservar lugares e operar pagamentos.

## Run & Operate

- `pnpm install` — instala todo o workspace JS (frontend, libs, scripts do backend)
- `cd api-server && uv sync` — cria o ambiente Python do backend
- `pnpm dev` — API (porta 8000) + frontend (porta 5173) em paralelo
- `pnpm --filter @workspace/api-server run db:migrate` — aplica migrations Alembic
- `pnpm --filter @workspace/api-server run db:seed` — dados de demonstração (3 contas de teste)
- `pnpm --filter @workspace/api-server run test` — testes pytest (auth/sessões/permissões)
- `pnpm run typecheck` — typecheck de libs + frontend
- `pnpm run build` — typecheck + build de produção
- `pnpm run codegen` — regenera hooks React e schemas Zod do OpenAPI
- Env: `DATABASE_URL` (opcional em dev — SQLite por omissão; obrigatório em produção)
- Env: `JWT_SECRET` (obrigatório em produção — segredo HMAC dos tokens)

## Stack

- pnpm workspaces, Node.js 24, TypeScript 5.9
- Frontend: React 19, Vite 7, Tailwind 4, shadcn/ui, TanStack Query, wouter
- Backend: **FastAPI** (Python 3.13, gerido com uv), SQLAlchemy 2, Alembic, psycopg3
- API codegen: Orval (OpenAPI → hooks React + schemas Zod)

## Where things live

- `viangola/` — interface web responsiva para passageiros e operações.
- `api-server/app/main.py` — endpoints da API e proteção por papel.
- `api-server/app/auth.py` — JWT (access 30min + refresh rotativo 14d), bcrypt, roles.
- `api-server/tests/` — 19 testes pytest de auth, sessões e permissões.
- `api-server/app/models.py` — modelos SQLAlchemy (fonte do schema).
- `viangola/src/lib/auth.tsx` — sessão no frontend (localStorage + refresh proativo).
- `lib/api-spec/openapi.yaml` — contrato de API e fonte da geração de clientes.
- `lib/api-client-react/` — hooks React gerados a partir do contrato.

## Architecture decisions

- A mesma interface cobre pesquisa/reserva para passageiros e acompanhamento operacional para administradores.
- O contrato OpenAPI é a fonte única para alinhar tipos entre o servidor e a interface.
- **FastAPI é o único backend.** O scaffold Express/Drizzle foi removido na estabilização do repositório.
- **Autenticação JWT por papéis**: admin (dashboard/viagens/pagamentos), driver (reservas das suas viagens), passenger (reservar + as suas reservas). Reservas ficam sempre ligadas à conta autenticada.
- Em desenvolvimento local a API usa SQLite sem configuração; produção usa PostgreSQL via `DATABASE_URL`.

## Product

Passageiros podem pesquisar partidas por origem, destino e data, escolher um assento e criar uma reserva. Operadores podem acompanhar indicadores, viagens, reservas e confirmar pagamentos.

## User preferences

_Populate as you build — explicit user instructions worth remembering across sessions._

## Gotchas

- Correr `pnpm install` apenas na raiz (o `preinstall` bloqueia npm/yarn).
- `uv` é obrigatório para o backend — os scripts do api-server delegam tudo para `uv run`.
- O registo de admin **não** é auto-registável (role `admin` → 422); as contas admin vêm do seed.
- Credenciais de teste (dev): admin@viangola.ao/Admin123!, driver@viangola.ao/Driver123!, maria@viangola.ao/Passenger123!.
- `format: email` ficou fora do `openapi.yaml` de propósito: o Orval emitiria `z.email()` (zod v4) e o workspace usa zod v3 — a validação de email é do Pydantic.

## Pointers

- Ver `README.md` para instalação, base de dados, migrations, seed e execução.
- Ver `docs/postgresql-persistence-report.md` para o relatório de validação da persistência.

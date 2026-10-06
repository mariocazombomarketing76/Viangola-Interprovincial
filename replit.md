# Viangola Interprovincial

Plataforma para pesquisar viagens interprovinciais em Angola, reservar lugares e operar pagamentos.

## Run & Operate

- `pnpm --filter @workspace/api-server run dev` — run the API server (port 5000)
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from the OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- Required env: `DATABASE_URL` — Postgres connection string

## Stack

- pnpm workspaces, Node.js 24, TypeScript 5.9
- API: Express 5
- DB: PostgreSQL + Drizzle ORM
- Validation: Zod (`zod/v4`), `drizzle-zod`
- API codegen: Orval (from OpenAPI spec)
- Build: esbuild (CJS bundle)

## Where things live

- `artifacts/viangola` — interface web responsiva para passageiros e operações.
- `artifacts/api-server/src/routes/viangola.ts` — endpoints e dados iniciais do MVP.
- `lib/api-spec/openapi.yaml` — contrato de API e fonte de geração dos hooks.
- `lib/api-client-react` — hooks React gerados a partir do contrato.

## Architecture decisions

- A mesma interface cobre pesquisa/reserva para passageiros e acompanhamento operacional para administradores.
- O contrato OpenAPI é a fonte única para alinhar tipos entre o servidor e a interface.
- O MVP usa dados de demonstração em memória para validar os fluxos; a persistência PostgreSQL é o próximo passo de produção.

## Product

Passageiros podem pesquisar partidas por origem, destino e data, escolher um assento e criar uma reserva. Operadores podem acompanhar indicadores, viagens, reservas e confirmar pagamentos.

## User preferences

_Populate as you build — explicit user instructions worth remembering across sessions._

## Gotchas

_Populate as you build — sharp edges, "always run X before Y" rules._

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details

# Viangola Interprovincial

Plataforma para pesquisar viagens interprovinciais em Angola, reservar lugares e
operar pagamentos. Equivalentes ao que o Uber Interprovincial faz a nível de
produto: passageiros, motoristas, viagens, reservas, lugares e pagamentos — com
painel administrativo partilhado pela mesma interface.

> **Estado atual:** Sprint 2 concluída — autenticação JWT completa (registo,
> login, refresh com rotação, logout, perfis) com roles `admin`/`driver`/
> `passenger` e rotas protegidas no frontend e na API. Backend FastAPI +
> PostgreSQL, frontend React + Vite.

---

## Arquitetura

```
viangola-interprovincial/
├── api-server/            # BACKEND (único) — FastAPI + SQLAlchemy + Alembic
│   ├── app/
│   │   ├── main.py        # 16 endpoints (/api/*) com proteção por papel
│   │   ├── auth.py        # JWT, bcrypt, roles, refresh tokens
│   │   ├── models.py      # Modelos SQLAlchemy (8 tabelas)
│   │   ├── schemas.py     # Schemas Pydantic (validação/resposta)
│   │   ├── db.py          # Engine, session e resolução de DATABASE_URL
│   │   └── seed.py        # Contas de demonstração + dados iniciais
│   ├── tests/             # Testes pytest (auth, sessões, permissões)
│   ├── alembic/           # Migrations (001_initial, 002_auth)
│   ├── alembic.ini
│   ├── pyproject.toml     # Projeto Python (uv)
│   └── uv.lock
├── viangola/              # FRONTEND — React 19 + Vite + Tailwind 4 + shadcn/ui
│   ├── src/
│   │   ├── App.tsx        # Rotas protegidas + shell (passageiro + operações)
│   │   ├── main.tsx       # Entry point
│   │   ├── index.css      # Tema Viangola (tokens de design)
│   │   ├── pages/         # login, register, profile, 404
│   │   ├── components/    # Componentes UI (shadcn)
│   │   ├── hooks/         # Hooks (use-toast)
│   │   └── lib/           # Utilitários (cn) + auth (sessão JWT)
│   ├── vite.config.ts     # Alias @, proxy /api → backend
│   └── tsconfig.json
├── lib/                   # Código gerado/contrato da API
│   ├── api-spec/          # openapi.yaml + config do Orval (fonte do contrato)
│   ├── api-client-react/  # Hooks React gerados do OpenAPI (Orval)
│   └── api-zod/           # Schemas Zod gerados do OpenAPI (Orval)
├── docs/                  # Relatórios de validação
├── pnpm-workspace.yaml    # Workspace pnpm (packages + catalog + segurança)
└── package.json           # Scripts de topo (dev / build / typecheck / codegen)
```

### Fluxo de dados

```
Navegador ──► Vite (dev: porta 5173)
                 │  proxy /api
                 ▼
           FastAPI (uvicorn, porta 8000)
                 │
                 ▼
        PostgreSQL (produção)  /  SQLite (dev local, por omissão)
```

O frontend nunca fala com a base de dados: consome sempre `/api/*` através dos
hooks gerados a partir de `lib/api-spec/openapi.yaml`.

---

## Pré-requisitos

| Ferramenta | Versão | Observação |
|---|---|---|
| Node.js | 24+ | [nodejs.org](https://nodejs.org) |
| pnpm | 12.x | gerido via `packageManager` (corepack) |
| uv | latest | [astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/) |
| Python | 3.13+ | o `uv` descarrega automaticamente se não existir |
| PostgreSQL | 14+ | só necessário para produção (em dev usa SQLite) |

---

## Instalação (clone limpo)

```bash
git clone <repo-url>
cd Viangola-Interprovincial

# 1. Dependências JavaScript (instala tudo: raiz, viangola, api-server, lib/*)
pnpm install

# 2. Dependências Python (cria api-server/.venv a partir do uv.lock)
cd api-server && uv sync && cd ..
```

---

## Execução local

```bash
# Sobe TUDO em paralelo: FastAPI (8000) + Vite (5173)
pnpm dev
```

- Interface: <http://localhost:5173>
- API: <http://localhost:8000/api/healthz>
- Em dev, o Vite encaminha `/api/*` para `http://127.0.0.1:8000`
  (alterável com `API_PROXY_TARGET`).

Só um dos lados:

```bash
pnpm --filter @workspace/api-server run dev   # só a API
pnpm --filter ./viangola run dev              # só o frontend
```

### Variáveis de ambiente

| Variável | Obrigatória? | Padrão | Descrição |
|---|---|---|---|
| `DATABASE_URL` | Não (dev) | `sqlite:///./viangola.db` | Ligação à base de dados. Em produção **defina** o PostgreSQL: `postgresql://user:pass@host:5432/viangola` |
| `JWT_SECRET` | **Sim (produção)** | valor de dev (`viangola-local-…`) | Segredo HMAC dos tokens JWT. Em produção **tem de ser definido** (≥32 bytes); sem ele, os tokens usam um segredo de dev que muda com o código. |
| `PORT` | Não | API `8000` / Vite `5173` | Porta de cada serviço |
| `BASE_PATH` | Não | `/` | Base path do build do frontend |
| `API_PROXY_TARGET` | Não | `http://127.0.0.1:8000` | Destino do proxy `/api` em dev |

---

## Base de dados

### Desenvolvimento (SQLite — zero configuração)

`pnpm dev` cria automaticamente `api-server/viangola.db` se `DATABASE_URL` não
estiver definido. Ficheiros `.db` estão no `.gitignore`.

### Produção (PostgreSQL)

```bash
export DATABASE_URL="postgresql://user:pass@host:5432/viangola"
```

O código converte automaticamente para `postgresql+psycopg://` (driver `psycopg3`,
já incluído nas dependências).

### Migrations (Alembic)

```bash
pnpm --filter @workspace/api-server run db:migrate        # aplica todas (upgrade head)
pnpm --filter @workspace/api-server run db:revision -- -m "descrição"   # nova migration
```

A migration inicial é `001_initial` e cria as tabelas: `users`, `drivers`,
`vehicles`, `trips`, `trip_seats`, `bookings`, `payments`. A `002_auth` adiciona
`is_active`, `last_login` em `users` e a tabela `refresh_tokens` (sessões
revogáveis).

### Seed (dados de demonstração)

```bash
pnpm --filter @workspace/api-server run db:seed
```

Cria as 3 contas de demonstração (com passwords bcrypt), motorista, viatura,
4 viagens (Luanda→Benguela, etc.), lugares e uma reserva já paga. O seed é
idempotente — pode correr mais do que uma vez (re-sincroniza passwords).

**Credenciais de teste:**

| Papel | Email | Password |
|---|---|---|
| Admin | `admin@viangola.ao` | `Admin123!` |
| Motorista | `driver@viangola.ao` | `Driver123!` |
| Passageiro | `maria@viangola.ao` | `Passenger123!` |

> Estas contas existem apenas para demonstração/dev — nunca as use em produção.

---

## Scripts disponíveis

| Comando | O que faz |
|---|---|
| `pnpm dev` | API + frontend em paralelo (dev) |
| `pnpm build` | Typecheck completo + build de produção do frontend |
| `pnpm typecheck` | Typecheck das libs + do frontend |
| `pnpm codegen` | Regenera hooks React e schemas Zod a partir do `openapi.yaml` |
| `pnpm --filter @workspace/api-server run test` | Testes pytest (auth, sessões, permissões) |
| `pnpm --filter @workspace/api-server run db:migrate` | Aplica migrations |
| `pnpm --filter @workspace/api-server run db:seed` | Popula dados de demonstração |

---

## Contrato da API

`lib/api-spec/openapi.yaml` é a **fonte única** do contrato:

```bash
pnpm codegen   # regenera lib/api-client-react e lib/api-zod
```

Endpoints implementados (FastAPI):

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| GET | `/api/healthz` | público | Health check |
| POST | `/api/auth/register` | público | Registo (passageiro/motorista) → tokens |
| POST | `/api/auth/login` | público | Login → access + refresh token |
| POST | `/api/auth/refresh` | público | Rotação de sessão (o refresh antigo é revogado) |
| POST | `/api/auth/logout` | público | Revoga o refresh token apresentado |
| GET | `/api/auth/me` | autenticado | Perfil do utilizador |
| GET | `/api/dashboard` | admin | KPIs, receita semanal e reservas recentes |
| GET | `/api/trips` | público | Lista/filtra viagens (origem, destino, data, estado) |
| POST | `/api/trips` | admin | Cria viagem |
| GET | `/api/trips/{id}` | público | Detalhe de viagem |
| GET | `/api/trips/{id}/seats` | público | Mapa de lugares |
| GET | `/api/bookings` | autenticado | Lista reservas (âmbito por papel, ver abaixo) |
| POST | `/api/bookings` | passageiro | Cria reserva (com bloqueio de lugar) |
| GET | `/api/payments` | admin | Lista pagamentos |
| POST | `/api/payments/{id}/confirm` | admin | Confirma pagamento |

---

## Autenticação e autorização

### Tokens

- **Access token** — JWT HS256, 30 min, claims `sub`, `role`, `type=access`.
  Enviado como `Authorization: Bearer <token>`.
- **Refresh token** — JWT com `jti` persistido em `refresh_tokens`, 14 dias,
  **rotativo**: cada `/auth/refresh` revoga o anterior (reuso é rejeitado com
  401). `/auth/logout` revoga a sessão.
- **Passwords** — apenas bcrypt (`$2b$…`); nunca em texto.
- O frontend guarda a sessão em `localStorage` e renova o access token
  automaticamente ~15 s antes de expirar (`viangola/src/lib/auth.tsx`).

### Papéis e âmbito

| Papel | Pode |
|---|---|
| `admin` | Criar viagens, ver dashboard, ver **todas** as reservas, ver/confirmar pagamentos |
| `driver` | Ver **apenas reservas das suas viagens** |
| `passenger` | Reservar lugares, ver **apenas as suas reservas** |
| (anónimo) | Pesquisar viagens e ver o mapa de lugares |

Reservas ficam sempre associadas à conta autenticada (o campo `passengerName`
do pedido é ignorado pelo servidor). No frontend, `/dashboard`, `/trips` e
`/payments` exigem admin; `/bookings` e `/profile` exigem login; utilizadores
sem sessão são redirecionados para `/login?next=…`.

---

## Testes

```bash
pnpm --filter @workspace/api-server run test   # ou: cd api-server && uv run pytest
```

19 testes cobrem: registo (duplicados, password fraca, admin não auto-
registável, hash bcrypt), login, `/auth/me`, rotação e revogação de refresh
tokens, logout, matriz de permissões (401/403 por papel) e âmbito de reservas
(passageiro/motorista/admin). Usam uma base SQLite dedicada (`tests/`), isolada
da base de dev.

---

## Qualidade e segurança do repositório

- `.gitignore` cobre `node_modules`, `dist`, `*.tsbuildinfo`, `.venv`,
  `__pycache__`, ficheiros `.db` e `.env`.
- Nenhum segredo no repositório — tudo via variáveis de ambiente (`JWT_SECRET`,
  `DATABASE_URL`).
- `pnpm-workspace.yaml` ativa `minimumReleaseAge: 1440` (defesa contra
  ataques supply-chain na cadeia npm).
- Rotas protegidas por JWT + roles; passwords só em hash bcrypt; CORS ainda
  em modo aberto (`*`) — restringir origens em produção.

---

## Roadmap (fases seguintes, ainda por implementar)

1. Perfis de motorista: upload de BI, carta e selfie + aprovação pelo admin
2. Integração de pagamentos (Multicaixa Express)
3. GPS/telemetria de viagens
4. App Flutter para passageiros/motoristas

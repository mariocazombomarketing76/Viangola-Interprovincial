# Relatório de validação da persistência PostgreSQL

**Data da validação:** 11 de setembro de 2026  
**Escopo:** estabilização da camada de persistência, sem alterações visuais

## Resultado geral

| Área | Resultado |
|---|---|
| PostgreSQL disponível | Aprovado |
| Alembic | `001_initial` aplicado e no estado `head` |
| SQLAlchemy | Aprovado em leitura, criação e atualização transacional |
| Persistência após reinício | Aprovado |
| Integridade referencial | Aprovado |
| Dados mockados em runtime | Não encontrados |
| Interface visual | Não alterada |

## Tabelas existentes

| Tabela | Registos observados |
|---|---:|
| `users` | 6 |
| `drivers` | 1 |
| `vehicles` | 1 |
| `trips` | 5 |
| `trip_seats` | 104 |
| `bookings` | 4 |
| `payments` | 4 |

## Relacionamentos

- `drivers.user_id` → `users.id`
- `drivers.approved_by` → `users.id`
- `vehicles.driver_id` → `drivers.id`
- `trips.driver_id` → `drivers.id`
- `trips.vehicle_id` → `vehicles.id`
- `trip_seats.trip_id` → `trips.id`
- `trip_seats.passenger_id` → `users.id`
- `bookings.trip_id` → `trips.id`
- `bookings.passenger_id` → `users.id`
- `payments.booking_id` → `bookings.id`

Todas as verificações de registos órfãos devolveram zero. Uma tentativa controlada de inserir um pagamento com `booking_id` inexistente foi rejeitada pela foreign key.

## Endpoints validados

- `GET /api/healthz`
- `GET /api/dashboard`
- `GET /api/trips`
- `POST /api/trips`
- `GET /api/trips/{trip_id}`
- `GET /api/trips/{trip_id}/seats`
- `GET /api/bookings`
- `GET /api/bookings?status=paid`
- `POST /api/bookings`
- `GET /api/payments`
- `POST /api/payments/{payment_id}/confirm`

Também foi validado o conflito de reserva do mesmo assento, que devolve `409`, e a confirmação atualiza simultaneamente `payments`, `bookings` e `trip_seats`.

## Persistência após reinício

Foi criada uma viagem de validação, uma reserva e um pagamento. Após reiniciar o workflow da API:

- a viagem continuou disponível;
- a reserva continuou disponível;
- o pagamento confirmado continuou confirmado;
- as quantidades devolvidas pela API continuaram a ser lidas do PostgreSQL.

## Limitação registada

Esta fase valida os endpoints existentes. A API atual ainda não expõe CRUD HTTP para `users`, `drivers` e `vehicles`, nem endpoints de atualização/remoção para todas as entidades. Os modelos, tabelas e relações existem no PostgreSQL, mas a criação desses endpoints deve ser uma fase própria para não introduzir funcionalidades fora do escopo de estabilização.
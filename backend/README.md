# Backend

Python backend scaffold for microservice-oriented components.

## Principles

- Keep business logic out until feature phases begin
- Organize code by clear service boundaries
- Separate domain, transport, and infrastructure concerns

## Planned Areas

- `app/api/` transport-layer endpoints when APIs are introduced
- `app/core/` shared configuration and application wiring
- `app/domain/` domain models and rules
- `app/events/` event contracts and handlers
- `app/schemas/` request and response schemas
- `app/services/` orchestration services
- `tests/` automated tests

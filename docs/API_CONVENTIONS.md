
- Query parameters should be snake_case.

- ISO 8601 UTC format must be used for all timestamp fields.

- Custom headers should use the 'X-AB-' prefix.

- Rate limits return 429 Too Many Requests with Retry-After header.

- Healthcheck endpoints (/health, /live, /ready) must return 200 OK within 200ms.
- Idempotency: All POST mutation endpoints support Idempotency-Key headers.

- **Standard Pagination**: List endpoints support `page` (default 1) and `limit` (default 20, max 100) query parameters.

# API Documentation Style

**Inherits:** [documentation-style-guide.md](./documentation-style-guide.md)  
**Version:** 1.0.0

---

## Scope

API.md, OpenAPI companion prose, endpoint reference in docs/.

---

## API.md Structure

1. **Overview** — base URL, auth scheme, content types
2. **Authentication** — how to obtain and send credentials (from `architecture.md`)
3. **Conventions** — pagination, errors, idempotency, versioning
4. **Endpoints** — grouped by resource
5. **Error catalog** — HTTP status + body shape
6. **Changelog pointer** — link to CHANGELOG.md API section

---

## Endpoint Entry Format

```markdown
### `POST /api/v1/resources`

Create a resource.

**Auth:** Bearer token required

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | yes | Display name |

**Response `201`:** Resource object

**Errors:** `400` validation, `401` unauthorized, `409` conflict

**Source:** `routes/resources.py`, project `architecture.md` § API
```

Every endpoint in API.md must appear in project `architecture.md` or implementation. Undocumented implemented endpoints are **gaps** to list in `documentation-report.md`.

---

## Request/Response Examples

Use JSON with realistic but fake data:

```json
{
  "name": "example-resource",
  "id": "res_123"
}
```

Match actual field names from code (Pydantic models, TypeScript types).

---

## Versioning

Document API version prefix (`/v1/`) matching implementation. If unversioned, state explicitly.

---

## MCP Usage

When documenting third-party library APIs (not project REST API), use capability `documentation-lookup` and cite library IDs in `documentation-report.md` MCP Evidence section.

---

## References

- [documentation-templates.md](../../docs/documentation/documentation-templates.md) § API

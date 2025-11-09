## Shared DTOs

The FastAPI application exposes an OpenAPI schema that both the backend and frontend consume.  
Run the helper script after installing dependencies to generate/update the spec:

```bash
PYTHONPATH=. python3 scripts/export_openapi.py
```

The script writes `openapi.json` to this directory so the React demo (or any other client) can derive TypeScript types from a single source of truth.

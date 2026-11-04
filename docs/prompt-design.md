# Prompt and provider design

TenderLens keeps model access behind a provider interface. The default
`LLM_PROVIDER=mock` implementation is deterministic and free, so local
development and automated tests do not require an API key or network access.

Provider safeguards:

- Structured output is validated with Pydantic before application use.
- Source chunk IDs are supplied by the application and must remain in scope.
- Uploaded document text is treated as untrusted data.
- Unknown values remain `null` or `unknown`; the provider must not invent them.
- Model suggestions remain separate from reviewer-confirmed decisions.

A future Ollama adapter can implement the same interface without changing API,
persistence or frontend code.

# Dev server for brand-logo-detector
$env:LLM_MODE = "mock"
uvicorn backend.main:app --reload --port 8000

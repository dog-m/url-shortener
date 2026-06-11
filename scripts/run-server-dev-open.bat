@cd ..

rem @start uv run fastapi dev --host 0.0.0.0

@start uv run uvicorn backend.main:app --reload --host 0.0.0.0 --lifespan=on

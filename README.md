# URL Shortener

A personal project developed as a learning ground for building modern, asynchronous Python web applications.

This project is currently under active development and serves as an exploration of typical web app patterns, including authentication, rate limiting, and analytics.

## Features

- Convert long URLs into manageable, short links.
- User accounts (regular + admin) and session management.
- Track click events and usage statistics.
- Rate Limiting.

## Tech Stack

- FastAPI (async)
- SQLAlchemy (async) with SQLite/PostgreSQL
- FastAPI-Cache/Redis
- Jinja2 templates, HTML, JS, CSS
- Pydantic models
- uv

## Getting Started

### Prerequisites

- Python 3.12+
- uv

### Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd url-shortener
   ```

1. Install dependencies using `uv`:

   ```bash
   uv sync
   ```

1. Set up environment variables:

   ```bash
   cp .env-example .env
   ```

   *Edit `.env` to configure your specific database and secret keys.*

### Running the Application

To start the development server:

```bash
uv run fastapi dev
```

## Development

This project uses strict typing and linting to maintain code quality.

- **Linting**: `uv run ruff check .`
<!--
- **Type Checking**: `uv run mypy .`
-->

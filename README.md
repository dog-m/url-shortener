# URL Shortener

A personal project developed as a learning ground for building modern, asynchronous Python web applications.

This project is currently under active development and serves as an exploration of typical web app patterns, including authentication, rate limiting, and analytics.

## Features

- **URL Shortening**: Convert long URLs into manageable, short links.
- **User Authentication**: Secure user accounts and session management.
- **Analytics**: Track click events and usage statistics.
- **Rate Limiting**: Protect API endpoints from abuse.
- **Admin Interface**: Basic controls for managing the system.

## Tech Stack

- **Backend**: FastAPI (async)
- **Database**: SQLAlchemy (async) with SQLite/PostgreSQL
- **Caching**: FastAPI-Cache/Redis
- **Frontend**: Jinja2 templates, HTML, JS, CSS
- **Validation**: Pydantic
- **Package Management**: uv

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

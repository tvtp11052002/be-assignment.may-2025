# 🧪 Backend Developer Exercise — Messaging System API

## 🎯 Objective

Implement a backend messaging system API with the following goals:

- Build APIs based on the provided data model.
- Use **FastAPI** for API development.
- Use **PostgreSQL** for data management.
- Use **Justfile** for all run and development commands.
- (Optional – Advanced) Use **Docker** to containerize the application.
- (Optional – Advanced) Convert the API to an **MCP server** and connect to **Claude Desktop** for testing.

## 📦 Tech Requirements

- Python 3.11+
- FastAPI
- PostgreSQL
- SQLAlchemy or Tortoise ORM
- Docker & Docker Compose
- Justfile
- GitHub Actions for CI/CD
- (Optional) MCP integration for AI agent testing

## 🧩 Data Model

The following tables must be implemented:

### `users`
- `id`: UUID (primary key)
- `email`: String (unique)
- `name`: String
- `created_at`: DateTime

### `messages`
- `id`: UUID (primary key)
- `sender_id`: UUID (foreign key to users)
- `subject`: String (optional)
- `content`: Text
- `timestamp`: DateTime

### `message_recipients`
- `id`: UUID (primary key)
- `message_id`: UUID (foreign key to messages)
- `recipient_id`: UUID (foreign key to users)
- `read`: Boolean
- `read_at`: DateTime (nullable)

## 📌 API Requirements

The system must support the following API functionality:

### User APIs
- Create a user
- Retrieve user info
- List users

### Message APIs
- Send a message to one or more recipients
- View sent messages
- View inbox messages
- View unread messages
- View a message with all recipients
- Mark a message as read

## ⚙️ Command Line Automation (Justfile)

All scripts for development and testing must be included in a `Justfile`. The following commands are required:

- `just install`
- `just dev`
- `just up`
- `just down`
- `just migrate`
- `just test`
- `just mcp` (optional)
- `just format` (optional)

## 🚀 Project Requirements

- Source code must be hosted in a **public GitHub repository**.
- The application must be runnable via `docker-compose`.
- Automated tests must be defined and executed via `just test`.
- Tests must run successfully via **GitHub Actions**.
- A `README.md` must describe:
  - Setup instructions
  - Justfile command list
  - How to use and test the APIs
  - (Optional) MCP instructions for Claude Desktop

## 🌟 Advanced (Optional)

- Convert the application to an MCP-compatible server.
- Define a set of MCP tool functions that can interact with the messaging system.
- Provide a `.mcp.json` manifest for Claude Desktop to consume.
- Demonstrate successful interaction between Claude and your MCP server.

## ✅ Review Criteria

| Criteria                 | Required | Bonus |
|--------------------------|----------|-------|
| API functionality        | ✅       |       |
| PostgreSQL integration   | ✅       |       |
| Command automation       | ✅       |       |
| Test coverage            | ✅       |       |
| CI/CD via GitHub Actions | ✅       |       |
| Docker containerization  |          | ⭐     |
| MCP server integration   |          | ⭐     |
| Claude Desktop testing   |          | ⭐     |

# Justfile for Messaging API Backend Assignment

# Install Python dependencies
install:
	pip install -r requirements.txt

# Run the FastAPI app
dev:
	uvicorn app.main:app --reload

# Start services using Docker Compose
up:
	docker-compose up -d

# Stop services
down:
	docker-compose down

# Run database migrations (if using Alembic)
migrate:
	python app/main.py

# Run tests
test:
	pytest --disable-warnings -v

# Format code using black and isort
format:
	black .
	isort .

# Run the MCP server (optional)
mcp:
	uvicorn app.mcp_server:app --reload

# Check list 
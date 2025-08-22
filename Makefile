.PHONY: help setup migrate migrations reset run test shell seed lint

# Default Python version
PYTHON := python3
VENV := venv
VENV_BIN := $(VENV)/bin
PYTHON_VENV := $(VENV_BIN)/python
PIP := $(VENV_BIN)/pip

# File markers for dependency tracking
VENV_MARKER := $(VENV)/pyvenv.cfg
DEPS_MARKER := $(VENV)/.deps_installed
DB_MARKER := backend/db.sqlite3

help:
	@echo "E-Commerce Platform"
	@echo "==================="
	@echo ""
	@echo "Available commands:"
	@echo "  make setup       - Initial setup (venv, install dependencies)"
	@echo "  make reset       - Reset database (delete, migrate, seed)"
	@echo "  make run         - Start the development server"
	@echo "  make seed        - Add sample data to existing database"
	@echo "  make migrations  - Create new migrations"
	@echo "  make migrate     - Apply migrations"
	@echo "  make test        - Run tests"
	@echo "  make shell       - Open Django shell"
	@echo "  make lint        - Check code style (black, flake8, isort)"
	@echo ""
	@echo "Quick start: just run 'make run' (auto-setup included!)"

# Create virtual environment
$(VENV_MARKER):
	@echo "Creating virtual environment..."
	@$(PYTHON) -m venv $(VENV)
	@touch $(VENV_MARKER)

# Install dependencies
$(DEPS_MARKER): $(VENV_MARKER) requirements.txt
	@echo "Installing dependencies..."
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt
	@touch $(DEPS_MARKER)
	@echo "✅ Dependencies installed!"

# Setup is just an alias for installing dependencies
setup: $(DEPS_MARKER)
	@echo "✅ Setup complete!"

# Create database with migrations and seed data
$(DB_MARKER): $(DEPS_MARKER)
	@echo "Creating database..."
	@cd backend && ../$(PYTHON_VENV) manage.py makemigrations marketplace --noinput
	@cd backend && ../$(PYTHON_VENV) manage.py migrate --noinput
	@cd backend && ../$(PYTHON_VENV) manage.py seed_database
	@echo "✅ Database created and seeded!"

# Reset database (force recreation)
reset: $(DEPS_MARKER)
	@echo "Resetting database..."
	@rm -f backend/db.sqlite3
	@cd backend && ../$(PYTHON_VENV) manage.py makemigrations marketplace --noinput
	@cd backend && ../$(PYTHON_VENV) manage.py migrate --noinput
	@cd backend && ../$(PYTHON_VENV) manage.py seed_database
	@echo "✅ Database reset complete!"

# Run server (ensures setup and database exist)
run: $(DEPS_MARKER) $(DB_MARKER)
	@echo "Starting development server..."
	@echo "Server will be available at http://localhost:8000"
	@echo "Press Ctrl+C to stop."
	@cd backend && ../$(PYTHON_VENV) manage.py runserver

# Create new migrations (requires dependencies)
migrations: $(DEPS_MARKER)
	@echo "Creating migrations..."
	@cd backend && ../$(PYTHON_VENV) manage.py makemigrations

# Apply migrations (requires dependencies)
migrate: $(DEPS_MARKER)
	@echo "Applying migrations..."
	@cd backend && ../$(PYTHON_VENV) manage.py migrate

# Run tests (requires full setup)
test: $(DEPS_MARKER) $(DB_MARKER)
	@echo "Running tests..."
	@cd backend && ../$(PYTHON_VENV) manage.py test ../tests

# Open shell (requires dependencies)
shell: $(DEPS_MARKER)
	@echo "Opening Django shell..."
	@cd backend && ../$(PYTHON_VENV) manage.py shell

# Seed database (requires dependencies and migrations)
seed: $(DEPS_MARKER)
	@echo "Seeding database with sample data..."
	@cd backend && ../$(PYTHON_VENV) manage.py seed_database
	@echo "✅ Database seeded!"


# Lint command - check code style issues and report all problems
lint: $(DEPS_MARKER)
	@echo "╔══════════════════════════════════════════════════════════════╗"
	@echo "║                    CODE STYLE CHECK REPORT                    ║"
	@echo "╚══════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "1. Black (code formatter)"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@$(VENV_BIN)/black --check backend/ tests/ 2>&1 && echo "✅ PASSED: No formatting issues" || echo "❌ FAILED: Formatting issues found"
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "2. isort (import ordering)"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@$(VENV_BIN)/isort --check-only --diff backend/ tests/ 2>&1 && echo "✅ PASSED: Import order is correct" || echo "❌ FAILED: Import order issues found"
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "3. flake8 (style violations)"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@$(VENV_BIN)/flake8 backend/ tests/ && echo "✅ PASSED: No style violations" || echo "❌ FAILED: Style violations found"
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "                 SUMMARY                 "
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@BLACK_STATUS=0; ISORT_STATUS=0; FLAKE8_STATUS=0; \
	$(VENV_BIN)/black --check backend/ tests/ > /dev/null 2>&1 || BLACK_STATUS=1; \
	$(VENV_BIN)/isort --check-only backend/ tests/ > /dev/null 2>&1 || ISORT_STATUS=1; \
	$(VENV_BIN)/flake8 backend/ tests/ > /dev/null 2>&1 || FLAKE8_STATUS=1; \
	if [ $$BLACK_STATUS -eq 0 ] && [ $$ISORT_STATUS -eq 0 ] && [ $$FLAKE8_STATUS -eq 0 ]; then \
		echo "✅ All checks passed! Code is clean."; \
	else \
		echo "❌ Some checks failed. Fix issues with:"; \
		[ $$BLACK_STATUS -ne 0 ] && echo "   • venv/bin/black backend/ tests/"; \
		[ $$ISORT_STATUS -ne 0 ] && echo "   • venv/bin/isort backend/ tests/"; \
		[ $$FLAKE8_STATUS -ne 0 ] && echo "   • Review flake8 errors above"; \
		exit 1; \
	fi
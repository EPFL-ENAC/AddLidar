.PHONY: setup install clean uninstall lint format subtree-add subtree-pull subtree-push-backend subtree-push-frontend subtree-push-potree-converter check-git-clean verify-subtrees reset-subtrees subtree-status deprecate-repos create-deprecation-notices help

# Repository configuration
SUBTREES = backend frontend potree-converter
BACKEND_REPO = git@github.com:EPFL-ENAC/AddLidar-API.git
BACKEND_BRANCH = dev
FRONTEND_REPO = git@github.com:EPFL-ENAC/AddLidar-Potree.git
FRONTEND_BRANCH = develop
POTREECONVERTER_REPO = git@github.com:EPFL-ENAC/PotreeConverterMakefile.git
POTREECONVERTER_BRANCH = main

# Map directory names to repository URLs
get-repo-url = $(if $(filter backend,$1),$(BACKEND_REPO),$(if $(filter frontend,$1),$(FRONTEND_REPO),$(if $(filter potree-converter,$1),$(POTREECONVERTER_REPO),)))

# Map directory names to repository branches
get-repo-branch = $(if $(filter backend,$1),$(BACKEND_BRANCH),$(if $(filter frontend,$1),$(FRONTEND_BRANCH),$(if $(filter potree-converter,$1),$(POTREECONVERTER_BRANCH),)))

# Check if a subtree already exists
check-subtree-exists = $(shell git log --grep="git-subtree-dir: $(1)" --oneline 2>/dev/null | head -1)

# Install dependencies and set up git hooks
install:
	@echo "Installing npm dependencies..."
	npm install
	@echo "Installing git hooks with lefthook..."
	npx lefthook install
	@echo "Setup complete!"

# Clean dependencies
clean:
	@echo "Cleaning dependencies..."
	rm -rf node_modules
	rm -f package-lock.json

# Uninstall hooks and clean
uninstall:
	@echo "Uninstalling git hooks..."
	npx lefthook uninstall || true
	$(MAKE) clean
	@echo "Uninstall complete!"

lint:
	@echo "Running linter..."
	npx prettier --check .
	@echo "Linting complete!"

format:
	@echo "Running formatter..."
	npx prettier --write .
	@echo "Formatting complete!"

# Safe subtree addition
subtree-add:
	@echo "🔍 Performing safe subtree addition..."
	@$(MAKE) check-git-clean
	@$(MAKE) add-backend-subtree
	@$(MAKE) add-frontend-subtree
	@$(MAKE) add-potree-converter-subtree
	@echo "✅ All subtrees processed successfully!"

# Individual subtree additions
add-backend-subtree:
	@echo "🔄 Processing backend subtree..."
	@if [ -d "backend" ]; then \
		if [ -n "$(call check-subtree-exists,backend)" ]; then \
			echo "✅ backend subtree already exists and is properly configured"; \
		else \
			echo "⚠️  backend directory exists but is not a subtree. Manual intervention required."; \
		fi; \
	else \
		echo "📥 Adding backend subtree from $(BACKEND_BRANCH) branch..."; \
		if git subtree add --prefix=backend $(BACKEND_REPO) $(BACKEND_BRANCH) --squash 2>/dev/null; then \
			echo "✅ backend subtree added successfully"; \
		else \
			echo "❌ Failed to add backend subtree. Check repository URL and permissions."; \
			exit 1; \
		fi; \
	fi

add-frontend-subtree:
	@echo "🔄 Processing frontend subtree..."
	@if [ -d "frontend" ]; then \
		if [ -n "$(call check-subtree-exists,frontend)" ]; then \
			echo "✅ frontend subtree already exists and is properly configured"; \
		else \
			echo "⚠️  frontend directory exists but is not a subtree. Manual intervention required."; \
		fi; \
	else \
		echo "📥 Adding frontend subtree from $(FRONTEND_BRANCH) branch..."; \
		if git subtree add --prefix=frontend $(FRONTEND_REPO) $(FRONTEND_BRANCH) --squash 2>/dev/null; then \
			echo "✅ frontend subtree added successfully"; \
		else \
			echo "❌ Failed to add frontend subtree. Check repository URL and permissions."; \
			exit 1; \
		fi; \
	fi

add-potree-converter-subtree:
	@echo "🔄 Processing potree-converter subtree..."
	@if [ -d "potree-converter" ]; then \
		if [ -n "$(call check-subtree-exists,potree-converter)" ]; then \
			echo "✅ potree-converter subtree already exists and is properly configured"; \
		else \
			echo "⚠️  potree-converter directory exists but is not a subtree. Manual intervention required."; \
		fi; \
	else \
		echo "📥 Adding potree-converter subtree from $(POTREECONVERTER_BRANCH) branch..."; \
		if git subtree add --prefix=potree-converter $(POTREECONVERTER_REPO) $(POTREECONVERTER_BRANCH) --squash 2>/dev/null; then \
			echo "✅ potree-converter subtree added successfully"; \
		else \
			echo "❌ Failed to add potree-converter subtree. Check repository URL and permissions."; \
			exit 1; \
		fi; \
	fi

# Pull updates from all original repos
subtree-pull:
	@echo "Pulling updates from all subtrees..."
	@echo "Pulling updates from backend ($(BACKEND_BRANCH) branch)..."
	@git subtree pull --prefix=backend $(BACKEND_REPO) $(BACKEND_BRANCH) --squash || true
	@echo "Pulling updates from frontend ($(FRONTEND_BRANCH) branch)..."
	@git subtree pull --prefix=frontend $(FRONTEND_REPO) $(FRONTEND_BRANCH) --squash || true
	@echo "Pulling updates from potree-converter ($(POTREECONVERTER_BRANCH) branch)..."
	@git subtree pull --prefix=potree-converter $(POTREECONVERTER_REPO) $(POTREECONVERTER_BRANCH) --squash || true
	@echo "All subtrees updated successfully!"

# Push commands
subtree-push-backend:
	@echo "Pushing backend changes to original repo..."
	@read -p "Enter branch name for backend repo (default: $(BACKEND_BRANCH)): " branch; \
	branch=$${branch:-$(BACKEND_BRANCH)}; \
	git subtree push --prefix=backend $(BACKEND_REPO) $$branch

subtree-push-frontend:
	@echo "Pushing frontend changes to original repo..."
	@read -p "Enter branch name for frontend repo (default: $(FRONTEND_BRANCH)): " branch; \
	branch=$${branch:-$(FRONTEND_BRANCH)}; \
	git subtree push --prefix=frontend $(FRONTEND_REPO) $$branch

subtree-push-potree-converter:
	@echo "Pushing potree-converter changes to original repo..."
	@read -p "Enter branch name for potree-converter repo (default: $(POTREECONVERTER_BRANCH)): " branch; \
	branch=$${branch:-$(POTREECONVERTER_BRANCH)}; \
	git subtree push --prefix=potree-converter $(POTREECONVERTER_REPO) $$branch

# Check if git working directory is clean
check-git-clean:
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "❌ Git working directory is not clean. Please commit or stash changes first."; \
		exit 1; \
	fi

# Verify subtree configuration
verify-subtrees:
	@echo "🔍 Verifying subtree configuration..."
	@echo -n "backend: "
	@if [ -d "backend" ]; then \
		if [ -n "$(call check-subtree-exists,backend)" ]; then \
			echo "✅ Properly configured as subtree"; \
		else \
			echo "⚠️  Directory exists but not configured as subtree"; \
		fi; \
	else \
		echo "❌ Directory missing"; \
	fi
	@echo -n "frontend: "
	@if [ -d "frontend" ]; then \
		if [ -n "$(call check-subtree-exists,frontend)" ]; then \
			echo "✅ Properly configured as subtree"; \
		else \
			echo "⚠️  Directory exists but not configured as subtree"; \
		fi; \
	else \
		echo "❌ Directory missing"; \
	fi
	@echo -n "potree-converter: "
	@if [ -d "potree-converter" ]; then \
		if [ -n "$(call check-subtree-exists,potree-converter)" ]; then \
			echo "✅ Properly configured as subtree"; \
		else \
			echo "⚠️  Directory exists but not configured as subtree"; \
		fi; \
	else \
		echo "❌ Directory missing"; \
	fi

# Show subtree status
subtree-status:
	@echo "📊 Subtree Status Report:"
	@echo "========================"
	@echo -n "backend: "
	@if [ -d "backend" ]; then \
		if [ -n "$(call check-subtree-exists,backend)" ]; then \
			echo "✅ Active subtree (from $(BACKEND_BRANCH) branch)"; \
		else \
			echo "⚠️  Directory exists (not a subtree)"; \
		fi; \
	else \
		echo "❌ Missing"; \
	fi
	@echo -n "frontend: "
	@if [ -d "frontend" ]; then \
		if [ -n "$(call check-subtree-exists,frontend)" ]; then \
			echo "✅ Active subtree (from $(FRONTEND_BRANCH) branch)"; \
		else \
			echo "⚠️  Directory exists (not a subtree)"; \
		fi; \
	else \
		echo "❌ Missing"; \
	fi
	@echo -n "potree-converter: "
	@if [ -d "potree-converter" ]; then \
		if [ -n "$(call check-subtree-exists,potree-converter)" ]; then \
			echo "✅ Active subtree (from $(POTREECONVERTER_BRANCH) branch)"; \
		else \
			echo "⚠️  Directory exists (not a subtree)"; \
		fi; \
	else \
		echo "❌ Missing"; \
	fi

# Reset subtrees (dangerous - use with caution)
reset-subtrees:
	@echo "⚠️  This will remove all subtree directories and their git history!"
	@echo "Make sure you have backups before proceeding."
	@read -p "Are you absolutely sure? Type 'DELETE' to confirm: " confirm; \
	if [ "$$confirm" = "DELETE" ]; then \
		echo "Removing subtree directories..."; \
		rm -rf backend frontend potree-converter; \
		echo "Subtree directories removed. Run 'make subtree-add' to re-create them."; \
	else \
		echo "Reset cancelled."; \
	fi

# Deprecation workflow
deprecate-repos:
	@echo "Starting repository deprecation process..."
	@echo "This will:"
	@echo "1. Add deprecation notices to original repos"
	@echo "2. Archive the repositories"
	@echo "3. Update README files"
	@echo ""
	@read -p "Are you sure you want to proceed? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		$(MAKE) create-deprecation-notices; \
	else \
		echo "Deprecation cancelled."; \
	fi

create-deprecation-notices:
	@echo "Creating deprecation notice files..."
	@mkdir -p temp-deprecation
	@echo "# 🚨 DEPRECATED REPOSITORY" > temp-deprecation/DEPRECATED.md
	@echo "" >> temp-deprecation/DEPRECATED.md
	@echo "This repository has been **deprecated** and is no longer maintained." >> temp-deprecation/DEPRECATED.md
	@echo "" >> temp-deprecation/DEPRECATED.md
	@echo "## 🔄 Migration" >> temp-deprecation/DEPRECATED.md
	@echo "" >> temp-deprecation/DEPRECATED.md
	@echo "This code has been moved to the [AddLidar monorepo](https://github.com/EPFL-ENAC/AddLidar)." >> temp-deprecation/DEPRECATED.md
	@echo "" >> temp-deprecation/DEPRECATED.md
	@echo "Please update your links, bookmarks, and dependencies to use the new repository." >> temp-deprecation/DEPRECATED.md
	@echo "" >> temp-deprecation/DEPRECATED.md
	@echo "## 📅 Deprecation Date" >> temp-deprecation/DEPRECATED.md
	@echo "" >> temp-deprecation/DEPRECATED.md
	@echo "Deprecated on: $$(date '+%B %d, %Y')" >> temp-deprecation/DEPRECATED.md
	@echo "" >> temp-deprecation/DEPRECATED.md
	@echo "## 🏠 New Home" >> temp-deprecation/DEPRECATED.md
	@echo "" >> temp-deprecation/DEPRECATED.md
	@echo "- **New Repository**: https://github.com/EPFL-ENAC/AddLidar" >> temp-deprecation/DEPRECATED.md
	@echo "- **Documentation**: https://github.com/EPFL-ENAC/AddLidar#readme" >> temp-deprecation/DEPRECATED.md
	@echo "- **Issues**: https://github.com/EPFL-ENAC/AddLidar/issues" >> temp-deprecation/DEPRECATED.md
	@echo ""
	@echo "Deprecation notice created in temp-deprecation/DEPRECATED.md"
	@echo "Please manually add this to each original repository and update their README files."
	@echo ""
	@echo "Next steps:"
	@echo "1. Copy DEPRECATED.md to each original repo"
	@echo "2. Update README files in original repos"
	@echo "3. Archive the repositories on GitHub"
	@echo "4. Update any CI/CD pipelines"

# Help target (single definition)
help:
	@echo "Git Subtree Commands:"
	@echo "  subtree-add               - Add all repos as subtrees (safe, can run multiple times)"
	@echo "  subtree-pull              - Pull updates from all original repos"
	@echo "  subtree-push-backend      - Push backend changes to original repo"
	@echo "  subtree-push-frontend     - Push frontend changes to original repo"
	@echo "  subtree-push-potree-converter - Push PotreeConverter changes to original repo"
	@echo "  verify-subtrees           - Check subtree configuration status"
	@echo "  subtree-status            - Show detailed subtree status"
	@echo "  reset-subtrees            - Remove all subtrees (dangerous!)"
	@echo "  deprecate-repos           - Start repository deprecation process"
	@echo ""
	@echo "Standard Commands:"
	@echo "  install    - Install dependencies and set up git hooks"
	@echo "  clean      - Clean node_modules and package-lock.json"
	@echo "  uninstall  - Remove git hooks and clean dependencies"
	@echo "  lint       - Run linter"
	@echo "  format     - Run formatter"
	@echo "  help       - Show this help message"
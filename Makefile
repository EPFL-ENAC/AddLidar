.PHONY: setup install clean uninstall help

# Default target
help:
	@echo "Available commands:"
	@echo "  setup      - Set up repository from template (first-time setup)"
	@echo "  install    - Install dependencies and set up git hooks"
	@echo "  clean      - Clean node_modules and package-lock.json"
	@echo "  uninstall  - Remove git hooks and clean dependencies"
	@echo "  help       - Show this help message"


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


# Repository configuration
SUBTREES = backend frontend potree-converter
BACKEND_REPO = git@github.com:EPFL-ENAC/AddLidar-API.git
FRONTEND_REPO = git@github.com:EPFL-ENAC/AddLidar-Potree.git
POTREECONVERTER_REPO = git@github.com:EPFL-ENAC/PotreeConverterMakefile.git

# Map directory names to repository URLs
get-repo-url = $(if $(filter backend,$1),$(BACKEND_REPO),$(if $(filter frontend,$1),$(FRONTEND_REPO),$(if $(filter potree-converter,$1),$(POTREECONVERTER_REPO),)))

# Check if a subtree already exists
check-subtree-exists = $(shell git log --grep="git-subtree-dir: $(1)" --oneline | head -1)

# Generic function to process a single subtree
define process-subtree
	@echo "🔄 Processing $(1) subtree..."
	@if [ -d "$(1)" ]; then \
		if [ -n "$(call check-subtree-exists,$(1))" ]; then \
			echo "✅ $(1) subtree already exists and is properly configured"; \
		else \
			echo "⚠️  $(1) directory exists but is not a subtree. Manual intervention required."; \
		fi; \
	else \
		echo "📥 Adding $(1) subtree..."; \
		if git subtree add --prefix=$(1) $(call get-repo-url,$(1)) main --squash 2>/dev/null; then \
			echo "✅ $(1) subtree added successfully"; \
		else \
			echo "❌ Failed to add $(1) subtree. Check repository URL and permissions."; \
			exit 1; \
		fi; \
	fi
endef

# Generic function to push to a subtree
define push-subtree
	@echo "Pushing $(1) changes to original repo..."
	@read -p "Enter branch name for $(1) repo: " branch; \
	git subtree push --prefix=$(1) $(call get-repo-url,$(1)) $$branch
endef

# Safe subtree addition
subtree-add:
	@echo "🔍 Performing safe subtree addition..."
	@$(MAKE) check-git-clean
	@$(foreach subtree,$(SUBTREES),$(call process-subtree,$(subtree)))
	@echo "✅ All subtrees processed successfully!"

# Pull updates from all original repos
subtree-pull:
	@echo "Pulling updates from all subtrees..."
	@$(foreach subtree,$(SUBTREES), \
		echo "Pulling updates from $(subtree)..." && \
		git subtree pull --prefix=$(subtree) $(call get-repo-url,$(subtree)) main --squash &&) true
	@echo "All subtrees updated successfully!"

# Push commands using the generic function
subtree-push-backend:
	$(call push-subtree,backend)

subtree-push-frontend:
	$(call push-subtree,frontend)

subtree-push-potree-converter:
	$(call push-subtree,potree-converter)

# Check if git working directory is clean
check-git-clean:
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "❌ Git working directory is not clean. Please commit or stash changes first."; \
		exit 1; \
	fi

# Verify subtree configuration
verify-subtrees:
	@echo "🔍 Verifying subtree configuration..."
	@$(foreach subtree,$(SUBTREES), \
		echo -n "$(subtree): " && \
		if [ -d "$(subtree)" ]; then \
			if [ -n "$(call check-subtree-exists,$(subtree))" ]; then \
				echo "✅ Properly configured as subtree"; \
			else \
				echo "⚠️  Directory exists but not configured as subtree"; \
			fi; \
		else \
			echo "❌ Directory missing"; \
		fi &&) true

# Show subtree status
subtree-status:
	@echo "📊 Subtree Status Report:"
	@echo "========================"
	@$(foreach subtree,$(SUBTREES), \
		echo -n "$(subtree): " && \
		if [ -d "$(subtree)" ]; then \
			if [ -n "$(call check-subtree-exists,$(subtree))" ]; then \
				echo "✅ Active subtree"; \
			else \
				echo "⚠️  Directory exists (not a subtree)"; \
			fi; \
		else \
			echo "❌ Missing"; \
		fi &&) true

# Reset subtrees (dangerous - use with caution)
reset-subtrees:
	@echo "⚠️  This will remove all subtree directories and their git history!"
	@echo "Make sure you have backups before proceeding."
	@read -p "Are you absolutely sure? Type 'DELETE' to confirm: " confirm; \
	if [ "$$confirm" = "DELETE" ]; then \
		echo "Removing subtree directories..."; \
		rm -rf $(SUBTREES); \
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

# Update help
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

.PHONY: subtree-add subtree-pull subtree-push-backend subtree-push-frontend subtree-push-potree-converter check-git-clean verify-subtrees reset-subtrees subtree-status
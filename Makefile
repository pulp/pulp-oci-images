help: ## Show this help.
	@sed -ne '/@sed/!s/## //p' $(MAKEFILE_LIST)

docs: ## Build unified docs
	pulp-docs build

servedocs: ## Serves unified docs
	pulp-docs serve

.PHONY: docs servedocs help

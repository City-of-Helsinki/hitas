.PHONY: help
.PHONY: up


define helptext

 Commands:

 up                              Build and run docker containers for the stack.

endef

export helptext

# Help should be first so that make without arguments is the same as help
help:
	@echo "$$helptext"

up:
	docker-compose up --detach --build

# Default target
.DEFAULT_GOAL := help

# Include .env if it exists
# -include .env

# Needed for CI
SHELL := /bin/bash

# Python defaults
export UV_PYTHON := 3.13

SRC_DIR := src
TEST_DIR := tests
DIRS_TO_LINT := $(SRC_DIR) $(TEST_DIR)

# Common ECR image repository
# AWS_ACCOUNT_ID ?= 122183027568
# AWS_REGION ?= us-east-2

.PHONY: check-uv
check-uv: ## ensure that the uv CLI is installed
	@which uv > /dev/null 2>&1 || (echo "Error: uv CLI is not installed. Please install it before proceeding." && exit 1)
	@echo "uv CLI is installed and ready to use."


# .PHONY: init 
# init: install
# 	test -f .env || cp .env.example .env


.PHONY: install
install: check-uv ## install all required packages (will also create venv)
	# Note that this automatically generates a virtual environment pinned at the python version specified in UV_PYTHON
	# Will automatically download the specified python version if not available
	@echo "Using Python at: $${UV_PYTHON}"
	${CD_DAG_DIR} uv sync


.PHONY: format
format: check-uv  ## format all Python code with black
	uv run -m black ${SRC_DIR}


.PHONY: lint
lint: check-uv  ## lint all Python code with pylint + validate formatting
	uv run -m black --check --diff ${SRC_DIR}
	uv run -m pylint ${DIRS_TO_LINT}
	uv lock --check
	uv sync --check


.PHONY: test
test: check-uv  ## run all tests with pytest
	uv run -m pytest


.PHONY: run
run:  ## run scripts
	AWS_PROFILE=${AWS_PROFILE} uv run -m src ${ARGS}


.PHONY: install-and-run
install-and-run: install run ## install and run scripts locally


.PHONY: install-and-test
install-and-test: install test ## install and test scripts locally


.PHONY: help
help: ## Display this help screen
	@echo "Usage: make <target>"
	@awk 'BEGIN {FS = ":.*##"; printf "\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  %-20s %s\n", $$1, $$2 }' ${MAKEFILE_LIST}
	# @echo ${AWS_REGION}

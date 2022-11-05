LOCALSTACK_CONTAINER_NAME="localstack"

.DEFAULT_GOAL := help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-40s\033[0m %s\n", $$1, $$2}'

setup: ## Setup a dev environment for working in this repo. Assumes in a venv or other isolation
	pip install -r .github/workflows/constraints.txt
	poetry install

build: setup ## build python packages
	pip install twine build
	python -m build --sdist --wheel --outdir dist/
	twine check dist/*

test: setup ## Run unit tests
	pytest

start-localstack: # Runs localstack for SQS and creates a quee that can be used for testing
	docker run -it -d --rm --name $(LOCALSTACK_CONTAINER_NAME) -p 4566:4566 -p 4571:4571 localstack/localstack || echo "$(LOCALSTACK_CONTAINER_NAME) is either running or failed"
	AWS_ACCESS_KEY_ID=x AWS_SECRET_ACCESS_KEY=x AWS_DEFAULT_REGION=us-east-1 aws --endpoint-url http://localhost:4566 sqs create-queue --queue-name test

stop-localstack: # Stops localstack
	docker stop $(LOCALSTACK_CONTAINER_NAME)

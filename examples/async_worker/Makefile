LOCALSTACK_CONTAINER="pydantic-sqs"
LOCALSTACK_QUEUE_NAME="test"


# This help function will automatically generate help/usage text for any make target that is commented with "##".
# Targets with a singe "#" description do not show up in the help text
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-40s\033[0m %s\n", $$1, $$2}'


start-localstack: ## Starts localstack in docker
	docker run -it -d --rm --name $(LOCALSTACK_CONTAINER) -p 4566:4566 -p 4571:4571 localstack/localstack || echo "$(LOCALSTACK_CONTAINER) is either running or failed"

stop-localstack: ## Stops localstack in docker
	docker rm -f $(LOCALSTACK_CONTAINER)

create-localstack-queue: ## Creates a test queue in localstack
	AWS_ACCESS_KEY_ID=x AWS_SECRET_ACCESS_KEY=x AWS_DEFAULT_REGION=us-east-1 aws --endpoint-url http://localhost:4566 sqs create-queue --queue-name test

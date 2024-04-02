
.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

requirements: ## Generate requirements.txt
	# strip extras?  see: https://lincolnloop.com/insights/using-pyprojecttoml-in-your-django-project/
	pip-compile \
	  --generate-hashes \
	  --output-file requirements.txt \
	  pyproject.toml

docker-image: ## Build a docker image
	docker build -t pytexbot .

run-docker: ## Run the docker image from 'make docker-image'
	docker run -it --env-file ./.env pytexbot

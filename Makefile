container:
	@echo "===================================================================="
	@echo "Build Docker Container"
	@echo "===================================================================="
	@docker build --tag ucyo/geomatch:prod .

prod: container
	@echo "===================================================================="
	@echo "Start and enter container"
	@echo "===================================================================="
	@docker run --env-file=.env --rm -it -v $(shell pwd)/code:/home/python/code --workdir /home/python/code ucyo/geomatch:prod /bin/bash

dev-container:
	@echo "===================================================================="
	@echo "Build Docker Container"
	@echo "===================================================================="
	@docker build --target builder --tag ucyo/geomatch:dev .

bash: dev-container
	@echo "===================================================================="
	@echo "Start and enter container"
	@echo "===================================================================="
	@docker run --env-file=.env --rm -it -v $(shell pwd)/code:/home/python/code --workdir /home/python/code ucyo/geomatch:dev /bin/bash


.PHONY: container prod dev-container bash

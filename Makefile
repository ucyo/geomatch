container:
	@echo "===================================================================="
	@echo "Build Docker Container"
	@echo "===================================================================="
	@docker build --tag code/code .

bash: container
	@echo "===================================================================="
	@echo "Start and enter container"
	@echo "===================================================================="
	@docker run --rm -it -v $(shell pwd)/code:/home/python/code --workdir /home/python/code code/code /bin/bash

.PHONY: container bash

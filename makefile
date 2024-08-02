# Makefile for managing Docker-based services and setup

.PHONY: setup start stop clean wait_for_health check_docker_compose

setup:
	@echo "Performing setup..."
	# Add any setup commands here, e.g., installing Python dependencies from requirements.txt
	pip install -r requirements.txt

start: check_docker_compose
	@read -p "Do you want to build the services before starting them? (y/n): " build_choice; \
	if [ $$build_choice = "y" ]; then \
		build_option="--build"; \
	else \
		build_option=""; \
	fi; \
	$(MAKE) wait_for_health start_services BUILD_OPTION=$$build_option

start_services:
	@echo "Starting services..."
	docker-compose up $$(BUILD_OPTION) -d
	@read -p "Do you want to download models (y/n)? " choice; \
	if [ $$choice = "y" ]; then \
		read -p "Enter model names separated by spaces: " models; \
		docker exec -it ollama ollama pull $$models; \
	fi

stop:
	@echo "Stopping services..."
	docker-compose down --remove-orphans

clean:
	@echo "Cleaning up..."
	docker-compose down -v --remove-orphans
	docker network prune -f
	docker system prune -f

check_docker_compose:
	@command -v docker-compose >/dev/null 2>&1 || { \
		read -p "docker-compose not found. Do you want to install it? (y/n) " choice; \
		if [ "$$choice" = "y" ]; then \
			sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose; \
			sudo chmod +x /usr/local/bin/docker-compose; \
			echo "docker-compose installed successfully."; \
		else \
			echo "docker-compose is required. Exiting."; \
			exit 1; \
		fi \
	}

wait_for_health:
	@echo "Waiting for all services to become healthy..."
	@services=$$(docker-compose ps --services); \
	healthy_services=0; \
	total_services=$$(echo $$services | wc -w); \
	while [ $$healthy_services -lt $$total_services ]; do \
		healthy_services=0; \
		for service in $$services; do \
			health=$$(docker inspect --format='{{json .State.Health.Status}}' "$$(docker-compose ps -q $$service)" 2>/dev/null); \
			if [ "$$health" = "\"healthy\"" ]; then \
				healthy_services=$$((healthy_services + 1)); \
			elif [ "$$health" = "\"unhealthy\"" ]; then \
				echo " - $$service is unhealthy"; \
				exit 1; \
			fi; \
		done; \
		if [ $$healthy_services -lt $$total_services ]; then \
			printf "."; \
			sleep 1; \
		fi; \
	done; \
	echo "All services are healthy!"

HOST_IP := $(shell ip -4 addr show | grep -oP '10\.\d+\.\d+\.\d+' | head -n 1)

all: build up

up:
	HOST_IP=$(HOST_IP) docker compose -f docker-compose.yml up

build:
	@echo "Detected IP: $(HOST_IP)"
	@sed -i "s/^NEW_HOST=.*/NEW_HOST=$(HOST_IP)/" .env/dev.env || echo "NEW_HOST=$(HOST_IP)" >> .env/dev.env
	HOST_IP=$(HOST_IP) docker compose -f docker-compose.yml build

down:
	docker compose -f docker-compose.yml down -v

clean: down
	docker volume prune -f
	docker system prune -af

.PHONY: all build up down clean
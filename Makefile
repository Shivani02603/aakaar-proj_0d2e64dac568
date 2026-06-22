install:
	pip install -r requirements.txt
	cd frontend && npm install

dev:
	./scripts/dev.sh

build:
	docker-compose build

test:
	pytest
	cd frontend && npm test

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

clean:
	docker-compose down --volumes --remove-orphans
	rm -rf backend/__pycache__ frontend/.next frontend/node_modules
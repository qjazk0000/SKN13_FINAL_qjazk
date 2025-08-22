.PHONY: up down logs ps snap restore reindex

up:
	docker compose up -d --build

down:
	# 데이터 보존: -v 금지!
	docker compose down

logs:
	docker compose logs -f --tail=200 qdrant backend

ps:
	docker compose ps

snap:
	docker compose exec backend python manage.py qdrant_snapshot

restore:
	# 예: make restore location=/qdrant/snapshots/collections/regulations_final-<timestamp>.snapshot
	docker compose exec backend python manage.py qdrant_restore --location=$(location)

reindex:
	# 여기에 문서 재임베딩/업서트 스크립트를 연결해도 됨 (추후)
	@echo "TODO: implement reindex pipeline" 
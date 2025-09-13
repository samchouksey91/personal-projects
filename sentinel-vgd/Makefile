.PHONY: seed demo up ci

seed:
	python data/seed_duckdb.py

demo:
	python eval/run_eval.py

up:
	uvicorn api.main:app --reload

ci:
	python eval/run_eval.py --ci

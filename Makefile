.PHONY: install lint format test reproduce figures pdf clean

PYTHON ?= python3

install:
	$(PYTHON) -m pip install -e ".[dev]"

lint:
	ruff check .
	black --check .

format:
	ruff check . --fix
	black .

test:
	$(PYTHON) -m scripts.run list
	# Smoke: sanity-only pass; real evaluation needs Docker + agent harness
	@echo "(real evaluation requires Docker; see README)"

reproduce:
	$(PYTHON) -m scripts.run run --agent claude-code --tasks all --verbose
	$(PYTHON) -m scripts.cross_lingual_delta
	$(PYTHON) -m scripts.leaderboard

figures: reproduce
	@echo "regenerated paper/figs/*.tex"

pdf: figures
	cd paper && pdflatex -interaction=nonstopmode main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex

clean:
	rm -rf logs/*.log logs/last_run.json logs/cross_lingual_delta.json
	rm -f paper/main.aux paper/main.log paper/main.bbl paper/main.blg paper/main.out paper/main.pdf

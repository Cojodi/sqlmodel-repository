all: help

test: ## run the tests
	pytest -s

test-cov: ## run the tests with coverage
	python3 -m pytest -s tests \
        --cov-report term-missing:skip-covered \
        --cov-config pytest.ini \
        --cov=. tests/ \
        -vv

help: ## prints help for target1 and target2
	@grep '##' $(MAKEFILE_LIST) \
		| grep -Ev 'grep|###' \
		| sed -e 's/^\([^:]*\):[^#]*##\([^#]*\)$$/\1:\2/' \
		| awk -F ":" '{ printf "%-18s%s\n", $$1 ":", $$2 }' \
		| grep -v 'sed'

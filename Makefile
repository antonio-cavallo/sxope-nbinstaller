help:
	@echo "make tests"

.PHONY: tests
tests:
	PYTHONPATH=src pytest -vvs tests 

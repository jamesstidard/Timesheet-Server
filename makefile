init:
	pip install -r requirements.txt
	pip install -e .
initialise:
	python -m timesheet.initialise
test:
	py.test tests
run:
	python -m timesheet.server

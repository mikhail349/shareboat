lint:
	isort . && flake8 && mypy .

install:
	pip install -r requirements.txt -r requirements_dev.txt

test:
	coverage run manage.py test -v 2 --exclude-tag=slow

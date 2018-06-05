install:
	pip install pipenv
	pipenv install --dev

test:
	pipenv run -- coverage run --include="django_k8s/*" manage.py test

coveralls:
	pipenv run -- coveralls

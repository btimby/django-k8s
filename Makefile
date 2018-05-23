install:
	pip install pipenv
	pipenv install --dev

test:
	cd django_k8s && pipenv run -- coverage run -p --include=django_k8s/* manage.py test django_k8s

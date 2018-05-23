install:
	pip install pipenv
	pipenv install --dev

test:
	cd django_k8s && pipenv run -- python manage.py test django_k8s

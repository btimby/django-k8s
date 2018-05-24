install:
	pip install pipenv
	pipenv install --dev

test:
	cd django_k8s && pipenv run -- coverage run --include="django_k8s/*" manage.py test django_k8s

coveralls:
	cd django_k8s && pipenv run -- coveralls

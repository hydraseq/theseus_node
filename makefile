default:
	cat makefile

test:
	py.test -v tests


release:
	rm -rf dist
	mkdir dist
	python setup.py sdist bdist_wheel
	python -m twine upload dist/*

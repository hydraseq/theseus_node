from invoke import task
from invoke import run

@task
def tests(c):
    c.run('python -vvx tests')
    result = run('python -vvx tests')
    print(result.ok)
    print(result.stdout.splitlines()[-1])
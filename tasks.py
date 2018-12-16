from invoke import task

@task
def tests(c):
    c.run('python -vvx tests')
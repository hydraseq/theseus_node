from invoke import task

@task
def tests(c):
    c.run('py.test -vvx tests', pty=True)

import nox

nox.options.reuse_existing_virtualenvs = True
nox.options.sessions = []

@nox.session(venv_backend="virtualenv", python="3.8")
def dev(session):
    session.install("nox>=2021.6.12")  # Dev dep, no upper bound
    session.install("-e", ".")

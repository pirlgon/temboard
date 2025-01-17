# Contributing

Thanks for your interest in contributing to temBoard. temBoard is an open
source project open to contribution from idea to code and more.


## Submitting an Issue or a Patch

We use the [dalibo/temboard] GitHub project to track issues and review
contributions. Fork the main repository and open a pull request against
`master` branch as usual.


## Cloning the Repository

Get temBoard UI and agent sources in one single repository:

```console
$ git clone https://github.com/dalibo/temboard.git
$ cd temboard/
```


## Directories Overview

[dalibo/temboard] git repository contains a few sub-projects. Here is a quick
overview.

- `docs/` - Global mkdocs documentation sources.
- `ui/` - Python Tornado project for temBoard UI aka server.
    - `ui/temboardui/toolkit` - Shared library between agent and UI.
- `agent/` - Bare Python project for temBoard agent.
    - `agent/temboardagent/toolkit` - Symlink to toolkit in UI source tree.
- `dev/` - Development scripts and setup.
  - `dev/perfui/` - Docker & Grafana project to visualize temBoard performances
    traces.
- `docker/` - Quickstart Docker Compose file.
- `tests/` - Functional integration tests.

Python package is `temboardui` for temBoard UI and `temboardagent` for temBoard
agent.


## Development Requirements

You need the following software to contribute to temBoard:

- bash, git, make, psql.
- Docker Compose.
- Python 3.6 with `venv` module.
- NodeJS and npm for building some assets.


## Setup Development

Running development version of UI and agent requires two terminals, one for
each.

The `develop` make target creates a virtual environment for Python 3.6,
installs temBoard UI, its dependencies, development tools, starts docker
services and initializes temBoard database.

``` console
$ make develop
make venv-3.6
make[1] : on entre dans le répertoire « /home/.../src/dalibo/temboard »
python3.6 -m venv dev/venv-py3.6/
...
2020-03-24 17:09:05,937 [30557] [migrator        ]  INFO: Database is up to date.
Initialized role temboard and database temboard.
docker-compose up -d
temboard_repository_1 is up-to-date
Creating temboard_instance_1 ... done
Creating temboard_agent_1    ... done


    You can now execute temBoard UI with dev/venv-py3.6/bin/temboard


$ dev/venv-py3.6/bin/temboard --debug
 INFO: Starting temboard 8.0.dev0.
 INFO: Found config file /home/.../temboard/temboard.conf.
 INFO: Running on Debian GNU/Linux 11 (bullseye).
 INFO: Using Python 3.6.8 (/home/.../.cache/pyenv/versions/temboard-uoBqmXGk-py3.6/bin/python) and Tornado 4.4.3 .
 INFO: Using libpq 11.5, Psycopg2 2.8.6 (dt dec pq3 ext lo64) and SQLAlchemy 1.3.24 .
2022-03-16 14:08:06,425 temboardui[1593889]: [pluginsmgmt     ]  INFO: Loaded plugin 'dashboard'.
...
2022-03-16 14:08:06,489 temboardui[1593889]: [temboardui      ]  INFO: Serving temboardui on https://0.0.0.0:8888
...
```

Go to [https://127.0.0.1:8888/](https://127.0.0.1:8888/) to access temBoard
running with your code!

You now need to run the agent. Open a second terminal to interact with the
agent and execute the following commands.

``` console
$ docker-compose exec agent0 /bin/bash
root@91cd7e12ac3e:/var/lib/temboard-agent# sudo -u postgres hupper -m temboardagent
 INFO: Starting temboard-agent 8.0.dev0.
 INFO: Found config file /etc/temboard-agent/temboard-agent.conf.
2020-08-11 14:29:45,834 [ 3769] [app             ] DEBUG: Looking for plugin activity.
...
```

The agent is preregistered in UI, using host `0.0.0.0`, port `2345` and key
`key_for_agent`. The monitored Postgres instance is named `postgres0.dev`.

Beware that two Postgres instances are set up with replication. The primary
instance may be either postgres0 or postgres1. See below for details.


## psql for Monitored PostgreSQL

If you need to execute queries in monitored PostgreSQL instances, execute psql
inside the corresponding agent container using the following command:

``` console
$ docker-compose exec agent0 sudo -iu postgres psql
psql (13.5 (Debian 13.5-0+deb11u1), server 14.1)
WARNING: psql major version 13, server major version 14.
         Some psql features might not work.
Type "help" for help.

postgres=#
```


## Playing with Replication

Two postgres instances are up with replication. You can execute a second agent
for it likewise:

``` console
$ docker-compose exec agent1 /bin/bash
root@91cd7e12ac3e:/var/lib/temboard-agent# sudo -u postgres hupper -m temboardagent
 INFO: Starting temboard-agent 8.0.dev0.
 INFO: Found config file /etc/temboard-agent/temboard-agent.conf.
2022-01-11 10:12:55,130 [ 1568] [app             ] DEBUG: Looking for plugin activity.
...
```

bash history is shared amongst these two containers.

In UI, the seconde agent is pre-registered with address 0.0.0.0, port 2346
instead of 2345, with the same key `key_for_agent`. The instance FQDN is
`postgres1.dev`.

The script `dev/switchover.sh` triggers a switchover between the two postgres
instances. Executing `dev/switchover.sh` one more time restore the original
typology.


## Testing with previous stable version

Compose project for development configures a stable agent named `agent-stable`.
This agent is preregistered in development UI. Browser `postgres-stable`
instance in UI to ensure temBoard UI is compatible with stable agent.

Access Postgres instance monitored by stable agent using the following compose
invocation:

``` console
$ docker-compose exec agent-stable sudo -u postgres psql
psql (13.5 (Debian 13.5-0+deb11u1), server 13.7)
Type "help" for help.

postgres=#
```


## Launching Multiple Agents

Default development environment instanciates two PostgreSQL instances and their
temBoard agents. Root Makefile offers two targets to help testing big scale
setup :

- `make mass-agents` loops from 2348 to 3000 and instanciate a PostgreSQL
  instance for each number and an agent to monitor it. Number is used as agent
  port. Each instanciation requires you to type `y` and Enter. This allows to
  throttle instanciations and to stop when enough instances are up.
- `make clean-agents` trashes every existing instances from 2348 to 3000,
  without interaction. **make clean-agents does not unregister agents!**


## Choosing PostgreSQL Version

You can change the version of the monitored PostgreSQL instance by overriding
image tag in `docker-compose.override.yml`.

``` yml
# file docker-compose.override.yml
version: "3.8"

services:
  postgres0:
    image: postgres:9.5-alpine &postgres_image

  postgres1:
    image: *postgres_image
```

Now apply changes with `make develop`. Docker-compose will recreate `postgres0`
and `agent0` containers, thus you need to start the agent as documented above.

Note that defining a different major version for postgres0 and postgres1 breaks
physical replication.


## Execute Unit Tests

Each UI and agent project has its own unit tests battery. Enable the virtualenv
and use pytest to run unit tests:

``` console
$ . dev/venv-py3.6/bin/activate
$ pytest ui/tests/unit
...
==== 31 passed, 10 warnings in 1.10 seconds ======
$ pytest agent/tests/unit
...
=============== 6 passed in 0.25s ================
$
```


## Execute Integration Tests

The `tests/` directory contains a pytest project to tests UI and agent
integration using Selenium.

Execute these tests right from your virtualenv, using pytest:

``` console
$ . dev/venv-py3.6/bin/activate
$ pytest tests/
============================= test session starts ==============================
platform linux -- Python 3.6.8, pytest-7.0.1, pluggy-1.0.0 -- /home/bersace/src/dalibo/temboard/dev/venv-py3.6/bin/python3.6
cachedir: .pytest_cache
postgresql: 14 (/usr/lib/postgresql/14/bin)
sqlalchemy: 1.4.35
system: Debian GNU/Linux 11 (bullseye)
tornado: 6.1
libpq: 14.2
psycopg2: 2.9.3 (dt dec pq3 ext lo64)
temboard: 8.0.dev0 (/home/bersace/src/dalibo/temboard/dev/venv-py3.6/bin/temboard)
temboard-agent: 8.0.dev0 (/home/bersace/src/dalibo/temboard/dev/venv-py3.6/bin/temboard-agent)
rootdir: /home/bersace/src/dalibo/temboard/tests, configfile: pytest.ini
plugins: mock-3.6.1, cov-3.0.0, tornado-0.8.1, anyio-3.5.0
...
tests/test_00_setup_ui.py::test_temboard_version PASSED                  [ 12%]
...
tests/test_20_register.py::test_web_register PASSED                      [100%]

============================== 8 passed in 17.69s ==============================
$
```

`pytests tests/ --help` describes custom options `--pg-version` and
`--selenium`. Take care of the custom pytest report header, it shows which
temboard and temboard-agent binary is used, the bin directory of PostgreSQL and
more.

`pytests tests/ --fixtures` describes fixtures defined by tests/conftest.py.
Fixtures configure a postgres for monitoring, an agent and the UI in `workdir/`
prefix. This may help you write a new test.

Selenium standalone container runs a headless Xvfb server with noVNC enabled.
View live tests in your browser at http://localhost:7900/ . Click the connect
button and interract with the browser and UI.

Selenium container may be flaky. If you suspend your computer, you may have
timeout from selenium. Use `make restart-selenium` to workaround this.


## Coding Style

An `.editorconfig` file configures whitespace and charset handling in various
programming language. The [EditorConfig]( http://editorconfig.org/#download)
site links to plugins for various editors. See `.editorconfig` for a
description of the conventions. Please stick to these conventions.

Python syntax must conform to flake8. CI checks new code with flake8.


## UI Database Schema Version

temBoard repository is versionned. A version is the name of a file in
`temboardui/model/versions`. Each file contains the code to execute to upgrade
to this version.

To create a new version, put a new file in `temboardui/model/versions/`
prefixed with a discrete number following the last version. As of now, version
file must ends with `.sql` and contains valid PostgreSQL SQL.

That's all. Use `temboard migratedb` to check and upgrade temBoard repository.


## Building CSS and Javascript

temBoard UI mainly relies on Bootstrap. The CSS files are compiled with SASS.
Execute all the following commands in ui/ directory.

In case you want to contribute on the styles, first install the nodeJS dev
dependencies:

``` console
$ npm install
```

Then you can either build a dist version of the CSS:

``` console
$ grunt sass:dist
```

Or build a dev version which will get updated each time you make a change in
any of the .scss files:

``` console
$ grunt watch
```


## Editing Documentation

The documentation is written in Markdown and built with `mkdocs`.

``` console
$ dev/venv-py3.6/bin/mkdocs serve
INFO     -  Building documentation...
INFO     -  Cleaning site directory
INFO     -  The following pages exist in the docs directory, but are not included in the "nav" configuration:
              - alerting.md
              - postgres_upgrade.md
INFO     -  Documentation built in 0.42 seconds
INFO     -  [16:21:24] Serving on http://127.0.0.1:8000/
...
```

Go to [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to view the
documentation. mkdocs has hot reload: saving file triggers a refresh in your
browser.


## Building RHEL Package

Building RPM packages for RHEL and compatible clones requires Docker and Docker
Compose for isolation. Uploading to Dalibo Labs requires internal project
yum-labs and access.

UI and agent each has `packaging/rpm` directory with a Makefile and scripts to
build RPM packages. Use the following targets to build and push packages:

- `make -C ui/packaging/rpm/ build-rhel<version>` - Build RPM.
- `make -C ui/packaging/rpm/ push` - Push **all** packages to yum.dalibo.org/labs.
- `make -C ui/packaging/rpm/ release-rhel<version>` - Build and push alltogether.

Version can be either 8 or 7. `agent/packaging/rpm/Makefile` provides the same
targets.

The builder script search for wheels in `ui/dist/` and if not found, tries to
download wheel from PyPI. Use top level `make dist` to generate a snapshot.


## Building Debian Package

Building debian packages requires Docker and Docker Compose for isolation. For
signing, you need the ``devscripts`` package and a GPG private key. For
uploading, you require ``dput``.

```
sudo apt install devscripts dput
```

Define environment variables `DEBFULLNAME` and `DEBEMAIL`. mkchanges.sh scripts
signs changes with your GPG key matching these environment variables.

Each UI and agent has `packaging/deb/` directory with a Makefile and scripts to
build packages. Use the following make target to build and push packages:

- `make -C ui/packaging/deb build-<codename>` - Build.
- `make -C ui/packaging/deb push` - Push previously build package.
- `make -C ui/packaging/deb release-<codename>` - Build and push alltogether.

`codename` is one of `bullseye`, `buster` or `stretch`.
`agent/packaging/deb/Makefile` provides the same targets.

The builder script search for wheels in `ui/dist/` and if not found, tries to
download wheel from PyPI. Use top level `make dist` to generate a snapshot.


## Releasing

Releasing a new version of temBoard requires write access to master branch on
[main repository](https://github.com/dalibo/temboard), [PyPI
project](https://pypi.org/project/temboard), [Docker Hub
repository](https://hub.docker.com/r/dalibo/temboard) and Dalibo Labs YUM and
APT repositories.

To release a new version:

- Checkout release branch (like v7).
- Choose the next version according to [PEP
  440](https://www.python.org/dev/peps/pep-0440/#version-scheme).
- Update `ui/temboardui/version.py` and `agent/temboardagent/version.py`
  without committing. The version must be the same.
- Generate and push commit and tag with `make release`.
- Push Python eggs to PyPI using `make release-pypi`.
- Build and upload Debian and RPM package with `make release-packages`.


## Throw Development Environment

`make clean` destroy virtual environments and docker services. Restart from
`make develop` as documented above. If you only need to trash services, use
docker-compose as usual : `docker-compose down -v`, running `make develop` will
restart them and configure the database.


[dalibo/temboard]: https://github.com/dalibo/temboard

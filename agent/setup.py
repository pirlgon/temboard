from setuptools import setup, find_packages, __version__ as setuptoolsv
import os

# Load version number
__version__ = None
setup_path = os.path.dirname(os.path.realpath(__file__))
exec(open(os.path.join(setup_path, 'temboardagent', 'version.py')).read())

if setuptoolsv < '1.0':
    __version__ = __version__.replace('+', '.')

setup(**dict(
    name='temboard-agent',
    version=__version__,
    author='Dalibo',
    author_email='contact@dalibo.com',
    license='PostgreSQL',
    url='http://temboard.io/',
    description='PostgreSQL Remote Control Agent',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Environment :: No Input/Output (Daemon)",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved",
        "Operating System :: POSIX :: Linux",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: System :: Monitoring",
    ],
    python_requires='~=3.5',
    install_requires=[
        'bottle >= 0.12, <0.13',
        'cryptography',
    ],
    data_files=[
        ('share/temboard-agent/', [
            'share/auto_configure.sh',
            'share/purge.sh',
            'share/restart-all.sh',
        ]),
        ('share/temboard-agent/quickstart/', [
            'share/temboard-agent_CHANGEME.pem',
            'share/temboard-agent_CHANGEME.key',
            'share/temboard-agent_ca_certs_CHANGEME.pem',
        ]),
        ('lib/systemd/system', ['packaging/temboard-agent@.service']),
    ],
    entry_points={
        'console_scripts': [
            'temboard-agent = temboardagent.__main__:main',
        ],
        'temboardagent.plugins': [
            'activity = temboardagent.plugins.activity:ActivityPlugin',
            'administration = temboardagent.plugins.administration:AdministrationPlugin',  # noqa
            'dashboard = temboardagent.plugins.dashboard:DashboardPlugin',
            'maintenance = temboardagent.plugins.maintenance:MaintenancePlugin',  # noqa
            'monitoring = temboardagent.plugins.monitoring:MonitoringPlugin',
            'pgconf = temboardagent.plugins.pgconf:PgConfPlugin',
            'statements = temboardagent.plugins.statements:StatementsPlugin',
        ],
    },
    packages=find_packages(),
    long_description=open('README.rst').read(),
))

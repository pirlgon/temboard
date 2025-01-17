import logging
import time

from bottle import Bottle, default_app

from ...toolkit import taskmanager
from ...toolkit.configuration import OptionSpec

from . import db
from . import metrics


bottle = Bottle()
logger = logging.getLogger(__name__)
workers = taskmanager.WorkerSet()


@bottle.get('/')
def dashboard():
    return metrics.get_metrics_queue(default_app().temboard.config)


@bottle.get('/config')
def dashboard_config():
    app = default_app().temboard
    return dict(
        scheduler_interval=app.config.dashboard.scheduler_interval,
        history_length=app.config.dashboard.history_length,
    )


@bottle.get('/live')
def dashboard_live():
    return metrics.get_metrics(default_app().temboard)


@bottle.get('/history')
def dashboard_history():
    return metrics.get_history_metrics_queue(default_app().temboard.config)


@bottle.get('/buffers')
def dashboard_buffers(pgconn):
    return metrics.get_buffers(pgconn)


@bottle.get('/hitratio')
def dashboard_hitratio(pgconn):
    return metrics.get_hitratio(pgconn)


@bottle.get('/active_backends')
def dashboard_active_backends(pgconn):
    return metrics.get_active_backends(pgconn)


@bottle.get('/cpu')
def dashboard_cpu():
    return metrics.get_cpu_usage()


@bottle.get('/loadaverage')
def dashboard_loadaverage():
    return metrics.get_loadaverage()


@bottle.get('/memory')
def dashboard_memory():
    return metrics.get_memory_usage()


@bottle.get('/hostname')
def dashboard_hostname():
    return metrics.get_hostname(default_app().temboard.config)


@bottle.get('/os_version')
def dashboard_os_version():
    return metrics.get_os_version()


@bottle.get('/pg_version')
def dashboard_pg_version(pgconn):
    return metrics.get_pg_version(pgconn)


@bottle.get('/n_cpu')
def dashboard_n_cpu():
    return metrics.get_n_cpu()


@bottle.get('/databases')
def dashboard_databases(pgconn):
    return metrics.get_databases(pgconn)


@bottle.get('/info')
def dashboard_info(pgconn):
    return metrics.get_info(pgconn, default_app().temboard.config)


@bottle.get('/max_connections')
def dashboard_max_connections(pgconn):
    return metrics.get_max_connections(pgconn)


@workers.register(pool_size=1)
def dashboard_collector_worker(app):
    logger.info("Running dashboard collector.")

    data = metrics.get_metrics(app)

    # We don't want to store notifications in the history.
    data.pop('notifications', None)
    logger.debug(data)

    db.add_metric(
        app.config.temboard.home,
        'dashboard.db',
        time.time(),
        data,
        app.config.dashboard.history_length
    )

    logger.debug("Done")


class DashboardPlugin:
    PG_MIN_VERSION = (90400, 9.4)
    s = 'dashboard'
    option_specs = [
        OptionSpec(s, 'scheduler_interval', default=2, validator=int),
        OptionSpec(s, 'history_length', default=150, validator=int),
    ]
    del s

    def __init__(self, app, **kw):
        self.app = app
        self.app.config.add_specs(self.option_specs)

    def bootstrap(self):
        db.bootstrap(self.app.config.temboard.home, 'dashboard.db')

    def load(self):
        default_app().mount('/dashboard', bottle)
        self.app.worker_pool.add(workers)
        workers.schedule(
            id='dashboard_collector',
            redo_interval=self.app.config.dashboard.scheduler_interval
        )(dashboard_collector_worker)
        self.app.scheduler.add(workers)

    def unload(self):
        self.app.scheduler.remove(workers)
        self.app.worker_pool.remove(workers)
        self.app.config.remove_specs(self.option_specs)

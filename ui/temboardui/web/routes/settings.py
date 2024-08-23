from flask import current_app as app
from flask import g, render_template

from ...model import orm
from ..flask import admin_required


@app.route("/settings/instances")
@admin_required
def settings_instances():
    return render_template(
        "settings/instances.html",
        sidebar=True,
        instance_list=orm.Instance.all().with_session(g.db_session).all(),
    )


@app.route("/settings/groups/instance")
@admin_required
def settings_instance_groups():
    return render_template(
        "settings/instance-groups.html",
        sidebar=True,
        groups=orm.Groups.all("instance").with_session(g.db_session).all(),
    )


@app.route("/settings/users")
@admin_required
def settings_users():
    return render_template(
        "settings/users.html",
        sidebar=True,
        role_list=orm.Role.all().with_session(g.db_session).all(),
    )


@app.route("/settings/groups/role")
@admin_required
def settings_groups():
    return render_template(
        "settings/groups.html",
        sidebar=True,
        groups=orm.Groups.all("role").with_session(g.db_session).all(),
    )

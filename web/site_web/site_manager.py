from flask import render_template

from site_web import site_blueprint
from site_web.site_login import require_type


@site_blueprint.route('/manager')
@require_type(['MANAGER', 'ADMIN'])
def manger():
    return render_template('manager.html')
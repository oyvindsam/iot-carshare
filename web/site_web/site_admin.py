from flask import render_template

from site_web import site_blueprint
from site_web.site_login import require_type


@site_blueprint.route('/admin')
@require_type('ADMIN')
def admin():
    return render_template('admin.html')
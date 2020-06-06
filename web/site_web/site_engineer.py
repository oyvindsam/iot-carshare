from flask import render_template

from site_web import site_blueprint
from site_web.site_login import require_type


@site_blueprint.route('/engineer')
@require_type(['ENGINEER', 'ADMIN'])
def engineer():
    return render_template('engineer.html')
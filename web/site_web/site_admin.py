from flask import redirect

from site_web import site_blueprint


@site_blueprint.route('/admin/')
def admin():
    return redirect('booking')


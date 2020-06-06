from flask import render_template

from site_web import site_blueprint


@site_blueprint.errorhandler(404)
def page_not_found(e):
    """
        Implementation of error handler in case wrong page is enterer along the url
        for example: http://127.0.0.1:5000/pagedoesnotexist
    """
    return render_template("404.html")
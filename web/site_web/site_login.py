from functools import wraps

import requests
from flask import request, render_template, g, redirect, session, abort

from site_web import site_blueprint
from site_web.flask_site import api_address


def require_type(required_type):
    """
    Helper decorator method  to see if logged in user has access to requested endpoint
    Args:
        required_type (list[string]): types (e.g. ['CUSTOMER', 'ADMIN']

    Returns: wrapped function or a render_template in not allowed

    """
    def check_role(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            type = session['person']['type']
            if type not in required_type:
                return render_template('index.html', error='Log in with a valid user to view page!')
            else:
                return fn(*args, **kwargs)
        return wrapper
    return check_role


@site_blueprint.route('/login', methods=['POST'])
def login():
    """
    Get log in data (username, password) from log in page, and try to
    authenticate with api.
    Returns: redirect to user type page, or log in page if details are not valid

    """
    response = requests.post(f"{api_address}/api/auth/login", json=request.form)
    if response.status_code == 200:
        data = response.json()
        type = data.get('type')
        # save authorization header in session
        session['auth'] = {'Authorization': 'Bearer ' + data.get('access_token')}
        # save logged in user
        session['person'] = {
            'username': data.get('username'),
            'type': type,
            'email': data.get('email')
        }
        if type == 'CUSTOMER':
            return redirect('bookcar')
        elif type == 'ADMIN':
            return redirect('admin')
        elif type == 'ENGINEER':
            return redirect('engineer')
        elif type == 'MANAGER':
            return redirect('manager')
        else:
            # should not happen really
            return abort(501, description='Unknown user type')
    else:
        return render_template('index.html', error='Could not login user!')


@site_blueprint.route('/register', methods=['POST'])
def register():
    """
    Get user detail from form post, and registers user with api
    Returns: log in page with or without error message

    """
    response = requests.post(f"{api_address}/api/auth/register", json=request.form)
    if response.status_code == 201:
        # maybe tell the user that they registered successfully
        return render_template('index.html')
    else:
        return render_template('index.html', error='Could not create user!')


@site_blueprint.route('/logout')
def logout():
    """
    Removes auth header from session
    Returns: log in page

    """
    if 'auth' in session.keys():
        del session['auth']
    return redirect('/')
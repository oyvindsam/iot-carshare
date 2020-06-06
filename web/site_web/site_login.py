import requests
from flask import request, render_template, g, redirect, session, abort

from site_web import site_blueprint
from site_web.flask_site import api_address


@site_blueprint.route('/login', methods=['POST'])
def login():
    response = requests.post(f"{api_address}/api/auth/login", json=request.form)
    if response.status_code == 200:
        data = response.json()
        type = data.get('type')
        # save authorization header in session
        session['auth'] = {'Authorization': 'Bearer ' + data.get('access_token')}
        # save logged in user
        session['person'] = {
            'username': data.get('username'),
            'type': type
        }
        if type == 'CUSTOMER':
            return redirect('bookcar')
        elif type == 'ADMIN':
            pass
        elif type == 'ENGINEER':
            pass
        elif type == 'MANAGER':
            pass
        else:
            # should not happen really
            return abort(501, description='Unknown user type')
    else:
        return render_template('index.html', error='Could not login user!')


@site_blueprint.route('/register', methods=['POST'])
def register():
    response = requests.post(f"{api_address}/api/auth/register", json=request.form)
    if response.status_code == 201:
        # maybe tell the user that they registered successfully
        return render_template('index.html')
    else:
        return render_template('index.html', error='Could not create user!')


@site_blueprint.route('/logout')
def logout():
    if 'auth' in session.keys():
        del session['auth']
    return redirect('/')
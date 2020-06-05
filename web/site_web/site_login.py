import requests
from flask import request, render_template

from site_web import site_blueprint
from site_web.flask_site import api_address


@site_blueprint.route('/login', methods=['POST'])
def login():
    response = requests.post(f"{api_address}/api/auth/login", json=request.form)
    if response.status_code == 200:
        g.auth = 'Authorization: Bearer ' + response.json().get('access_token')
        return render_template('bookcar.html')
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

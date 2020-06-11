import json

import requests
from flask import render_template, session, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, validators
from wtforms.fields.html5 import IntegerField, EmailField
from wtforms.validators import InputRequired

from site_web import site_blueprint
from site_web.flask_site import api_address


class PersonForm(FlaskForm):
    type_choices = [
        ('CUSTOMER', 'Customer'),
        ('ADMIN', 'Admin'),
        ('MANAGER', 'Manager'),
        ('ENGINEER', 'Engineer')
    ]

    # id is -1 for new persons
    id = IntegerField(InputRequired('Need person id'), default=-1, render_kw={'readonly': True})
    username = StringField('Username', [InputRequired('Need username')])
    first_name = StringField('First name', [InputRequired('Need first name')])
    last_name = StringField('Last name', [InputRequired('Need last name')])
    email = EmailField('Email', [InputRequired('Need email'), validators.Email()])
    password = StringField('Password', [InputRequired('Need password')])
    type = SelectField('Type', [InputRequired('Need type id')], choices=type_choices)


@site_blueprint.route('/admin/person')
def person_list():
    person_data = requests.get(f"{api_address}/api/admin/person", headers=session['auth'])
    print(json.loads(person_data.json()))
    return render_template('admin/person-list.html', person_data=json.loads(person_data.json()))


@site_blueprint.route('/admin/person/new', methods=['GET', 'POST'])
def person_detail_new():
    form = PersonForm()
    if form.validate_on_submit():
        new_person = {
            'username': form.username.data,
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'email': form.email.data,
            'type': form.type.data,
            'password': form.password.data,
        }
        response = requests.post(f"{api_address}/api/admin/person",
                                 json=json.dumps(new_person),
                                 headers=session['auth'])
        if response.status_code == 201:
            return redirect('/admin/person')
        error = response.json()['error']
        return render_template('admin/person-detail-new.html', form=form, error=error)
    return render_template('admin/person-detail-new.html', form=form)


@site_blueprint.route('/admin/person/<int:id>', methods=['GET', 'POST'])
def person_detail(id):
    form = PersonForm()
    if form.validate_on_submit():
        id = form.id.data
        person = {
            'id': id,
            'username': form.person_manufacturer.data,
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'email': form.email.data,
            'type': form.type.data,
            'password': form.password.data,
        }
        response = requests.put(f"{api_address}/api/admin/person/{id}",
                                json=json.dumps(person),
                                headers=session['auth'])
        if response.status_code == 200:
            return redirect('/admin/person')
        else:
            return render_template('admin/person-detail.html',
                                   form=form,
                                   error=response.json())
    else:
        person_data = requests.get(f"{api_address}/api/admin/person/{id}",
                                   headers=session['auth'])
        person = json.loads(person_data.json())
        form = PersonForm(**person)
        return render_template('admin/person-detail.html', form=form)


@site_blueprint.route('/admin/person/<int:id>/delete', methods=['POST'])
def person_detail_delete(id):
    response = requests.delete(f"{api_address}/api/admin/person/{id}", headers=session['auth'])
    return redirect('/admin/person')


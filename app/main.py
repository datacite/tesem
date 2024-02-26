from datetime import datetime

from flask import Flask, request, abort, redirect, render_template, url_for
from os import getenv
from flask_jwt_extended import JWTManager, decode_token
from flask_jwt_extended.exceptions import JWTDecodeError
from httpx import HTTPError
from flask_bootstrap import Bootstrap5
from dotenv import load_dotenv

from emails import send_confirmation_email
from models import User, Datafile
from database import db
from forms import RequestAccessForm

load_dotenv()
app = Flask(__name__)

app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config["SECRET_KEY"] = getenv("SECRET_KEY", "changeme")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL", "sqlite:///tesem-dev.db")
app.config["JWT_SECRET_KEY"] = getenv("JWT_SECRET_KEY", "changeme")
app.config["MAILGUN_API_KEY"] = getenv("MAILGUN_API_KEY", "changeme")
app.config["MAILGUN_ENDPOINT"] = getenv("MAILGUN_ENDPOINT", "https://api.mailgun.net/v3/mg.datacite.org")
app.config["MAILGUN_DOMAIN"] = getenv("MAILGUN_DOMAIN", "mg.datacite.org")
app.config["EMAIL_FROM"] = getenv("EMAIL_FROM", "DataCite Data Files Service")
app.config["EMAIL_ADDRESS"] = getenv("EMAIL_ADDRESS", "support@datacite.org")

db.init_app(app)
jwt = JWTManager(app)
bootstrap = Bootstrap5(app)


@app.route('/')
@app.route('/datafiles')
def index():
    datafiles = Datafile.query.all()
    return render_template('index.html', datafiles=datafiles)


@app.route('/datafiles/<datafile_slug>')
def datafile(datafile_slug):
    datafile = Datafile.query.filter_by(slug=datafile_slug).first()
    if not datafile:
        abort(404, f"Datafile {datafile_slug} does not exist")
    return render_template('datafile.html', datafile=datafile)


@app.route('/datafiles/<datafile_slug>/access', methods=['GET', 'POST'])
def request_access(datafile_slug):
    datafile = Datafile.query.filter_by(slug=datafile_slug).first()
    if not datafile:
        abort(404, f"Datafile {datafile_slug} does not exist")

    form = RequestAccessForm()
    if form.validate_on_submit():
        # create user account
        u = User()
        u.email = form.email.data
        u.name = form.name.data
        u.organisation = form.organisation.data
        u.contact = form.contact.data
        u.primary_use = form.primary_use.data
        u.additional_info = form.additional_info.data
        u.datafile = datafile
        u.requested_access_date = datetime.utcnow()
        u.save()

        token = u.generate_token()
        try:
            send_confirmation_email(u.email, u.name, datafile.name, 24, url_for('download_datafile', datafile_slug=datafile.slug, token=token, _external=True), datafile.landing_page)
            return render_template('success.html', datafile=datafile)
        except HTTPError as e:
            abort(500, "Something went wrong - please contact support@datacite.org") # todo: error handling
    else:
        return render_template('request.html', datafile=datafile, form=form)


@app.route('/datafiles/<datafile_slug>/download')
def download_datafile(datafile_slug):
    token = request.args.get('token')
    if not token or token == '':
        abort(403, "Missing token - please check the link in your email and try again, making sure to include the ?token= parameter")
    try:
        token_json = decode_token(token)
        u = User.get(token_json['sub'])
        if not u:
            abort(403, "Invalid token - please check the link in your email and try again")

        datafile = Datafile.query.filter_by(slug=datafile_slug).first()
        if not datafile:
            abort(404, f"Datafile {datafile_slug} does not exist")
        url = datafile.generate_link()
        u.access_date = datetime.utcnow()
        u.save()
        return redirect(url, code=302)
    except JWTDecodeError:
        abort(403, "Invalid token - please check the link in your email and try again")


@app.errorhandler(404)
def page_not_found(message):
    return render_template('error.html', code=404, status="Page not found", message=message), 404


@app.errorhandler(500)
def internal_server_error(message):
    return render_template('error.html', code=500, status="Internal server error", message=message), 500


@app.errorhandler(403)
def forbidden(message):
    return render_template('error.html', code=403, status="Forbidden", message=message), 403


if __name__ == '__main__':
    app.run()

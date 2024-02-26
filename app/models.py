from datetime import timedelta
import boto3
from botocore.exceptions import ClientError
from flask import url_for, render_template

from database import db, Model
from flask_jwt_extended import create_access_token


class User(Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(240), nullable=False)
    organisation = db.Column(db.String(120), nullable=False)
    contact = db.Column(db.Boolean, nullable=False)
    primary_use = db.Column(db.JSON, nullable=True)
    additional_info = db.Column(db.Text, nullable=True)
    access_date = db.Column(db.DateTime, nullable=True)
    requested_access_date = db.Column(db.DateTime, nullable=True)
    datafile_id = db.Column(db.Integer, db.ForeignKey('datafiles.id'))
    datafile = db.relationship('Datafile', lazy=True)

    def generate_token(self):
        return create_access_token(identity=self.id, expires_delta=timedelta(days=1))


class Datafile(Model):
    __tablename__ = 'datafiles'
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(24), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    size = db.Column(db.String(120), nullable=False)
    filename = db.Column(db.String(120), nullable=False)
    doi = db.Column(db.String(120), nullable=True)
    blurb = db.Column(db.Text, nullable=True)

    def generate_link(self):
        s3_client = boto3.client("s3")
        try:
            url = s3_client.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": "pidgraph-data-dumps",
                    "Key": self.filename
                },
                ExpiresIn=300,
            )
            return url
        except ClientError as e:
            # TODO: Add some logging here
            print(f"Couldn't generate presigned URL: {e}")
            return None

    @property
    def landing_page(self):
        if self.doi:
            return f"https://doi.org/{self.doi}"
        else:
            return url_for('datafile', datafile_slug=self.slug, _external=True)

    @property
    def access_button(self):
        return render_template("components/access_button.html", link=url_for('request_access', datafile_slug=self.slug))

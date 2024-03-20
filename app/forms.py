from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, TextAreaField, SelectMultipleField, widgets, RadioField, EmailField
from wtforms.validators import DataRequired, StopValidation, Email

use_choices = [
    ('research', 'Research: Analyze the dataset, identify trends, build new models.'),
    ('teaching', 'Teaching: Prepare lessons, create assignments, teach data analysis skills.'),
    ('software', 'Software Development: Build tools, create applications, integrate data sources.'),
    ('reporting', 'Reporting: Checking on external use of data.'),
    ('notsure', 'I’m not sure yet.'),
    ('other', 'Other (please specify below).')
]


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(html_tag='ul', prefix_label=False)
    option_widget = widgets.CheckboxInput()


class MultiCheckboxAtLeastOne:
    def __call__(self, form, field):
        if len(field.data) == 0:
            raise StopValidation('At least one option must be selected.')
        if 'other' in field.data and form.additional_info.data == '':
            raise StopValidation('Please provide information about your usage below.')


class EscapedLabel:
    def __init__(self, label):
        self.label = label

    def __html__(self):
        return self.label


class RequestAccessForm(FlaskForm):
    # form based on User properties
    name = StringField('Name*', validators=[DataRequired()])
    organisation = StringField('Organisational Affiliation*', validators=[DataRequired()])
    email = EmailField('Email (to receive the link to the data file)*', validators=[DataRequired(), Email()])
    contact = RadioField('Can we follow up with you at this email address to discuss your planned use of the data file?*', choices=[(True, 'Yes'), (False, 'No')], coerce=bool, validators=[DataRequired()])
    primary_use = MultiCheckboxField('What is your planned use for the data? (check all that apply)*', choices=use_choices, validators=[MultiCheckboxAtLeastOne()])
    additional_info = TextAreaField('Tell us more about how you plan to use the data!')
    accept_terms = BooleanField(EscapedLabel('I acknowledge the <a href="https://support.datacite.org/docs/datacite-data-file-use-policy" target="_blank">DataCite Data File Use Policy</a>'), validators=[DataRequired()])
    submit = SubmitField('Send link')

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, TextAreaField, SelectMultipleField, widgets, RadioField
from wtforms.validators import DataRequired, StopValidation

use_choices = [
    ('research', 'Analyze the dataset, identify trends, build new models.'),
    ('teaching', 'Prepare lessons, create assignments, teach data analysis skills.'),
    ('software', 'Build tools, create applications, integrate data sources.'),
    ('reporting', 'Checking on external use of data.'),
    ('notsure', 'I’m not sure yet.'),
    ('other', 'Other (please specify below).')
]


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(html_tag='ul', prefix_label=False)
    option_widget = widgets.CheckboxInput()


class MultiCheckboxAtLeastOne():
    def __call__(self, form, field):
        if len(field.data) == 0:
            raise StopValidation('At least one option must be selected.')
        if 'other' in field.data and form.other_use.data == '':
            raise StopValidation('Please specify your other use.')


class RequestAccessForm(FlaskForm):
    # form based on User properties
    name = StringField('Name*', validators=[DataRequired()])
    organisation = StringField('Organisational Affiliation*', validators=[DataRequired()])
    email = StringField('Email*', validators=[DataRequired()])
    contact = RadioField('Can we follow up with you at this email address to discuss your planned use of the data file?*', choices=[(True, 'Yes'), (False, 'No')], coerce=bool, validators=[DataRequired()])
    primary_use = MultiCheckboxField('What is your planned use for the data? (check all that apply)*', choices=use_choices, validators=[MultiCheckboxAtLeastOne()])
    other_use = StringField('Other use')
    additional_info = TextAreaField('Tell us more about how you plan to use the data!')
    submit = SubmitField('Request Access')

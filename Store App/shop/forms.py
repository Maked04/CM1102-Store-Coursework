from wtforms import Form, BooleanField, PasswordField, StringField, DateField, FileField, RadioField, SelectField, TextAreaField, IntegerField, ValidationError, validators
from datetime import datetime
import pycountry


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def validateFile(form, field):
    filename = field.data
    if '.' in filename:
        ext = filename.rsplit('.', 1)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValidationError(ext+" is not a valid file extention")


class CheckoutForm(Form):
    card_number = StringField(label=('Card Number:'),
        validators=[validators.DataRequired(), 
        validators.Length(min=16, max=16, message='Card Number must be 16 digits long') ])

class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [
        validators.DataRequired()
        ])

class CreateAccountForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    profile_pic = FileField("Profile Pic", [validateFile])

class EditProfileForm(Form):
    profile_pic = FileField("Profile Pic", [validateFile])


class CheckoutInfoForm(Form):
    first_name = StringField('First Name', [validators.DataRequired()])
    surname = StringField('Surname', [validators.DataRequired()])
    email = StringField('Email Address', [validators.Email()])
    phone_number = IntegerField('Phone(optional)')
    country = SelectField("Country", choices=[(country.alpha_2, country.name) for country in pycountry.countries], validators=[validators.DataRequired()])
    #address = TextAreaField('Address', [validators.DataRequired()])
    address = StringField('Address', [validators.DataRequired()])
    apartment = StringField('Address 2')
    city = StringField('City', [validators.DataRequired()])
    postcode = StringField('Postcode', [validators.Length(min=6, max=7), validators.DataRequired()])


class CheckoutShippingForm(Form):
    shipping_type = RadioField("Shipping Method", choices=[("standard", "£3.99 Standard 4-5 Days"), ("express", "£7.99 Express 1-2 Days")], default="standard")

    
class CheckoutPaymentForm(Form):
    card_number = StringField(label=('Card Number'),
        validators=[validators.DataRequired(), 
        validators.Length(min=16, max=16, message='Card Number must be 16 digits long') ])
    name_on_card = StringField("Name on Card", [validators.DataRequired()])
    #expiry_date = DateField('Expiry Date', format='%Y-%m', default=datetime.now(), validators=[validators.DataRequired()])
    expiry_date = StringField('Expiry Date', validators=[validators.DataRequired()])
    csv = StringField('Security Code', [validators.DataRequired(), validators.Length(min=3, max=3)])


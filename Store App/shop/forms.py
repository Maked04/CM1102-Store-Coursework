from wtforms import Form, BooleanField, PasswordField, StringField, FileField, ValidationError, validators

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

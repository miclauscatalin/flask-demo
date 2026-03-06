# Definesc toate formularele WTForms ale aplicației cu validare și câmpuri CSRF.
# / I define all WTForms forms for the app, with validation and CSRF fields.
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, TextAreaField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Length, EqualTo, Optional, Email


class RegisterForm(FlaskForm):
    # La înregistrare, emailul este obligatoriu pentru 2FA la login
    # / At registration, email is mandatory for 2FA on login
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    email    = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm  = PasswordField("Confirm password", validators=[DataRequired(), EqualTo("password")])
    submit   = SubmitField("Create account")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Login")


class TaskForm(FlaskForm):
    title = StringField("New task", validators=[DataRequired(), Length(max=120)])
    due_at = DateTimeLocalField("Due", format="%Y-%m-%dT%H:%M", validators=[Optional()])
    remind_at = DateTimeLocalField("Remind at", format="%Y-%m-%dT%H:%M", validators=[Optional()])
    remind_email = BooleanField("Email reminder")
    image = FileField("Imagine/Screenshot", validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "gif", "webp"], "Doar imagini!")])
    submit = SubmitField("Add")


class ProfileForm(FlaskForm):
    notification_email = EmailField("Notification Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Save Profile")


class TaskEditForm(FlaskForm):
    title = StringField("Titlu", validators=[DataRequired(), Length(max=120)])
    notes = TextAreaField("Note", validators=[Optional()])
    due_at = DateTimeLocalField("Scadent la", format="%Y-%m-%dT%H:%M", validators=[Optional()])
    remind_at = DateTimeLocalField("Reamintire la", format="%Y-%m-%dT%H:%M", validators=[Optional()])
    remind_email = BooleanField("Email reminder")
    image = FileField("Imagine/Screenshot", validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "gif", "webp"], "Doar imagini!")])
    submit = SubmitField("Salvează")


class SMTPForm(FlaskForm):
    smtp_host = StringField("SMTP Host", validators=[Optional(), Length(max=255)])
    smtp_port = StringField("SMTP Port", validators=[Optional()])
    smtp_username = StringField("SMTP Username (Email)", validators=[Optional(), Length(max=255)])
    smtp_password = StringField("SMTP Password", validators=[Optional(), Length(max=255)])
    sender_email = EmailField("Sender Email", validators=[Optional(), Email()])
    sender_name = StringField("Sender Name", validators=[Optional(), Length(max=80)])
    test_email = EmailField("Test Email", validators=[Optional(), Email()])
    submit = SubmitField("Save SMTP Settings")


class TwoFAForm(FlaskForm):
    # Formular pentru codul de autentificare în doi pași
    # / Form for two-factor authentication code
    code   = StringField("Cod 2FA", validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField("Verifică")


class ForgotPasswordForm(FlaskForm):
    # Formular pentru declanșarea resetării parolei
    # / Form for triggering password reset
    username = StringField("Username", validators=[DataRequired()])
    submit   = SubmitField("Trimite codul")


class ResetPasswordForm(FlaskForm):
    # Formular pentru introducerea codului şi a noii parole
    # / Form for entering the reset code and the new password
    code     = StringField("Cod de resetare", validators=[DataRequired(), Length(min=6, max=6)])
    password = PasswordField("Parolă nouă", validators=[DataRequired(), Length(min=6)])
    confirm  = PasswordField("Confirmă parola", validators=[DataRequired(), EqualTo("password")])
    submit   = SubmitField("Resetează parola")
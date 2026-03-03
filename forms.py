from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Length, EqualTo, Optional, Email


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField("Confirm password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Create account")


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
    submit = SubmitField("Add")


class ProfileForm(FlaskForm):
    notification_email = EmailField("Notification Email", validators=[Optional(), Email()])
    submit = SubmitField("Save Profile")


class SMTPForm(FlaskForm):
    smtp_host = StringField("SMTP Host", validators=[Optional(), Length(max=255)])
    smtp_port = StringField("SMTP Port", validators=[Optional()])
    smtp_username = StringField("SMTP Username (Email)", validators=[Optional(), Length(max=255)])
    smtp_password = StringField("SMTP Password", validators=[Optional(), Length(max=255)])
    sender_email = EmailField("Sender Email", validators=[Optional(), Email()])
    sender_name = StringField("Sender Name", validators=[Optional(), Length(max=80)])
    test_email = EmailField("Test Email", validators=[Optional(), Email()])
    submit = SubmitField("Save SMTP Settings")
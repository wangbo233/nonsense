from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired


class BlogForm(FlaskForm):
    title = StringField("title", validators=[DataRequired()])
    content = TextAreaField("content", validators=[DataRequired()])
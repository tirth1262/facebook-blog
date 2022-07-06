from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed


class PostForm(FlaskForm):
	"""THIS FORM USE TO CREATE A NEW POST """
	title = StringField('Title', validators=[DataRequired()])
	content = TextAreaField('Content', validators=[DataRequired()])
	picture = FileField('Picture', validators=[DataRequired(),FileAllowed(['jpg', 'png'])])
	is_public = BooleanField('Is Public', default=True)
	submit = SubmitField('Post')

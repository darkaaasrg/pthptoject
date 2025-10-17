from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, HiddenField
from wtforms.validators import InputRequired, Length, Email, URL
from flask_wtf.file import FileField, FileAllowed

class LoginForm(FlaskForm):
    username = StringField('Ім\'я користувача', validators=[InputRequired(), Length(min=2, max=64)])
    password = PasswordField('Пароль', validators=[InputRequired()])
    submit = SubmitField('Увійти')


class ProductForm(FlaskForm):
    name = StringField('Назва Продукту', validators=[InputRequired(), Length(max=100)])
    desc = TextAreaField('Опис', validators=[InputRequired()])
    img_file = FileField(
        'Зображення продукту (PNG, JPG)',
        validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Дозволено лише зображення!')]
    )
    submit = SubmitField('Зберегти Продукт')


class CarouselItemForm(FlaskForm):
    title = StringField('Заголовок Слайда', validators=[InputRequired(), Length(max=200)])
    desc = TextAreaField('Опис Слайда', validators=[InputRequired()])

    img_file = FileField(
        'Зображення (PNG, JPG)',
        validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Дозволено лише зображення!')]
    )

    text_position = SelectField(
        'Розміщення Тексту',
        choices=[('center', 'По центру'), ('left', 'Зліва'), ('right', 'Справа')],
        validators=[InputRequired()]
    )
    button_text = StringField('Текст Кнопки', default="")
    button_link = StringField('Посилання Кнопки (URL)',
                              validators=[URL(require_tld=False, message='Введіть коректне посилання (URL)'),
                                          Length(max=200)], default="#")

    submit = SubmitField('Зберегти Слайд')


class SearchForm(FlaskForm):
    q = StringField('Пошук', validators=[Length(max=100)], default="")
    search_submit = SubmitField('Знайти')

    hidden_data = HiddenField()

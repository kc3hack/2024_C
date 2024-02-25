from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, SelectField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Length, Regexp

class LoginForm(FlaskForm):
    username = StringField('Name', validators=[DataRequired(), Length(1, 100)], render_kw={"placeholder" : "Name"}) #User name
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder" : "password"})
    submit = SubmitField('Login', id="button-blue")

class SignUpForm(FlaskForm):
    #ユーザー登録用フォーム
    username = StringField('Name', validators=[DataRequired(), Length(min=1, max=20, message="名前が長すぎます"), Regexp("^\w+$")], render_kw={"placeholder" : "Name"}) #user name
    email = EmailField("Email", validators=[DataRequired()], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder" : "password"})
    submit = SubmitField('Sign Up', id="button-blue")

class AddSpotForm(FlaskForm):
    #隠れスポット追加用フォーム
    spot_name = StringField("スポット名",validators=[DataRequired()])
    latitude = FloatField("緯度", validators=[DataRequired()])
    longitude = FloatField("経度", validators=[DataRequired()])
    spot_place = SelectField("地域", choices=[('0', '京都'), ('1', '大阪'), ('2', '兵庫'), ('3', '滋賀'), ('4', '奈良'), ('5', '和歌山')], validators=[DataRequired()])
    spot_type = SelectField('種類', choices=[('0', '飲食店'), ('1', '場所'), ('2', 'その他')], validators=[DataRequired()])
    spot_overview = StringField("概要", validators=[Length(min=1, max=100, message="概要が長すぎます。"), DataRequired()])
    spot_detail = TextAreaField("詳細", validators=[DataRequired()])
    submit = SubmitField('次へ')

class SignUpWithSpotForm(FlaskForm):
    #隠れスポットの登録とユーザー登録を同時に行う場合のフォーム
    username = StringField('UserName', validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    spot_place = SelectField("地域", choices=[('0', '京都'), ('1', '神戸'), ('2', '大阪'), ('3', 'その他')], validators=[DataRequired()])
    spot_type = SelectField('種類', choices=[('0', '飲食店'), ('1', '場所'), ('2', 'その他')], validators=[DataRequired()])
    spot_name = StringField("店名/場所の名前",validators=[DataRequired()])
    spot_detail = StringField("詳細", validators=[DataRequired()])
    submit = SubmitField('Sign Up')
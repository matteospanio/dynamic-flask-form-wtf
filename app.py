from flask import Flask, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import FieldList
from wtforms import Form as NoCsrfForm
from wtforms.fields import StringField, FormField, SubmitField, SelectField
from wtforms import validators

app = Flask(__name__)
app.config.from_pyfile("app.cfg")
db = SQLAlchemy(app)


# DB MODELS
class Questionario(db.Model):
    __tablename__ = "questionari"
    id = db.Column(db.Integer(), primary_key=True)
    titolo = db.Column(db.String())
    domande = db.relationship('Domanda', backref='domande', lazy='dynamic')


class Domanda(db.Model):
    __tablename__ = 'domande'
    id = db.Column(db.Integer(), primary_key=True)
    testo = db.Column(db.String())
    quiz_id = db.Column(db.Integer(), db.ForeignKey('questionari.id'))


# FORMS
class AddQuestionForm(FlaskForm):
    submit = SubmitField('+')


class DomandaForm(NoCsrfForm):
    testo = StringField('Testo della domanda')


class SelectDomandaForm(DomandaForm):
    selezione = SelectField('Category', choices=[('cat1', 'Category 1'), ('cat2', 'Category 2')])


class QuestionarioForm(FlaskForm):
    titolo = StringField('Titolo')
    domande = FieldList(FormField(DomandaForm, default=lambda: Domanda()), min_entries=1)
    submit = SubmitField('Salva')


from commands import create_tables, populate_db, delete_db
app.cli.add_command(create_tables)
app.cli.add_command(populate_db)
app.cli.add_command(delete_db)


@app.route('/', methods=['GET', 'POST'])
def index():
    questionario = Questionario.query.filter_by(id=1).first()
    main_form = QuestionarioForm(obj=questionario)
    domande = DomandaForm(prefix='domanda-_-')
    # add_question = AddQuestionForm()

    if main_form.submit.data and main_form.validate():
        main_form.populate_obj(questionario)
        db.session.commit()
        flash('modifiche salvate', 'success')

    return render_template('index.html', questionario=questionario,
                           _template=domande, main_form=main_form)


if __name__ == '__main__':
    app.run(debug=True, port=5001)

from flask import Flask, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy.orm import backref
from wtforms import FieldList
from wtforms import Form as NoCsrfForm
from wtforms.fields import StringField, FormField, SubmitField
from wtforms import validators


app = Flask(__name__)
app.config.from_pyfile("app.cfg")
db = SQLAlchemy(app)


# DB models


class Utente(db.Model):
    __tablename__ = "utenti"
    id = db.Column(db.Integer(), primary_key=True)
    nome = db.Column(db.String(64))
    questionari = db.relationship("Questionario")

    def __init__(self, nome):
        self.nome = nome


class Questionario(db.Model):
    __tablename__ = "questionari"
    id = db.Column(db.Integer(), primary_key=True)
    titolo = db.Column(db.String(64))
    user_id = db.Column(db.Integer(), db.ForeignKey("utenti.id"))
    questions = db.relationship(
        "Domanda", backref=db.backref("domande", collection_class=list)
    )

    def __init__(self, titolo, uid):
        self.user_id = uid
        self.titolo = titolo


class Domanda(db.Model):
    __tablename__ = "domande"
    id = db.Column(db.Integer(), primary_key=True)
    testo = db.Column(db.String(256))
    quiz_id = db.Column(db.Integer(), db.ForeignKey("questionari.id"))
    risposte = db.relationship("Risposta")


class Risposta(db.Model):
    __tablename__ = "risposte"
    id = db.Column(db.Integer(), primary_key=True)
    testo = db.Column(db.String(256))
    domanda_id = db.Column(db.Integer(), db.ForeignKey("domande.id"))


# FORMS


class DomandaForm(NoCsrfForm):
    testo = StringField(
        "Title"#validators=[validators.DataRequired("please, enter the question")]
    )


class QuestionarioForm(FlaskForm):
    titolo = StringField("Titolo")
    questions = FieldList(
        FormField(DomandaForm, default=lambda: Domanda()), min_entries=1
    )
    submit = SubmitField("salva")


# ROUTES


@app.route("/", methods=["GET", "POST"])
def index():
    quiz = Questionario.query.filter_by(user_id=1).first()

    if len(quiz.questions) == 0:
        quiz.questions = [Domanda(testo="domanda?")]
        flash("creata domanda", "success")

    form = QuestionarioForm()#obj=quiz)
    domande = DomandaForm(prefix='domanda-_-')

    if form.validate_on_submit():
        print(f"----->[INFO]\n{form.titolo.data}")
        print(form.questions.data)
        print("------------------")
        for elem in form.questions.data:
            print()
            print('---->LIST OUT')
            print(elem)
            # nuova_domanda = Domanda(**elem)
            # quiz.questions.append(nuova_domanda)
        # form.populate_obj(quiz)
        # db.session.commit()
        flash("saved changes", "success")

    return render_template(
        "index.html", form=form, _template=domande, questionario=quiz
    )


@app.route("/delete/<question_id>", methods=["POST"])
def delete(question_id):
    domanda = Domanda.query.filter_by(id=question_id)
    db.session.delete(domanda)
    db.session.commit()
    return redirect(url_for(".index"))


@app.route("/add/<quiz_id>", methods=["POST"])
def add(quiz_id):
    domanda = Domanda(testo="nuova domanda", quizid=quiz_id)
    db.session.add(domanda)
    db.session.commit()
    return redirect(url_for(".index"))


@app.route("/display/<quizid>")
def display(quizid):
    questionario = Questionario.query.filter_by(id=quizid)
    domande = Domanda.query.filter_by(quiz_id=quizid)
    return render_template("view.html", module=questionario, dom=domande)


if __name__ == "__main__":
    db.drop_all()
    db.create_all()
    mat = Utente("Mat")
    db.session.add(mat)
    db.session.commit()
    db.session.add(Questionario("Nuovo questionario", 1))
    db.session.commit()
    app.run(debug=True, port=5003)

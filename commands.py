import click
from flask.cli import with_appcontext
from app import db, Questionario, Domanda


@click.command(name='create_tables')
@with_appcontext
def create_tables():
    """create_tables è un wrapper per la creazione delle tabelle del DB"""
    db.create_all()
    print("Your DB has been created")


@click.command(name='populate_db')
@with_appcontext
def populate_db():
    questionario = Questionario(titolo='Nuovo questionario')
    db.session.add(questionario)
    db.session.commit()
    db.session.add(Domanda(testo='Domanda di default', quiz_id=questionario.id))
    db.session.commit()
    print("Your DB has been populated")


@click.command(name='delete_db')
@with_appcontext
def delete_db():
    """drop all tables of the database"""
    db.drop_all()
    print("DB Deleted")


from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField, HiddenField
from wtforms.validators import DataRequired, NumberRange
import sqlite3

#declare flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

# #declare database -- standard sqlite python
# db = sqlite3.connect("books-collection.db")
# cursor = db.cursor()
# cursor.execute("CREATE TABLE books (id INTEGER PRIMARY KEY, title varchar(250) NOT NULL UNIQUE, author varchar(250) NOT NULL, rating FLOAT NOT NULL)")
# cursor.execute("INSERT INTO books VALUES(1, 'Harry Potter', 'J. K. Rowling', '9.3')")
# cursor.execute("UPDATE books SET rating='0.0' WHERE id = 1")
# db.commit()

#declare database -- flask SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new-books-collection.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.init_app(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=False, nullable=False)
    author = db.Column(db.String(250), unique=False, nullable=False)
    rating = db.Column(db.Float, unique=False, nullable=False)

    def __repr__(self):
        return f'<Book {self.title}>'

#create record
new_book = Book(id=1, title="Slaughterhouse Five", author="Vonnegut, Kurt", rating=10.0)

with app.app_context():
    db.create_all()
    db.session.add(new_book)
    
with app.app_context():
    db.session.commit()

#declare variables
with app.app_context():
    all_books = db.session.query(Book).all()

class AddBookForm(FlaskForm):
    title = StringField('Book Title', validators=[DataRequired()])
    author = StringField('Author Name', validators=[DataRequired()])
    rating = DecimalField('Rating', places=1,validators=[DataRequired(), NumberRange(0,10)])
    submit = SubmitField('Add Book')
    
class EditBookForm(FlaskForm):
    id = HiddenField('id')
    title = StringField('Book Title', validators=[DataRequired()])
    author = StringField('Author Name', validators=[DataRequired()])
    rating = DecimalField('Rating', places=1,validators=[DataRequired(), NumberRange(0,10)])
    submit = SubmitField('Update Book')

def refresh_library():
    global all_books
    with app.app_context():
        all_books = db.session.query(Book).order_by(Book.author, Book.title).all()
        print(all_books)

@app.route('/')
def home():
    refresh_library()
    return render_template("index.html", books=all_books)


@app.route("/add", methods=['GET', 'POST'])
def add():
    form = AddBookForm()
    if form.validate_on_submit():
        #print("True")
        new_book = Book(title=form.title.data, author=form.author.data, rating=float(form.rating.data))
        with app.app_context():
            db.session.add(new_book)
            db.session.commit()
        # book = {'title': form.title.data, 'author': form.author.data, 'rating': float(form.rating.data)}
        # all_books.append(book)
        #print(all_books)
        refresh_library()
        return home()        
    return render_template('add.html', form=form)

@app.route("/edit/<int:id>", methods=['GET', 'POST'])
def edit(id):
    #lookup book
    with app.app_context():
        book = Book.query.get(id)
    form = EditBookForm()
    form.id.data = book.id
    form.title.data = book.title
    form.author.data = book.author
    form.rating.data = book.rating 
    
    if form.validate_on_submit():
        #print("True")
        with app.app_context():
            book = Book.query.get(id)
            book.title = request.form["title"]
            book.author = request.form["author"]
            book.rating = float(request.form["rating"])
            db.session.commit()  
        refresh_library()
        return home()        
    return render_template('edit.html', form=form)

@app.route("/delete/<int:id>")
def delete(id):
    print(id)
    #lookup book
    with app.app_context():
        book = Book.query.get(id)
        
    with app.app_context():
        db.session.delete(book)
        db.session.commit()
        
    refresh_library()
    return home()        

if __name__ == "__main__":
    app.run(debug=True)


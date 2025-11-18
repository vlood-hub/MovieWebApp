from flask import Flask, jsonify, request, render_template, redirect, url_for, abort
from data_manager import DataManager
from models import db, Movie
from api import data_fetcher
from pathlib import Path

app = Flask(__name__)

BASE_DIR = Path(__file__).parent
DB_DIR = BASE_DIR / "data"
DB_FILE = DB_DIR / "movies.db"

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_FILE}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  # Link the database and the app.

data_manager = DataManager()


# ---------- ERROR HANDLING ----------
@app.errorhandler(404)
def page_not_found(error):
    """Render 404 error page."""
    return render_template("404.html", error=error), 404


def is_user(user_id):
    """Check whether the user exists."""
    user = data_manager.get_users(user_id)
    if not user:
        abort(404, description="User not found")

    return user


def is_movie(movie_id):
    """Check whether the movie exists."""
    movie = data_manager.get_movie(movie_id)
    if not movie:
        abort(404, description="Movie not found")

    return movie


# ---------- HOME ROUTE ----------
@app.route('/')
def home():
    """Render the homepage."""
    users = data_manager.get_users()
    return render_template('index.html', users=users)


# ---------- USER ROUTES ----------
@app.route('/users', methods=['POST'])
def add_user():
    """Add a new user"""
    name = request.form.get('name')
    if not name:
        return jsonify({"error": "Name is required"}), 400

    data_manager.create_user(name)
    return redirect(url_for('home'))


@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """Delete a user"""
    is_user(user_id)

    data_manager.delete_user(user_id)
    return redirect(url_for('home'))


# ---------- MOVIE ROUTES ----------
@app.route('/users/<int:user_id>/movies', methods=['GET'])
def get_movies(user_id):
    """Get all movies for a user"""
    user = is_user(user_id)
    movies = data_manager.get_movies(user_id)

    return render_template("user_movies.html", user=user, movies=movies)


@app.route('/users/<int:user_id>/movies/add', methods=['GET', 'POST'])
def add_movie(user_id):
    """Add movie for a specific user."""
    user = is_user(user_id)

    if request.method == 'POST':
        new_title = request.form.get('title')
        comment = request.form.get('comment', '')
        if not new_title:
            return "Title required", 400

        new_title_cap = new_title.title()
        user_movies = data_manager.get_movies(user_id)
        if any(movie.title.lower() == new_title.lower() for movie in user_movies):
            return jsonify({"message": "Movie already exists"}), 400
        else:
            try:
                fetch_movie = data_fetcher.fetch_data(new_title_cap)
            except KeyError:
                return jsonify({"error": "Movie not found"}), 404
            except TypeError:
                pass

        new_movie = Movie(
            title=fetch_movie.get("Title", new_title_cap),
            year=fetch_movie.get("Year", None),
            rating=fetch_movie.get("imdbRating", None),
            poster=fetch_movie.get("Poster", None),
            comment=comment,
            user_id=user_id,
            )
        data_manager.add_movie(new_movie)

        return redirect(url_for('get_movies', user_id=user_id))

    # Handle GET (render add form)
    return render_template('add_movie.html', user=user)


@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """Update movie for a specific user."""
    movie = is_movie(movie_id)

    # Handle POST (save changes)
    if request.method == 'POST':
        new_title = request.form.get('title')
        new_comment = request.form.get('comment')
        data_manager.update_movie(movie_id, new_title, new_comment)

        return redirect(url_for('get_movies', user_id=user_id))

    # Handle GET (show edit page)
    return render_template('update_movie.html', user_id=user_id, movie=movie)


@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(user_id, movie_id):
    """Delete movie for a specific user."""
    is_movie(movie_id)

    data_manager.delete_movie(movie_id)
    return redirect(url_for('get_movies', user_id=user_id))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=5000)
from models import db, User, Movie

class DataManager:

    # ---------- USERS ----------
    def get_users(self, user_id=None):
        """Fetches either all users or a single user by ID."""
        if user_id is not None:
            # Return one user by ID
            return User.query.get(user_id)
        # Otherwise, return all users
        return User.query.all()


    def create_user(self, name):
        """Create a new user."""
        new_user = User(name=name)
        db.session.add(new_user)
        db.session.commit()


    def delete_user(self, user_id):
        """Delete a user and all their movies."""
        user = User.query.get(user_id)

        db.session.delete(user)
        db.session.commit()


    # ---------- MOVIES ----------
    def get_movies(self, user_id):
        """Return all movies for a specific user."""
        return Movie.query.filter_by(user_id=user_id).all()


    def get_movie(self, movie_id):
        """Return a specific movie."""
        return Movie.query.get(movie_id)


    # def add_movie(self, user_id, title, year, rating, poster, comment=None):
    #     """Add a new movie to a user's list."""
    #     user = self.get_users(user_id)

    #     new_movie = Movie(
    #         title=title,
    #         year=year,
    #         rating=rating,
    #         poster=poster,
    #         comment=comment,
    #         user_id=user.id
    #         )

    #     db.session.add(new_movie)
    #     db.session.commit()

    def add_movie(self, new_movie):
        """Add a new movie to database."""
        db.session.add(new_movie)
        db.session.commit()


    def update_movie(self, movie_id, new_title, new_comment):
        """Update movie details."""
        movie = Movie.query.get(movie_id)

        movie.title = new_title
        movie.comment = new_comment
        db.session.commit()


    def delete_movie(self, movie_id):
        """Delete a movie from database."""
        movie = Movie.query.get(movie_id)

        db.session.delete(movie)
        db.session.commit()
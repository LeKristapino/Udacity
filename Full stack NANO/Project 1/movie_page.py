import fresh_tomatoes
import movie

# creating movie instances
inception = movie.Movie("Inception",
                        2010,
                        "http://4.bp.blogspot.com/_ne8uJrqxejc/TAMX7wNvtjI/AAAAAAAAJsg/fDFQ6z94o3Q/s1600/leo-dicaprio-inception-movie-poster-15.png",  # noqa
                        "https://www.youtube.com/watch?v=66TuSJo4dZM")
dark_knight = movie.Movie("The Dark Knight",
                          2008,
                          "http://www.freedesign4.me/wp-content/gallery/posters/free-movie-film-poster-the_dark_knight_movie_poster.jpg",  # noqa

                          "https://www.youtube.com/watch?v=EXeTwQWrcwY")
deal = movie.Movie("Deal",
                   2008,
                   "https://static3.solarmovie.is/images/movies/0446676_big.jpg",  # noqa
                   "https://www.youtube.com/watch?v=zKkmfiGxY5w")
inside_job = movie.Movie("Inside Job",
                         2010,
                         "https://currentconcepts.files.wordpress.com/2011/02/inside_job.jpg",  # noqa
                         "https://www.youtube.com/watch?v=FzrBurlJUNk")
social_network = movie.Movie("The Social Network",
                             2010,
                             "http://www.flickeringmyth.com/wp-content/uploads/2014/11/social-network.jpg",  # noqa
                             "https://www.youtube.com/watch?v=2RB3edZyeYw")
limitless = movie.Movie("Limitless",
                        2012,
                        "http://pencurimovie.pw/wp-content/uploads/2014/02/Limitless-UK-poster.jpg",  # noqa
                        "https://www.youtube.com/watch?v=2GJvgJrW7O8")

# creating movies list
movies = [inception, dark_knight, deal, inside_job, social_network, limitless]

# running website
fresh_tomatoes.open_movies_page(movies)

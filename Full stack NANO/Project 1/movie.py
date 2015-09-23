#class for generating movie instances
class Movie():
    def __init__(self, title, release, poster_url, trailer_url):
        self.title = title
        self.release_date = release
        self.poster_image_url = poster_url
        self.trailer_youtube_url = trailer_url

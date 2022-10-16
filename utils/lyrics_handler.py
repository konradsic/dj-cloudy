import lyricsgenius as glyrics

def initialize_client(access_token):
    client = glyrics.Genius(access_token)
    return client

def get_lyrics(client, author, title):
    song = client.search_song(title=title, artist=author)
    return song.lyrics
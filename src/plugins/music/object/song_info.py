class SongInfo:
    def __init__(self, song_id: int, song_name: str, song_album: str):
        self.sid = song_id
        self.name = song_name
        self.singers = []
        self.album = song_album
        self.url = None

    def __str__(self):
        return f"{self.name}—{','.join(self.singers)}—{self.album}"
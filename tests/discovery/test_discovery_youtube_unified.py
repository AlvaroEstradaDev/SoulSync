import json
from database.music_database import MusicDatabase


def test_youtube_discovery_writes_to_mirrored_playlists(tmp_path):
    db = MusicDatabase(str(tmp_path / "music.db"))

    playlist_id = db.mirror_playlist(
        source="youtube",
        source_playlist_id="abc123hash",
        name="My YT Playlist",
        tracks=[
            {"track_name": "Song A", "artist_name": "Artist A", "source_track_id": "yt1"},
            {"track_name": "Song B", "artist_name": "Artist B", "source_track_id": "yt2"},
        ],
        profile_id=1,
    )
    assert playlist_id is not None

    db_tracks = db.get_mirrored_playlist_tracks(playlist_id)
    assert len(db_tracks) == 2

    db.update_mirrored_playlist_phase(playlist_id, "discovering", discovery_progress=0, discovery_source="spotify")
    playlist = db.get_mirrored_playlist(playlist_id)
    assert playlist["phase"] == "discovering"
    assert playlist["discovery_source"] == "spotify"

    db.update_mirrored_track_extra_data(db_tracks[0]["id"], {
        "discovered": True,
        "provider": "spotify",
        "confidence": 0.95,
        "matched_data": {"id": "sp1", "name": "Song A", "artists": ["Artist A"]},
    })

    db.update_mirrored_playlist_phase(playlist_id, "discovered", discovery_progress=100, discovery_source="spotify")

    playlist = db.get_mirrored_playlist(playlist_id)
    assert playlist["phase"] == "discovered"
    assert playlist["discovery_progress"] == 100

    tracks = db.get_mirrored_playlist_tracks(playlist_id)
    extra = json.loads(tracks[0]["extra_data"]) if isinstance(tracks[0]["extra_data"], str) else tracks[0]["extra_data"]
    assert extra["discovered"] is True
    assert extra["matched_data"]["name"] == "Song A"


def test_mirror_playlist_with_source_id(tmp_path):
    db = MusicDatabase(str(tmp_path / "music.db"))

    playlist_id = db.mirror_playlist(
        source="youtube",
        source_playlist_id="hash1",
        name="YT Playlist",
        tracks=[{"track_name": "Song", "artist_name": "Artist"}],
        profile_id=1,
        source_id="PLreal_yt_id_123",
    )

    playlist = db.get_mirrored_playlist(playlist_id)
    assert playlist["source_id"] == "PLreal_yt_id_123"
    assert playlist["phase"] == "fresh"

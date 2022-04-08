

from WrappedObjects import Config


config = Config(debug=False,
                database='./database.db',
                json_config='./config.json',
                download_dir='./Downloads',
                download_chunk_size=512,
                record_beatmaps=True,
                lookup_beatmaps_in_database=False,
                download_progress_bar_length=20,
                formattable_beatmap_filename="{0[beatmapset_id]} {0[artist]} - {0[title]}")

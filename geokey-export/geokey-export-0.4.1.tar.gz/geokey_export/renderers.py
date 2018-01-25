"""GeoJSON renderer."""

from io import BytesIO
import csv
from rest_framework.renderers import BaseRenderer
from .base import media_keys, comment_keys
from .utils import (
    get_responses,
    get_fields,
    get_mediafiles,
    get_info_comment,
    create_observation_row
)


class CSVRenderer(BaseRenderer):
    """Renderes serialised Contributions into text to be exported as csv."""
    media_type = 'text/csv'
    format = 'csv'

    def render_mediafiles(self, data):
        """Create the csv file all the comments for all the contributions."""
        output = BytesIO()
        writer = csv.writer(output)
        writer.writerow(media_keys)
        for row in data:
            obs_id = row['id']
            if row['media']:
                media = row['media']
                for m in media:
                    writer.writerow(get_mediafiles(obs_id, m, media_keys))
        return output.getvalue()

    def render_comments(self, data):
        """Create the csv file all the comments for all the contributions."""
        output = BytesIO()
        writer = csv.writer(output)
        writer.writerow(comment_keys)

        for row in data:
            obs_id = row['id']
            for comment in row['comments']:
                writer.writerow(get_info_comment(obs_id, comment, comment_keys))
                responses = get_responses(obs_id, comment, len(comment['responses']))
                for response in responses:
                    writer.writerow(response)
        return output.getvalue()

    def render_contribution(self, data):
        """Create the csv file all the contributions."""
        output = BytesIO()
        writer = csv.writer(output)
        keys_obs = get_fields(data)
        writer.writerow(keys_obs)
        for row in data:
            writer.writerow(create_observation_row(row, keys_obs))
        return output.getvalue()

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """Render `data` into serialized html text."""
        rendered = self.render_contribution(data)

        return rendered

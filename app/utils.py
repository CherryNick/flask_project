from flask import request
from app.models import Media
from os import path
from app import app, db
from shortuuid import uuid


def upload_media(form):
    """Upload media and return media id"""
    file = request.files[form.media.name]
    if file:
        filename = f'{uuid()}.jpg'
        media = Media()
        media.make_path(filename)
        file.save(path.join(path.dirname(__file__), media.path[1:]))
        db.session.add(media)
        db.session.commit()
        return media.id
    else:
        return None

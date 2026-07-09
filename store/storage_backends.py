"""
Custom Django storage backend that saves files to Supabase Storage via its
REST API, instead of the local filesystem. Activated by setting
USE_SUPABASE_STORAGE=True (see settings.py) — with that off (the default),
Django uses local disk storage instead and this file isn't used at all.
"""
import mimetypes
import uuid

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


@deconstructible
class SupabaseStorage(Storage):

    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL.rstrip('/')
        self.service_key = settings.SUPABASE_SERVICE_KEY
        self.bucket = settings.SUPABASE_BUCKET

    def _headers(self, content_type=None):
        headers = {
            'Authorization': f'Bearer {self.service_key}',
            'apikey': self.service_key,
        }
        if content_type:
            headers['Content-Type'] = content_type
        return headers

    def _object_url(self, name):
        return f'{self.supabase_url}/storage/v1/object/{self.bucket}/{name}'

    def _public_url(self, name):
        return f'{self.supabase_url}/storage/v1/object/public/{self.bucket}/{name}'

    def _save(self, name, content):
        content.seek(0)
        data = content.read()
        content_type = mimetypes.guess_type(name)[0] or 'application/octet-stream'

        response = requests.post(
            self._object_url(name),
            headers=self._headers(content_type),
            data=data,
        )
        if response.status_code not in (200, 201):
            # Object already exists at this name — overwrite it instead.
            response = requests.put(
                self._object_url(name),
                headers=self._headers(content_type),
                data=data,
            )
            if response.status_code not in (200, 201):
                raise IOError(
                    f'Could not upload "{name}" to Supabase Storage bucket '
                    f'"{self.bucket}": {response.status_code} {response.text}'
                )
        return name

    def _open(self, name, mode='rb'):
        response = requests.get(self._object_url(name), headers=self._headers())
        if response.status_code != 200:
            raise FileNotFoundError(
                f'"{name}" not found in Supabase Storage bucket "{self.bucket}"'
            )
        return ContentFile(response.content, name=name)

    def exists(self, name):
        response = requests.head(self._object_url(name), headers=self._headers())
        return response.status_code == 200

    def delete(self, name):
        try:
            requests.delete(self._object_url(name), headers=self._headers())
        except requests.RequestException:
            pass  # don't crash a product delete just because the photo cleanup failed

    def url(self, name):
        return self._public_url(name)

    def size(self, name):
        response = requests.head(self._object_url(name), headers=self._headers())
        return int(response.headers.get('Content-Length', 0))

    def get_available_name(self, name, max_length=None):
        # product_image_upload_to / site_image_upload_to below already
        # generate a random, collision-proof filename, so there's no need
        # to check/rename here — just use it as-is.
        return name


def product_image_upload_to(instance, filename):
    """Random, collision-proof filename for product photos, e.g. products/ab12cd34....jpg"""
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'jpg'
    return f'products/{uuid.uuid4().hex}.{ext}'


def site_image_upload_to(instance, filename):
    """Random, collision-proof filename for hero/lookbook photos, e.g. site/ab12cd34....jpg"""
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'jpg'
    return f'site/{uuid.uuid4().hex}.{ext}'

# -*- coding: utf-8 -*-

from apiclient import discovery
from apiclient import errors
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2Credentials
import httplib2


class GError(Exception):

    ''' Universal Error class for easy use.
        -----------------------------------

    Catch it what ever you do with Google files, just in case.
    '''
    pass


class GFileBase(object):
    mime_type = None
    file_id = None
    filename = None
    parents = []
    title = None
    description = None

    def __init__(self, item):
        self.__raw = item
        self.file_id = item.get('id', None)
        self.filename = item.get('filename', None)
        self.parents = item.get('parents', [])
        self.title = item.get('title', None)
        self.description = item.get('description', None)

    def get_raw(self):
        return self.__raw

    def __eq__(self, other):
        return self.file_id == other.file_id


class GDoc(GFileBase):
    mime_type = u'application/vnd.google-apps.document'


class GSheet(GFileBase):
    mime_type = u'application/vnd.google-apps.spreadsheet'


class GFolder(GFileBase):
    mime_type = u'application/vnd.google-apps.folder'


class GFile(GFileBase):

    def __init__(self, item):
        super(GFile, self).__init__(item)

        try:
            self.mime_type = item['mimeType']
        except KeyError:
            pass


class GFactory(object):

    def __new__(cls, item):

        try:
            klass = {
                u'application/vnd.google-apps.document': GDoc,
                u'application/vnd.google-apps.spreadsheet': GSheet,
                u'application/vnd.google-apps.folder': GFolder,
            }[item['mimeType']]
            return klass(item)
        except KeyError:
            return GFile(item)


class GDrive(object):

    ''' Google Drive API model class
        ----------------------------

    Use in subclass of generic view, wich is also subclass of OAuthMixin.
    '''

    def __init__(self, request):
        credentials = OAuth2Credentials.from_json(request.session['gdrive_oauth_credentials'])
        http = credentials.authorize(httplib2.Http())
        self.service = discovery.build('drive', 'v2', http=http)

    def filter(self, **kwargs):
        ''' Get list of files (and folders which are files too)
            ---------------------------------------------------

        Works like a Django model .objects.filter(). For more information use:
            https://developers.google.com/drive/v2/reference/files/list
        '''

        if not kwargs:
            kwargs['maxResults'] = 10

        try:
            results = self.service.files().list(**kwargs).execute()

            for item in results.get('items', []):
                yield GFactory(item)

        except errors.HttpError, error:
            raise GError(error)

    def get(self, file_id):
        ''' Get a file from Google Drive
            ----------------------------

        Read more:
            https://developers.google.com/drive/v2/reference/files/get
        '''

        try:
            result = self.service.files().get(fileId=file_id).execute()
            return GFactory(result)
        except errors.HttpError, error:
            raise GError(error)

    def save(self, f):
        ''' Save a file to Google Drive
            ---------------------------

        Works like a Django model .save(). For more information use:
            https://developers.google.com/drive/v2/reference/files/insert
            https://developers.google.com/drive/v2/reference/files/patch
            https://developers.google.com/drive/v2/reference/files/update

        Required arguments of a G<FileType> object:
            title: Title of the file to insert, including the extension
        optional:
            parents: A list of parents folder's ID.
            description: Description of the file to insert.
        '''

        if f.file_id is None:
            return self.__insert(f)
        else:
            return self.__update(f)

    def delete(self, f):
        ''' Delete a file from Google Drive
            -------------------------------

        Reade more:
            https://developers.google.com/drive/v2/reference/files/delete
        '''
        try:
            return self.service.files().delete(fileId=f.file_id).execute()
        except errors.HttpError, error:
            raise GError(error)

    ###################
    # Private methods #
    ###################
    def __insert(self, f):
        ''' Insert new file.
            ----------------

        Returns:
            Inserted file metadata if successful, None otherwise.
        '''
        body = {
            'title': f.title,
            'description': f.description,
            'mimeType': f.mime_type,
            'parents': f.parents,
            'mimeType': f.mime_type
        }

        try:
            insert_file = self.service.files().insert(body=body).execute()
            return GFactory(insert_file)
        except errors.HttpError, error:
            raise GError(error)

    def __update(self, f):
        ''' Update an existing file's metadata and content.
            -----------------------------------------------

        Returns:
          Updated file metadata if successful, None otherwise.
        '''
        body = {
            'title': f.title,
            'description': f.description,
            'mimeType': f.mime_type,
            'parents': f.parents,
            'mimeType': f.mime_type
        }

        try:
            updated_file = self.service.files().update(
                fileId=f.file_id, body=body, newRevision=True).execute()
            return GFactory(updated_file)
        except errors.HttpError, error:
            raise GError(error)

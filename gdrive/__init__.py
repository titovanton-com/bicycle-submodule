# -*- coding: utf-8 -*-

import re
import xml.etree.ElementTree as ET

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

    def __init__(self, gdrive, item):
        self.gdrive = gdrive
        self.__raw = item
        self.id = item.get('id', None)
        self.filename = item.get('filename', None)
        self.parents = item.get('parents', [])
        self.title = item.get('title', None)
        self.description = item.get('description', None)

    def get_raw(self):
        return self.__raw

    def __eq__(self, other):
        return self.id == other.id

    def save(self):
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

        if self.id is None:
            return self.__insert()
        else:
            return self.__update()

    def delete(self):
        ''' Delete a file from Google Drive
            -------------------------------

        Reade more:
            https://developers.google.com/drive/v2/reference/files/delete
        '''
        try:
            return self.gdrive.service.files().delete(fileId=self.id).execute()
        except errors.HttpError, error:
            raise GError(error)

    ###################
    # Private methods #
    ###################
    def __validate(self):
        assert self.title,\
            GError('Required title: title of the file to insert, including the extension')
        assert self.mime_type,\
            GError('Required mime_type: mime type of the file to insert')

    def __insert(self):
        ''' Insert new file.
            ----------------

        Returns:
            Inserted file metadata if successful, None otherwise.
        '''
        self.__validate()
        body = {
            'title': self.title,
            'description': self.description,
            'mimeType': self.mime_type,
            'parents': self.parents,
            'mimeType': self.mime_type
        }

        try:
            insert_file = self.gdrive.service.files().insert(body=body).execute()
            return GFactory(self.gdrive, insert_file)
        except errors.HttpError, error:
            raise GError(error)

    def __update(self):
        ''' Update an existing file's metadata and content.
            -----------------------------------------------

        Returns:
          Updated file metadata if successful, None otherwise.
        '''
        self.__validate()
        body = {
            'title': self.title,
            'description': self.description,
            'mimeType': self.mime_type,
            'parents': self.parents,
            'mimeType': self.mime_type
        }

        try:
            updated_file = self.gdrive.service.files().update(
                fileId=self.id, body=body, newRevision=True).execute()
            return GFactory(self.gdrive, updated_file)
        except errors.HttpError, error:
            raise GError(error)


class GDoc(GFileBase):
    mime_type = u'application/vnd.google-apps.document'


class GWorkSheet(object):

    def __init__(self, updated, title, col_count, row_count, id=None):
        ''' Google Worksheet model '''
        self.updated = updated
        self.title = title
        self.col_count = col_count
        self.row_count = row_count
        self.id = id


class GSheet(GFileBase):
    mime_type = u'application/vnd.google-apps.spreadsheet'
    worksheets = None

    def __init__(self, gdrive, item):
        super(GSheet, self).__init__(gdrive, item)

        if self.id:
            self.worksheets = self.__init_worksheets()

    def __init_worksheets(self):
        ''' Retrieving information about worksheets

        Wotch more:
            https://developers.google.com/google-apps/spreadsheets/
        '''

        url = 'https://spreadsheets.google.com/feeds/worksheets/%s/private/full'
        (resp, content) = self.gdrive.http.request(url % self.id, 'GET')
        self.__raw_worksheets = content
        root = ET.fromstring(content)
        mutches = re.findall(r'xmlns\:?([^=]*?)=("(.+?)"|\'(.+?)\')', content, re.MULTILINE)
        ns = {i[0]: i[2] or i[3] for i in mutches}
        ns['default'] = ns['']

        for entry in root.findall('default:entry', ns):
            id = entry.find('default:id', ns).text.split('/')[-1]
            updated = entry.find('default:updated', ns).text
            title = entry.find('default:title', ns).text
            col_count = entry.find('gs:colCount', ns).text
            row_count = entry.find('gs:rowCount', ns).text
            yield GWorkSheet(updated, title, int(col_count), int(row_count), id=id)

    def add_worksheet(self, title, row_count, col_count):
        body = '''<entry xmlns="http://www.w3.org/2005/Atom"
                xmlns:gs="http://schemas.google.com/spreadsheets/2006">
            <title>%s</title>
            <gs:rowCount>%d</gs:rowCount>
            <gs:colCount>%d</gs:colCount>
        </entry>''' % (title, row_count, col_count)
        url = 'https://spreadsheets.google.com/feeds/worksheets/%s/private/full'
        (resp, content) = self.gdrive.http.request(
            url % self.id, 'POST', body=body, headers={'content-type': 'application/atom+xml'})
        assert False
        root = ET.fromstring(content)
        worksheet_id = root.find('{http://www.w3.org/2005/Atom}id').text.split('/')[-1]
        return content

    def get_raw_worksheets(self):
        return self.__raw_worksheets


class GFolder(GFileBase):
    mime_type = u'application/vnd.google-apps.folder'


class GFile(GFileBase):

    def __init__(self, gdrive, item):
        super(GFile, self).__init__(gdrive, item)

        try:
            self.mime_type = item['mimeType']
        except KeyError:
            pass


class GFactory(object):

    def __new__(cls, gdrive, item):

        try:
            klass = {
                u'application/vnd.google-apps.document': GDoc,
                u'application/vnd.google-apps.spreadsheet': GSheet,
                u'application/vnd.google-apps.folder': GFolder,
            }[item['mimeType']]
            return klass(gdrive, item)
        except KeyError:
            return GFile(gdrive, item)

    def filter(self, gdrive, **kwargs):
        ''' Get list of files (and folders which are files too)
            ---------------------------------------------------

        Works like a Django model .objects.filter(). For more information use:
            https://developers.google.com/drive/v2/reference/files/list
        '''

        if not kwargs:
            kwargs['maxResults'] = 10

        try:
            results = gdrive.service.files().list(**kwargs).execute()

            for item in results.get('items', []):
                yield GFactory(gdrive, item)

        except errors.HttpError, error:
            raise GError(error)

    def get(self, gdrive, id):
        ''' Get a file from Google Drive
            ----------------------------

        Read more:
            https://developers.google.com/drive/v2/reference/files/get
        '''

        try:
            result = gdrive.service.files().get(fileId=id).execute()
            return GFactory(gdrive, result)
        except errors.HttpError, error:
            raise GError(error)


class GDrive(object):

    ''' Google Drive API model class
        ----------------------------

    Use in subclass of generic view, wich is also subclass of OAuthMixin.
    '''

    def __init__(self, request):
        credentials = OAuth2Credentials.from_json(request.session['gdrive_oauth_credentials'])
        self.http = credentials.authorize(httplib2.Http())
        self.service = discovery.build('drive', 'v2', http=self.http)

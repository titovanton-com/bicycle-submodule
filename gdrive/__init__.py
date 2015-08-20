# -*- coding: utf-8 -*-

import re
import xml.etree.ElementTree as ET

from apiclient import discovery
from apiclient import errors
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2Credentials
import httplib2

from django.template import Context
from django.template.loader import get_template

from utils import get_xml_ns


class IdMixin(object):
    __id = None

    def get_id(self):
        return self._id

    def __eq__(self, other):
        return self._id == other.get_id()


class GError(Exception):

    ''' Universal Error class for easy use.
        -----------------------------------

    Catch it what ever you do with Google files, just in case.
    '''
    pass


class GFileBase(IdMixin):
    # TODO: tests with uploading a file
    mime_type = None
    file_mime_type = None
    file_id = None
    filename = None
    convert = False
    parents = []
    title = None
    description = None

    def __init__(self, gdrive, item):
        self.gdrive = gdrive
        self._raw = item
        self._id = item.get('id', None)
        self.filename = item.get('filename', None)
        self.convert = item.get('convert', False)
        self.parents = item.get('parents', [])
        self.title = item.get('title', None)
        self.description = item.get('description', None)

        if self.mime_type is None:
            self.mime_type = item.get('mimeType', None)
            self.file_mime_type = item.get('fileMimeType', None)

    def get_raw(self):
        return self._raw

    def save(self):
        # TODO: tests with uploading a file
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

        if self._id is None:
            return self._insert()
        else:
            return self._update()

    def delete(self):
        ''' Delete a file from Google Drive
            -------------------------------

        Reade more:
            https://developers.google.com/drive/v2/reference/files/delete
        '''
        try:
            return self.gdrive.service.files().delete(fileId=self._id).execute()
        except errors.HttpError, error:
            raise GError(error)

    ###################
    # Private methods #
    ###################
    def _validate(self):
        assert self.title,\
            GError('Required title: title of the file to insert, including the extension')
        assert self.mime_type,\
            GError('Required mime_type: mime type of the file to insert')

    def _insert(self):
        ''' Insert new file.
            ----------------

        Returns:
            Inserted file metadata if successful, None otherwise.
        '''
        self._validate()

        if self.filename is not None:
            media_body = MediaFileUpload(
                self.filename, mimetype=self.file_mime_type, resumable=True)

        body = {
            'title': self.title,
            'description': self.description,
            'mimeType': self.mime_type,
            'parents': self.parents,
        }

        try:
            params = {'body': body}

            if self.filename is not None:
                params['media_body'] = media_body

            insert_file = self.gdrive.service.files().insert(**params).execute()
            return GFactory(self.gdrive, insert_file)
        except errors.HttpError, error:
            raise GError(error)

    def _update(self):
        ''' Update an existing file's metadata and content.
            -----------------------------------------------

        Returns:
          Updated file metadata if successful, None otherwise.
        '''
        self._validate()

        if self.filename is not None:
            media_body = MediaFileUpload(
                self.filename, mimetype=self.file_mime_type, resumable=True)

        body = {
            'title': self.title,
            'description': self.description,
            'mimeType': self.mime_type,
            'parents': self.parents,
        }

        try:
            params = {'body': body, 'fileId': self._id, 'newRevision': True}

            if self.filename is not None:
                params['media_body'] = media_body

            updated_file = self.gdrive.service.files().update(**params).execute()
            return GFactory(self.gdrive, updated_file)
        except errors.HttpError, error:
            raise GError(error)


class GDoc(GFileBase):
    mime_type = u'application/vnd.google-apps.document'


class GWorkSheet(IdMixin):
    # TODO: Delete the worksheet
    # TODO: update_multiple_cells tests
    _file = None

    def __init__(self, f, item):
        ''' Google Worksheet model '''

        self._file = f
        self.title = item['title']
        self.col_count = item['col_count']
        self.row_count = item['row_count']
        self._id = item.get('id', None)

    def __eq__(self, other):
        return self._id == other.id

    def save(self):
        ''' Attach to a file and upload to a Google Drive this worksheet
            ----------------------------------------------------------

        Required:
            title, col_count, row_count.

        Returns:
            nothing!
        TODO:
            Update does not works
        '''

        for w in self._file.get_worksheets():

            if w != self and w.title == self.title:
                raise GError('The worksheet with given title is already exists.')

        if self._id is None:
            body = get_template('gdrive/insert_worksheet.xml').render(Context({'obj': self}))
            url = 'https://spreadsheets.google.com/feeds/worksheets/%s/private/full'

            (resp, content) = self._file.gdrive.http.request(
                url % self._file._id, 'POST', body=body,
                headers={'content-type': 'application/atom+xml'})

            root = ET.fromstring(content)
            mutches = re.findall(r'xmlns\:?([^=]*?)=("(.+?)"|\'(.+?)\')', content, re.MULTILINE)
            ns = {i[0]: i[2] or i[3] for i in mutches}
            ns['default'] = ns['']
            self._id = root.find('default:id', ns).text.split('/')[-1]

            if self._id:
                w_list = self._file.get_worksheets()
                w_list += [self]
            else:
                raise GError('Worksheet attaching error.')

        else:
            body = get_template('gdrive/update_worksheet.xml').render(Context({'obj': self}))
            url = 'https://spreadsheets.google.com/feeds/worksheets/%s/private/full/%s/version'

            (resp, content) = self._file.gdrive.http.request(
                url % (self._file._id, self._id), 'PUT', body=body,
                headers={'content-type': 'application/atom+xml'})

            return content

    def retrieve_cells(self):
        # TODO: make good

        url = 'https://spreadsheets.google.com/feeds/cells/%s/%s/private/full'

        (resp, content) = self._file.gdrive.http.request(
            url % (self._file._id, self._id), 'GET')

        return content

    def update_multiple_cells(self, cells):
        ''' Update batch of rows using R1C1 notation

        Cells is a dicts, for example:
            {'R1C1': 'title', 'R1C2': 'count', 'R2C1': 'apples', 'R2C2': 10}

        TODO: tests
        '''

        if self._id is not None:
            content = self.retrieve_cells()
            ns = get_xml_ns(content)
            ET.register_namespace('', ns['default'])
            root = ET.fromstring(content)
            edit_links = {}

            for entry in root.findall('default:entry', ns):
                cell_id = entry.find('default:id', ns).text.split('/')[-1]
                edit_links[cell_id] = ET.tostring(entry.find('default:link[@rel=\'edit\']', ns))

            body = get_template('gdrive/update_multiple_cells.xml').render(
                Context({'obj': self, 'cells': cells, 'links': edit_links}))
            url = 'https://spreadsheets.google.com/feeds/cells/%s/%s/private/full/batch'

            (resp, content) = self._file.gdrive.http.request(
                url % (self._file._id, self._id), 'POST', body=body,
                headers={'content-type': 'application/atom+xml'})

            # checking for errors
            # ns = get_xml_ns(content)
            # root = ET.fromstring(content)

            # for entry in root.findall('atom:entry', ns):
            #     title = entry.find('atom:title', ns).text

            #     if title == 'Error':
            #         cell_id = entry.find('atom:id', ns).text.split('/')[-1]
            #         c = entry.find('atom:title', ns).text
            #         raise GError()

            return content

    def get_id(self):
        return self._id

    def get_file_id(self):
        return self._file._id


class GSheet(GFileBase):
    mime_type = u'application/vnd.google-apps.spreadsheet'
    _worksheets = None

    def __init__(self, gdrive, item):
        super(GSheet, self).__init__(gdrive, item)

    def get_worksheets(self):
        ''' Lazy retrieving all worksheets for file with id
            -----------------------------------------------

        Returns:
            None or list of GWorkSheet objects

        Wotch more:
            https://developers.google.com/google-apps/spreadsheets/
        '''

        if self._id and self._worksheets is None:
            url = 'https://spreadsheets.google.com/feeds/worksheets/%s/private/full'
            (resp, content) = self.gdrive.http.request(url % self._id, 'GET')
            root = ET.fromstring(content)
            ns = get_xml_ns(content)
            self._worksheets = []

            for entry in root.findall('default:entry', ns):
                id = entry.find('default:id', ns).text.split('/')[-1]
                updated = entry.find('default:updated', ns).text
                title = entry.find('default:title', ns).text
                col_count = entry.find('gs:colCount', ns).text
                row_count = entry.find('gs:rowCount', ns).text
                item = {
                    'updated': updated,
                    'title': title,
                    'col_count': int(col_count),
                    'row_count': int(row_count),
                    'id': id,
                }
                w = GWorkSheet(self, item)
                self._worksheets += [w]

        return self._worksheets


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

    @classmethod
    def get(cls, gdrive, id):
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

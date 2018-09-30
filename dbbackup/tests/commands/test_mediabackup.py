"""
Tests for mediabackup command.
"""
import os
import tempfile
from django.test import TestCase
from django.core.files.storage import get_storage_class
from dbbackup.management.commands.mediabackup import Command as DbbackupCommand
from dbbackup.storage import get_storage
from dbbackup.tests.utils import DEV_NULL, HANDLED_FILES, add_public_gpg


class MediabackupBackupMediafilesTest(TestCase):
    def setUp(self):
        HANDLED_FILES.clean()
        self.command = DbbackupCommand()
        self.command.servername = 'foo-server'
        self.command.storage = get_storage()
        self.command.stdout = DEV_NULL
        self.command.compress = False
        self.command.encrypt = False
        self.command.path = None
        self.command.media_storage = get_storage_class()()
        self.command.time = None

    def tearDown(self):
        if self.command.path is not None:
            try:
                os.remove(self.command.path)
            except OSError:
                pass

    def test_func(self):
        self.command.backup_mediafiles()
        self.assertEqual(1, len(HANDLED_FILES['written_files']))

    def test_compress(self):
        self.command.compress = True
        self.command.backup_mediafiles()
        self.assertEqual(1, len(HANDLED_FILES['written_files']))
        self.assertTrue(HANDLED_FILES['written_files'][0][0].endswith('.gz'))

    def test_encrypt(self):
        self.command.encrypt = True
        add_public_gpg()
        self.command.backup_mediafiles()
        self.assertEqual(1, len(HANDLED_FILES['written_files']))
        outputfile = HANDLED_FILES['written_files'][0][1]
        outputfile.seek(0)
        self.assertTrue(outputfile.read().startswith(b'-----BEGIN PGP MESSAGE-----'))

    def test_compress_and_encrypt(self):
        self.command.compress = True
        self.command.encrypt = True
        add_public_gpg()
        self.command.backup_mediafiles()
        self.assertEqual(1, len(HANDLED_FILES['written_files']))
        outputfile = HANDLED_FILES['written_files'][0][1]
        outputfile.seek(0)
        self.assertTrue(outputfile.read().startswith(b'-----BEGIN PGP MESSAGE-----'))

    def test_write_local_file(self):
        self.command.path = tempfile.mktemp()
        self.command.backup_mediafiles()
        self.assertTrue(os.path.exists(self.command.path))
        self.assertEqual(0, len(HANDLED_FILES['written_files']))

    def test_time(self):
        self.command.time = "2000-01-01 000000"
        self.command.backup_media_files()
        self.assertEqual(1, len(HANDLED_FILES['written_files']))
        self.assertTrue(self.command.time in HANDLED_FILES['written_files'][0][0])

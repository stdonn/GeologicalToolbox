# -*- coding: UTF-8 -*-
"""
This is a test module for the Resources.Geometries.Line class using unittest
"""

import tempfile
import unittest
import uuid

from pathlib import Path
from GeologicalToolbox.DBHandler import DBHandler


class TestDBMigrationClass(unittest.TestCase):
    """
    This class tests the alembic database migration functionality
    """

    def setUp(self):
        # type: () -> None
        """
        set parameters

        :return: None
        """

        db_file = str(uuid.uuid4())
        tmp_path = Path(tempfile.gettempdir())
        if tmp_path.exists() and not tmp_path.is_dir():
            raise AssertionError("temporary path exists, but is not a directory: {}".format(str(tmp_path)))
        elif not tmp_path.exists():
            tmp_path.mkdir(parents=True, exist_ok=True)
        self.db = "sqlite:///{}.data".format(str(tmp_path.joinpath(db_file)))

    def test_migration(self):
        # type: () -> None
        """
        Test the database migration itself

        :return: Nothing
        :raises AssertionError: Raises AssertionError if a test fails
        """
        handler = DBHandler(self.db, test=True)

        self.assertFalse(handler.check_current_head())
        handler.start_db_migration()
        self.assertTrue(handler.check_current_head())

        handler.close_last_session()

    def tearDown(self):
        # type: () -> None
        """
        remove temporary database
        :return: Nothing
        """
        p = Path(self.db)
        if p.exists():
            p.unlink()


if __name__ == '__main__':
    unittest.main()

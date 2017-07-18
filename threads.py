# -*- coding:utf-8 -*-

from threading import Thread
from __init__ import db
from DCP_data import DCP_data
from multiprocessing import Pool
from tdcpblib.tdcpb_checks import tdcpb_check
from tdcpblib.common import TdcpbException
from shutil import copytree
import os


PATH_STORAGE = "storage"

class Copy(Thread):
    def __init__(self, id_dcp, hashcheck_when_finished=True):
        Thread.__init__(self)
        self.id_dcp = id_dcp
        self.storage_dir = PATH_STORAGE
        self.hashcheck_when_finished = hashcheck_when_finished

    def run(self):
        dcp = db.session.query(DCP_data).filter_by(id=self.id_dcp).first()
        hash_check = None
        try:
            dcp.copy_result = "Copy in progress"
            db.session.commit()

            # Copy DCP
            target_dir = os.path.join(self.storage_dir,os.path.basename(dcp.source_directory))
            copytree(dcp.source_directory,target_dir)

            dcp.copy_result = "OK"
            dcp.target_directory = target_dir
            db.session.commit()
            if self.hashcheck_when_finished:
                hash_check = HashCheck(self.id_dcp)

        except OSError as e:
            dcp.copy_result = "Fail"
            dcp.copy_err = " ".join([e.message, e.filename, e.strerror])
            db.session.commit()


        # Start the long check of the copy
        if hash_check:
            hash_check.start()



class Check(Thread):
    def __init__(self, id_dcp, copy_when_finished=True):
        Thread.__init__(self)
        self.id_dcp = id_dcp
        self.copy_when_finished = copy_when_finished

    def run(self):
        dcp = db.session.query(DCP_data).filter_by(id=self.id_dcp).first()
        copy = None
        try:
            dcp.chack_result = "Check in progress"
            db.session.commit()

            # Short check of DCP in source directory
            tdcpb_check(dcp.source_directory)

            dcp.check_result = "OK"
            db.session.commit()

            if self.copy_when_finished:
                copy = Copy(self.id_dcp)

        except Exception as e:
            dcp.check_result = "Fail"
            dcp.check_err = " ".join([e.message, e.filename, e.strerror])
            db.session.commit()

        # Start copying the DCP
        if copy:
            copy.start()

class HashCheck(Thread):
    def __init__(self, id_dcp):
        Thread.__init__(self)
        self.id_dcp = id_dcp

    def run(self):
        dcp = db.session.query(DCP_data).filter_by(id=self.id_dcp).first()

        try:
            dcp.check_hash_result = "Hash check in progress"
            db.session.commit()

            # Long check of DCP in target directory
            tdcpb_check(dcp.target_directory,u"long")

            dcp.check_hash_result = "OK"
            db.session.commit()

        except Exception as e:
            dcp.check_hash_result = "Fail"
            dcp.check_hash_err = " ".join([e.message, e.filename, e.strerror])
            db.session.commit()
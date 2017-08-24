# -*- coding:utf-8 -*-

from threading import Thread
from __init__ import db, logger
from DCP_data import DCP_data
import subprocess as SP
from tdcpblib.tdcpb_checks import tdcpb_check
from tdcpblib.common import TdcpbException
from tdcpblib.di_parser import DiParser, DiError
from shutil import copytree
import os

PATH_STORAGE = u"/Donnees/storage"
PATH_TORRENTS = u"Donnees/torrents"
COMMENT = u""


class Copy(Thread):
    def __init__(self, id_dcp, hashcheck_when_finished=True):
        Thread.__init__(self)
        self.id_dcp = id_dcp
        self.storage_dir = PATH_STORAGE
        self.hashcheck_when_finished = hashcheck_when_finished

    def run(self):
        dcp = db.session.query(DCP_data).filter_by(id=self.id_dcp).first()
        hash_check = None
        dcp.copy_result = u"Copy in progress"
        db.session.commit()
        logger.info(u"Copy started for {}".format(dcp.dcp_name))

        source_path = os.path.join(dcp.source_directory, dcp.dcp_name)
        target_path = os.path.join(self.storage_dir, dcp.dcp_name)

        try:
            # Copy DCP
            copytree(source_path,target_path)
        except OSError as e:
            dcp.copy_result = u"Fail"
            _msg = u" ".join([e.message, e.filename, e.strerror])
            dcp.copy_err = _msg
            db.session.commit()
            logger.error(u"Copy KO for {}, {}".format(dcp.dcp_name, _msg))
        else:
            dcp.copy_result = u"OK"
            dcp.target_directory = self.storage_dir
            dcp.copy_err = None
            db.session.commit()
            logger.info(u"Copy OK for {}".format(dcp.dcp_name))

            if self.hashcheck_when_finished:
                hash_check = HashCheck(self.id_dcp)



        # Start the long check of the copy
        if hash_check:
            hash_check.start()


class Check(Thread):
    def __init__(self, id_dcp, copy_when_finished=True):
        Thread.__init__(self)
        self.id_dcp = id_dcp
        self.unexpected_files = None
        self.copy_when_finished = copy_when_finished

    def run(self):
        dcp = db.session.query(DCP_data).filter_by(id=self.id_dcp).first()
        copy = None
        dcp.check_result = u"Check in progress"
        db.session.commit()
        dcp_path = os.path.join(dcp.source_directory,dcp.dcp_name)
        logger.info(u"Dir check started for {}".format(dcp.dcp_name))

        try:
            # Short check of DCP in source directory
            d = DiParser(dcp.get_s_dcp_path(), logger)
            res = d.check_files()
        except DiError as e:
            dcp.check_result = u"Fail"
            if e.value.startswith(u"Not a DCP folder:"):
                _msg = u"Dir {} does not exist".format(dcp.get_s_dcp_path())
                logger.error(_msg)
                dcp.check_err = _msg
            else:
                logger.error(e.value)
                dcp.check_err = e.value
            db.session.commit()
        except Exception as e:
            dcp.check_result = u"Fail"
            logger.error(e.message)
            dcp.check_err = e.message
            db.session.commit()
        else:
            if res == u"KO":
                dcp.check_result = u"Fail"
                dcp.check_err = d.error
                db.session.commit()
            else:
                dcp.check_result = u"OK"
                if d.unexpected_files:
                    self.unexpected_files = d.unexpected_files
                    dcp.check_warning = u"Unexpected files were found : {}".format(", ".join(*self.unexpected_files))
                else:
                    self.unexpected_files = None
                    dcp.check_warning = None
                dcp.check_err = None
                db.session.commit()
                logger.info(u"Dir check OK for {}".format(dcp.dcp_name))

            if self.copy_when_finished:
                copy = Copy(self.id_dcp)

        # Start copying the DCP
        if copy:
            copy.start()


class HashCheck(Thread):
    def __init__(self, id_dcp, torrent_when_finished=True):
        Thread.__init__(self)
        self.id_dcp = id_dcp
        self.torrent_when_finished = torrent_when_finished

    def run(self):
        dcp = db.session.query(DCP_data).filter_by(id=self.id_dcp).first()
        create_torrent = None
        dcp.check_hash_result = u"Hash check in progress"
        db.session.commit()
        logger.info(u"Hash check started for {}".format(dcp.dcp_name))

        dcp_path = os.path.join(dcp.source_directory,dcp.dcp_name)

        try:
            # Long check of DCP in target directory
            d = DiParser(dcp.get_t_dcp_path(), logger)
            res = d.check_hash()

        except Exception as e:
            dcp.check_hash_result = u"Fail"
            dcp.check_hash_err = e.message
            db.session.commit()
            logger.error(e.message)
        else:
            if res == u"KO":
                dcp.check_hash_result = u"Fail"
                dcp.check_hash_err = d.error
                db.session.commit()
            else:
                dcp.check_hash_result = u"OK"
                dcp.check_hash_err = None
                db.session.commit()
                logger.info(u"Hash check OK for {}".format(dcp.dcp_name))
            if self.torrent_when_finished:
                create_torrent = CreateTorrent(self.id_dcp)

        if create_torrent:
            create_torrent.start()



class CreateTorrent(Thread):
    def __init__(self, id_dcp):
        Thread.__init__(self)
        self.id_dcp = id_dcp
        self.comment = COMMENT

    def run(self):
        dcp = db.session.query(DCP_data).filter_by(id=self.id_dcp).first()
        dcp.torrent_result = u"Torrent creation in progress"
        db.session.commit()
        logger.info(u"Torrent creation started for {}".format(dcp.dcp_name))

        path_torrent = os.path.join(PATH_TORRENTS, dcp.dcp_name) + ".torrent"

        if dcp.target_directory:
            cmd = [u"/usr/bin/transmission-create",u"-p",u"-o",path_torrent,u"-c",self.comment, os.path.join(dcp.target_directory,dcp.dcp_name)]
            _stdout, _stderr = None, None
            try:
                sp = SP.Popen(cmd,stdout=SP.PIPE,stderr=SP.PIPE)
                sp.wait()
                _stdout, _stderr = sp.communicate()
            except Exception as e:
                dcp.torrent_result = u"Fail"
                if _stderr:
                    _msg = u" ".join([e.message, _stderr])
                    dcp.torrent_err = _msg
                    logger.error(_msg)
                else:
                    dcp.torrent_err = e.message
                    logger.error(e.message)
                db.session.commit()

            else:
                dcp.torrent_result = u"OK"
                dcp.torrent_err = None
                db.session.commit()
                logger.info(u"Torrent creation OK for {}".format(dcp.dcp_name))
        else:
            dcp.torrent_result = u"Fail"
            dcp.torrent_err = u"No target directory for DCP " + dcp.dcp_name
            db.session.commit()

class DcpProcessesException(Exception):
    def __init__(self, type, message=None):
        Exception.__init__(self, message)
        self.type = type

class StatsThread(Thread):
    def __init__(self, type, *args):
        Thread.__init__(self)
        self.type = type
        self.args = args
    def check_stats(self, checker):
        pass
    def copy_stats(self, source, target):
        total_size = os.path.getsize(source)
        current_size = os.path.getsize(target)
        while current_size < total_size:
            pass



    def run(self):
        if type==u"check":
            self.check_stats(self.args[0])
        elif type==u"copy":
            self.copy_stats()

class DcpProcessesManager():
    def __init__(self,id_dcp):
        self.id_dcp = id_dcp
        self.checker = Check(id_dcp, False)
        self.copier = Copy(id_dcp, False)
        self.hashchecker = HashCheck(id_dcp, False)
        self.torrentcreator = CreateTorrent(id_dcp)

    def start_check(self):
        dcp = db.session.query(DCP_data).filter_by(id=self.id_dcp).first()
        if not os.path.exists(dcp.get_s_dcp_path()):
            raise DcpProcessesException(u"No existing source", u"Dir " + dcp.get_s_dcp_path() + u"doesn't exist")

        self.checker.start()
        stats = StatsThread(u"check", self.checker)
        stats.start()

        return stats

    def start_copy(self):
        dcp = db.session.query(DCP_data).filter_by(id=self.id_dcp).first()
        if (dcp.check_result!=u"OK"):
            raise DcpProcessesException(u"Check not completed", u"DCP " + dcp.dcp_name + u" is not checked")

        self.copier.start()
        stats = StatsThread(u"copy", dcp.get_s_dcp_path(), dcp.get_t_dcp_path())
        stats.start()

        return stats
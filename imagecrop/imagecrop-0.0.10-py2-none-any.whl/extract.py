# -*- coding: utf-8 -*-

"""
Created on 2017-12-04


Image extraction using a template. Uses homography and feature matching,
and stores results in a db for faster reprocessing. Usage:

from imagecrop.extract import Extracter
ex = Extracter()
ex.crop_images(image_directory, crop_template, file_extension)

Crops are extracted to a directory named successful_crops directly underneath
image_directory

"""
from __future__ import unicode_literals

__author__ = u'Stephan Hügel'
__version__ = '0.0.10'

import os
import sys
import hashlib
import glob
import logging
import shutil

import numpy as np

import cv2
from cv2 import imread as cv_imread

if sys.version_info[0] == 2:
    import pathlib2 as pathlib
else:
    import pathlib


from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import Column, Integer, String, Unicode, Boolean, Float, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy import and_
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker, scoped_session, relationship

# these imports are for custom SQL constructs
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import DateTime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError

# create a custom utcnow function


class utcnow(expression.FunctionElement):
    type = DateTime()


@compiles(utcnow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


@compiles(utcnow, 'sqlite')
def sqlite_utcnow(element, compiler, **kw):
    return "CURRENT_TIMESTAMP"


class AppMixin(object):
    """
    Provide common attributes to our models
    In this case, lowercase table names, timestamp, and a primary key column
    """

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    __mapper_args__ = {'always_refresh': True}

    id = Column(Integer, primary_key=True)
    # the correct function is automatically selected based on the dialect
    timestamp = Column(DateTime, server_default=utcnow())

Base = declarative_base()
logging.basicConfig()


class Directory(Base, AppMixin):
    """ The full path to the directory in which the image extraction has been run """
    fullpath = Column(String(250, convert_unicode=True), nullable=False, unique=True)
    pprocessed = relationship("Processed", back_populates="path")

    def __repr__(self):
        return "%s, %s files processed" % (self.fullpath, len(self.pprocessed))


class Pt_Assoc(Base):
    """ Unique combinations of a Processed file and a Template """
    __tablename__ = 'pt_assoc'
    template_id = Column('template_id', Integer, ForeignKey(
        'template.id'), primary_key=True)
    processed_id = Column('processed_id', Integer, ForeignKey(
        'processed.id'), primary_key=True)
    # was an image successfully extracted?
    success = Column(Boolean, nullable=False, index=True)
    template = relationship("Template", back_populates="processed")
    processed = relationship(
        "Processed", back_populates="templates", single_parent=True)

    def __repr__(self):
        return "Template: %s, success? %s" % (self.template, self.success)


class Processed(Base, AppMixin):
    """ A processed image. MD5 is the file MD5, not filename MD5 """
    # the file name without a path
    fname = Column(String(250, convert_unicode=True), nullable=False, unique=True)
    md5 = Column(String(32), nullable=False, unique=True)
    path_id = Column(Integer, ForeignKey('directory.id'))
    path = relationship(
        "Directory", back_populates="pprocessed", uselist=False)
    templates = relationship("Pt_Assoc", back_populates="processed",
                             cascade="save-update, merge, delete, delete-orphan")

    @property
    def fullpath(self):
        return os.path.join(self.path.fullpath, self.fname)

    def __init__(self, fname, fullpath):
        self.fname = fname
        self.md5 = md5(os.path.join(fullpath, fname))
        self.path = create_or_get_path(fullpath)

    def __repr__(self):
        return "%s, templates: %s" % (self.fname, self.templates)


class Template(Base, AppMixin):
    fname = Column(String(250, convert_unicode=True), nullable=False, unique=True)
    md5 = Column(String(32), nullable=False, unique=True)
    processed = relationship(
        "Pt_Assoc", back_populates="template", order_by="Pt_Assoc.success")

    def __init__(self, fname, fullpath):
        self.fname = fname
        self.md5 = md5(os.path.join(fullpath, fname))

    def __repr__(self):
        return "%s (%s)" % (self.fname, self.md5)


def sync(bs, db_path):
    """
    Connect to the DB, return a scoped session factory
    """
    # first, bind to or create the db
    pth = 'sqlite:///%s/image_crop.db' % db_path
    engine = create_engine(pth)
    # create the tables by syncing metadata from the models
    # bs is a declarative_base instance
    bs.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
    return Session


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def create_or_get_path(path):
    session = Session()
    obj = session.query(Directory).filter(
        Directory.fullpath == path).one_or_none()
    if not obj:
        obj = Directory(fullpath=path)
        session.add(obj)
        session.commit()
    session.close()
    return obj


def create_or_get_file(fname, fpath, sess):
    # We already know the file and template combination don't exist
    fl = sess.query(Processed).filter(Processed.md5 == md5(
        os.path.join(fpath, fname))).one_or_none()
    if not fl:
        fl = Processed(fname, fpath)
    return fl


def create_or_get_template(tname, tpath, sess):
    tmp = sess.query(Template).filter(Template.md5 == md5(
        os.path.join(tpath, tname))).one_or_none()
    if not tmp:
        tmp = Template(tname, tpath)
    return tmp


def crop_coords(dst):
    """
    Return coords in correct order for cropping
    we want:
    top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]

    Input is the output from a perspectiveTransform, whose input
    is output[0] from a findHomography call

    """
    x, y = [], []
    for contour_line in [np.int32(dst)]:
        for contour in contour_line:
            x.append(contour[0][0])
            y.append(contour[0][1])
    x1, x2, y1, y2 = min(x), max(x), min(y), max(y)
    return x1, x2, y1, y2

# these will be available to Extracter.__init__
Session = sync(Base, os.path.expanduser('~'))


class Extracter(object):
    """ Image extraction instance. Look at the crop_images and list_crops methods for details. """

    def __init__(self):
        self.session = Session()
        super(Extracter, self).__init__()

    def __add_file(self, fname, fullpath, success, tname, tpath):
        """ Add a file, template, and success combination """
        try:
            with self.session.no_autoflush:
                processed = create_or_get_file(fname, fullpath, self.session)
                assoc = Pt_Assoc(success=success)
                tmp = create_or_get_template(tname, tpath, self.session)
                assoc.template = tmp
                processed.templates.append(assoc)
                self.session.add_all([processed, assoc])
            self.session.flush()
        except FlushError:
            # The Processed / Template combination exists already, so update it
            self.session.rollback()
            with self.session.no_autoflush:
                assoc = self.session.query(Pt_Assoc)\
                    .filter(and_(
                        Pt_Assoc.processed_id == processed.id,
                        Pt_Assoc.template_id == tmp.id))\
                    .one()
                assoc.success = success
                assoc.template = tmp
                processed.templates.append(assoc)
                self.session.add_all([processed, assoc])
        self.session.commit()

    def __match_with_template(self, template, candidate, num_points=10):
        """ Extract a region of interest using homography and feature matching """
        # get absolute file path
        file_path = os.path.abspath(candidate)
        # extract image name
        file_name = os.path.basename(candidate)
        # remove extension
        file_name_noext = os.path.splitext(file_name)[0]
        # extract full path without filename
        path_nofile = os.path.split(os.path.abspath(file_path))[:-1][0]

        # work out the same for templates
        template_path = os.path.abspath(template)
        template_name = os.path.basename(template)
        template_name_noext = os.path.splitext(template_name)[0]
        template_path_nofile = os.path.split(
            os.path.abspath(template_path))[:-1][0]

        # construct output dir
        output_dir = os.path.join(
            path_nofile, "successful_crops", md5(template_path))
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # find SIFT features
        MIN_MATCH_COUNT = num_points

        img1 = cv2.imread(template, 0)  # queryImage (the template)
        img2 = cv2.imread(candidate, 1)  # trainImage (image to crop)

        template_width = img1.shape[1]

        # Initiate SIFT detector
        sift = cv2.xfeatures2d.SIFT_create()
        # find the keypoints and descriptors with SIFT
        kp1, des1 = sift.detectAndCompute(img1, None)
        kp2, des2 = sift.detectAndCompute(img2, None)

        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)

        flann = cv2.FlannBasedMatcher(index_params, search_params)

        matches = flann.knnMatch(des1, des2, k=2)

        # store all the good matches as per Lowe's ratio test.
        good = []
        for m, n in matches:
            if m.distance < 0.7 * n.distance:
                good.append(m)
        if len(good) > MIN_MATCH_COUNT:
            src_pts = np.float32(
                [kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
            dst_pts = np.float32(
                [kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            matchesMask = mask.ravel().tolist()

            h, w = img1.shape
            pts = np.float32(
                [[0, 0], [0, h-1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
            dst = cv2.perspectiveTransform(pts, M)

            # this is the region we want to extract
            x1, x2, y1, y2 = crop_coords(dst)

            # print("Crop width: ", x2 - x1)
            # print ("Crop height: ", y2 - y1)

            if (x2 - x1 <= 0) or (y2 - y1<= 0):
                success = False
            elif (x2 - x1) < template_width:
                success = False
            else:
                crop_img = img2[y1:y2, x1:x2]
                cv2.imwrite(os.path.join(output_dir, "%s_crop.png" %
                                         file_name_noext), crop_img)
                success = True
        else:
            success = False
            matchesMask = None
        # finally, add processed file to DB
        self.__add_file(file_name, path_nofile, success,
                        template_name, template_path_nofile)

    def crop_images(self, path, template, extension, match_points=30, reprocess=False):
        """
        Try to extract image crops from files in the given path using the given template and extension.

        Usage:
        ex = Extracter()
        ex.crop_images("images", "template.jpg", "jpg")
        if reprocess=True, only un-cropped templates for the given input directory are considered
        """
        # get list of all globbed filenames and their md5
        pth = os.path.abspath(path)
        filenames = glob.glob(u"%s/*.%s" % (pth, extension))
        hashes = [md5(filename) for filename in filenames]
        # filter: check whether file MD5s are in the db,
        # returning those that have been successfully processed using the
        # template
        if not reprocess:
            subset = set([
                pr.fullpath for pr in
                self.session.query(Processed)
                .join(Pt_Assoc)
                .join(Template)
                .filter(and_(
                    Processed.md5.in_(hashes),
                    Pt_Assoc.success == True,
                    Template.md5 == md5(template)
                ))
                .all()
            ])
            # subtract subset from original list
            to_process = list(set(filenames) - subset)
        else:
            to_process = set([
                pr.fullpath for pr in
                self.session.query(Processed)
                .join(Pt_Assoc)
                .join(Template)
                .filter(and_(
                    Processed.md5.in_(hashes),
                    Pt_Assoc.success == False,
                ))
                .all()
            ])
        length = len(to_process)
        if not length:
            print("All files in this directory have already been processed.")
        else:
            print("Processing %s file(s) in this directory." % length)
            for img in to_process:
                self.__match_with_template(template, img, num_points=match_points)
            # show a summary
            db_template = self.session.query(Template).filter(Template.md5 == md5(template)).one()
            print("Template %s summary:" % db_template.md5)
            self.__status(db_template, pth)

    def summary(self, path):
        """ List all classified files, templates, and classification status per template for a given path """
        # deal with trailing slashes
        pth = os.path.abspath(path)
        classified = self.session.query(Directory).filter(
            Directory.fullpath == pth).one_or_none()
        if not classified:
            print("This directory has not yet been processed")
        else:
            total_crops = self.session.query(Pt_Assoc)\
                .join(Processed)\
                .join(Directory)\
                .filter(and_(
                    Pt_Assoc.success == True,
                    Directory.fullpath == pth))\
                .count()

            print("Summary:\n%s files were processed, generating %s cropped images." % (
                len(classified.pprocessed), total_crops))

            num_templates = self.session.query(Template)\
                .join(Pt_Assoc)\
                .join(Processed)\
                .filter(Directory.fullpath == pth)\
                .all()

            print("%s templates were used to try to extract cropped test images:" % len(
                num_templates))

            for (i, tmp) in enumerate(num_templates):
                print("\n\tTemplate %s: %s" % (i + 1, tmp))
                # for each template, get its files for that path
                # (true / false, total)
                self.__status(tmp, pth)

    def __status(self, tmp, pth):
        """ For a given template and path, show crop status of each file in that path """
        summaries = self.session.query(Pt_Assoc.success, func.count(Pt_Assoc.success))\
            .filter(and_(
                Pt_Assoc.template_id == tmp.id,
                Directory.fullpath == pth))\
            .group_by(Pt_Assoc.success).all()
        for summary in summaries:
            print("\tCrop extracted: {} ({} files)".format(
                summary[0], summary[1]))
            # only list files with unsuccessful crops
            if not summary[0]:
                per_category = self.session.query(Processed)\
                    .join(Pt_Assoc)\
                    .filter(and_(
                        Pt_Assoc.template_id == tmp.id,
                        Pt_Assoc.success == summary[0],
                        Directory.fullpath == pth))\
                    .all()

                for fl in per_category:
                    print("\t\t%s" % fl.fname)

    def delete(self, path, template_md5=None):
        """ Delete cropped images for a given directory and optional template combination """
        pth = os.path.abspath(path)
        crops_dir = os.path.join(pth, "successful_crops")
        # logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
        # select all association rows matching the given path and template
        # criteria
        tpc = self.session.query(Pt_Assoc)\
            .join(Processed)\
            .filter(Directory.fullpath == pth)
        if template_md5:
            tpc = tpc\
                .join(Template)\
                .filter(Template.md5 == template_md5)
        template_path_crops = tpc.all()
        # Just to make sure nobody accidentally deletes random directories
        if len(template_path_crops):
            tmp_md5 = template_md5 or ''
            print("Deleting %s cropped images." % len(template_path_crops))
            shutil.rmtree(os.path.join(crops_dir, tmp_md5))
            # delete entries from DB
            for crop in template_path_crops:
                crop.processed.templates.remove(crop)
            self.session.commit()
            # clean up after ourselves, deleting the crops dir if empty
            try:
                if not set(os.listdir(crops_dir)) - set([u'.DS_Store']):
                    shutil.rmtree(crops_dir)
            except OSError:
                # we already cleaned up this dir because delete was called with
                # no template
                pass
        else:
            print("No crops were found for that template and directory combination.")

    def __exit__(self):
        self.session.close()
        Session.remove()

# -*- coding: utf-8 -*-

"""
SJC Transfer Prototype
~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2017-2018 by San Jacinto College
:license: unspecificed

This file contains the object models to allow the application to communicate
with the database.

"""


import os
from sqlalchemy import Column, Integer, String, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

_ROOT = os.path.abspath(os.path.dirname(__file__))

def _get_data(path):
    return os.path.join(_ROOT,path)

def db_connect():
    """Create db session with SQLite database.

    Used primary for debugging purposes.
    """
    engine = create_engine(f'sqlite:///{_get_data("transfer_experiment.db")}')

    Base.metadata.create_all(engine)
    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    return DBSession()

class University(Base):
    __tablename__ = "university"

    id = Column(Integer, primary_key=True)
    name = Column(String(250),nullable=False)

course_programs = Table(
    'course_programs', 
    Base.metadata, 
    Column('program_id', ForeignKey('program.id'), primary_key=True),
    Column('course_id', ForeignKey('course.id'), primary_key=True)
    )

programs_sjc_courses = Table(
    'programs_sjc_courses', 
    Base.metadata, 
    Column('program_id', ForeignKey('program.id'), primary_key=True),
    Column('sjc_course_id', ForeignKey('SJC.id'), primary_key=True)
    )

components_programs = Table(
    'components_programs', 
    Base.metadata, 
    Column('program_id', ForeignKey('program.id'), primary_key=True),
    Column('component_id', ForeignKey('component.id'), primary_key=True)
    )

components_courses = Table(
    'components_courses',
    Base.metadata,
    Column('course_id', ForeignKey('course.id'), primary_key=True),
    Column('component_id', ForeignKey('component.id'), primary_key=True)
)

requirements_courses = Table(
    'requirements_courses',
    Base.metadata,
    Column('course_id', ForeignKey('course.id'), primary_key=True),
    Column('requirement_id', ForeignKey('requirement.id'), primary_key=True)
)

requirements_programs = Table(
    'requirements_programs',
    Base.metadata,
    Column('program_id', ForeignKey('program.id'), primary_key=True),
    Column('requirement_id', ForeignKey('requirement.id'), primary_key=True)
)

components_requirements = Table(
    'components_requirements',
    Base.metadata,
    Column('component_id', ForeignKey('component.id'), primary_key=True),
    Column('requirement_id', ForeignKey('requirement.id'), primary_key=True)
)


class Course(Base):
    __tablename__ = "course"

    id = Column(Integer, primary_key=True)
    univ_id = Column(Integer, ForeignKey('university.id'))
    name = Column(String(250),nullable=False)
    rubric = Column(String(250),nullable=False)
    number = Column(String(250),nullable=False)
    hours = Column(Integer, nullable=True)
    acgm = Column(Boolean, nullable=True)
    acgm_id = Column(Integer, ForeignKey('ACGM.id'))
    sjc = Column(Boolean, nullable=True)
    sjc_id = Column(Integer, ForeignKey('SJC.id'))
    super_id = Column(Integer, ForeignKey('course.id'))
    university = relationship("University", back_populates="courses")
    programs = relationship(
        "Program", 
        secondary=course_programs,
        back_populates="courses",
        collection_class=ordering_list('name'))
    components = relationship(
        "Component", 
        secondary=components_courses,
        back_populates="courses")
    requirements = relationship(
        "Requirement",
        secondary=requirements_courses,
        back_populates="courses"
    )
    prerequisites = relationship("Course",post_update=True)


University.courses = relationship("Course", order_by=Course.id, back_populates="university")

class Program(Base):
    __tablename__ = "program"

    id = Column(Integer, primary_key=True)
    univ_id = Column(Integer, ForeignKey('university.id'))
    name = Column(String(250),nullable=False)
    link = Column(String(250),nullable=True)
    courses = relationship(
        "Course", 
        secondary=course_programs, 
        back_populates="programs")

    components = relationship(
        "Component", 
        secondary=components_programs,
        back_populates="programs"
        )

    requirements = relationship(
        "Requirement",
        secondary=requirements_programs,
        back_populates="programs"
    )
    sjc_courses = relationship(
        "SJC", 
        secondary=programs_sjc_courses, 
        back_populates="programs")

class Component(Base):
    __tablename__ = "component"

    id = Column(Integer, primary_key=True)
    univ_id = Column(Integer, ForeignKey('university.id'))
    prog_id = Column(Integer, ForeignKey('program.id'))
    name = Column(String(250), nullable=False)
    courses = relationship(
        "Course", 
        secondary=components_courses, 
        back_populates="components")
    programs = relationship(
        "Program",
        secondary=components_programs,
        back_populates="components")
    requirements = relationship(
        "Requirement",
        secondary=components_requirements,
        back_populates="components"
    )

class Requirement(Base):
    __tablename__ = "requirement"

    id = Column(Integer, primary_key=True)
    univ_id = Column(Integer, ForeignKey('university.id'))
    name = Column(String(250), nullable=False)
    comp_id = Column(Integer, ForeignKey('component.id'))
    courses = relationship(
        "Course",
        secondary=requirements_courses,
        back_populates="requirements"
    )
    programs = relationship(
        "Program",
        secondary=requirements_programs,
        back_populates="requirements"
    )
    components = relationship(
        "Component",
        secondary=components_requirements,
        back_populates="requirements"
    )

class ACGM(Base):
    __tablename__ = "ACGM"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    rubric = Column(String(250), nullable=False)
    number = Column(String(250), nullable=False)
    hours = Column(Integer, nullable=True)
    UHCL_id = Column(Integer, ForeignKey('course.id'))
    SJC_id = Column(Integer, ForeignKey('SJC.id'))

class SJC(Base):
    __tablename__ = "SJC"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    rubric = Column(String(250), nullable=False)
    number = Column(String(250), nullable=False)
    hours = Column(Integer, nullable=True)
    UHCL_id = Column(Integer, ForeignKey('course.id'))
    ACGM_id = Column(Integer, ForeignKey('ACGM.id'))

    programs = relationship(
        "Program", 
        secondary=programs_sjc_courses,
        back_populates="sjc_courses"
        )
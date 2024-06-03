#!/usr/bin/python

from wtforms import Form, BooleanField, StringField, IntegerField, SelectField
from wtforms import DecimalField, DateField, DateTimeField, validators
from model import Model


class PersonForm(Form):
    formname = "Create a new person"
    lastname = StringField('Lastname', [validators.Length(min=2, max=25)])
    firstname = StringField('Firstname', [validators.Length(min=2, max=25)])
    address = StringField('Address', [validators.Length(min=6, max=100)])
    phone = StringField('Phone', [validators.Length(min=6, max=14)])


class CurriculumForm(Form):
    formname = "Create a new curriculum"
    name = StringField('Name', [validators.Length(min=2, max=25)])
    secretary = SelectField('Secretary', coerce=int, choices=[])
    director = SelectField('Directory', coerce=int, choices=[])

    def setNames(self):
        with Model() as model:
            l = [(p[0], p[1] + " " + p[2]) for p in model.listPersons()]
            self.secretary.choices = l
            self.director.choices = l


class CourseForm(Form):
    formname = "Create a new course"
    teacher = SelectField('Teacher', coerce=int, choices=[])
    name = StringField('Name of the course',
                       [validators.Length(min=2, max=25)])
    
    def setNames(self):
        with Model() as model:
            l = [(p[0], p[1] + " " + p[2]) for p in model.listPersons()]
            self.teacher.choices = l


class SelectStudentForm(Form):
    formname = "Register a student into a curriculum"
    student = SelectField('Student', coerce=int, choices=[])

    def setNames(self):
        with Model() as model:
            l = [(p[0], p[1] + " " + p[2]) for p in model.listPersons()]
            self.student.choices = l


class SelectCourseForm(Form):
    formname = "Register a course into a curriculum"
    course = SelectField('Course', coerce=int, choices=[])
    ects = IntegerField('ECTS')

    def setNames(self):
        with Model() as model:
            l = [(p[0], p[1] + " by " + p[3] + " " + p[4])
                 for p in model.listCourses()]
            self.course.choices = l


class ValidationForm(Form):
    formname = "Create a new validation for a course"
    name = StringField('Name of the examination',
                       [validators.Length(min=2, max=25)])
    coef = IntegerField('Coeficient of the examination in the course')
    date = DateField('Date of the examination')


class GradesForm(Form):
    formname = "Add a new grade"
    student = SelectField('Student', coerce=int, choices=[])
    grade = DecimalField('Grade')

    def setNames(self, idCourse):
        with Model() as model:
            l = [(p[0], p[1] + " " + p[2])
                 for p in model.listStudentsOfCourse(idCourse)]
            self.student.choices = l

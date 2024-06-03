#!/usr/bin/python

from model import Model
from flask import *
from forms import *
from sqlite3 import IntegrityError
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


################################################################
####              HANDLING OF PERSONS                       ####
################################################################


@app.route('/person/', methods=['GET', 'POST'])
def showPersons():
    with Model() as model:
        form = PersonForm(request.form)
        if request.method == 'POST' and form.validate():
            model.createPerson(form.lastname.data, form.firstname.data,
                               form.address.data, form.phone.data)

        pers = model.listPersons()
        keys = [
            '', 'Lastname', 'Firstname', 'Address', 'Phone', '#Curriculums',
            'Details', 'Delete'
        ]
        return render_template(
            'listing.html',
            to_list=[(pers, keys, "Persons")],
            title='Persons',
            forms=[form])


@app.route('/person/del/<id>/')
def delPerson(id=None):
    with Model() as model:
        model.deletePerson(id)
        return redirect(url_for('showPersons'))


@app.route('/person/<id>/', methods=['GET', 'POST'])
def showPerson(id=None):
    with Model() as model:
        exams = model.listValidationsOfStudent(id)
        curri = model.listCurriculumsOfStudent(id)
        keys_exams = [
            '', 'Date', 'Curriculum', 'Course', 'Validation', 'Grade'
        ]
        keys_curri = ['Curriculum Name', 'Grade']
        return render_template(
            'listing.html',
            to_list=[
                (curri, keys_curri, "Summary of " + model.getNameOfPerson(id)),
                (exams, keys_exams,
                 "Detailed grades of student " + model.getNameOfPerson(id))
            ],
            title='Person ' + model.getNameOfPerson(id))


################################################################
####              HANDLING OF CURRICULUMS                   ####
################################################################


@app.route('/curriculum/', methods=['GET', 'POST'])
def showCurriculums():
    with Model() as model:
        form = CurriculumForm(request.form)
        form.setNames()
        if request.method == 'POST' and form.validate():
            model.createCurriculum(form.name.data, form.secretary.data,
                                   form.director.data)
        pers = model.listCurriculums()
        keys = [
            '', 'Name', 'Director Lastname', 'Firstname', 'Secretary Lastname',
            'Firstname', 'Details', 'Delete'
        ]
        return render_template(
            'listing.html',
            to_list=[(pers, keys, "Curriculums")],
            title='Curriculums',
            forms=[form])


@app.route('/curriculum/del/<id>/')
def delCurriculum(id=None):
    with Model() as model:
        model.deleteCurriculum(id)
        return redirect(url_for('showCurriculums'))


@app.route('/curriculum/<id>/', methods=['GET', 'POST'])
def showCurriculum(id=None):
    with Model() as model:
        addStudentForm = SelectStudentForm(request.form)
        addStudentForm.setNames()
        addCourseForm = SelectCourseForm(request.form)
        addCourseForm.setNames()
        if request.method == 'POST':
            if addStudentForm.validate():
                model.registerPersonToCurriculum(addStudentForm.student.data,
                                                 id)
            else:
                if addCourseForm.validate():
                    model.registerCourseToCurriculum(addCourseForm.course.data,
                                                     id,
                                                     addCourseForm.ects.data)
                    addStudentForm = SelectStudentForm()
                    addStudentForm.setNames()
        avg = model.averageGradesOfStudentsInCurriculum(id)
        cou = model.listCoursesOfCurriculum(id)
        keys_avg = ['Lastname', 'Firstname', 'totalGrade']
        keys_cou = [
            '', 'Name', 'Teacher Lastname', 'Teacher Firstname', 'ECTS',
            'Delete'
        ]
        return render_template(
            'listing.html',
            to_list=[
                (avg, keys_avg, "Averaged grades of curriculum " +
                 model.getNameOfCurriculum(id)),
                (cou, keys_cou,
                 "Courses of curriculum " + model.getNameOfCurriculum(id)),
            ],
            title='Curriculum ' + model.getNameOfCurriculum(id),
            forms=[addStudentForm, addCourseForm])


@app.route('/curriculum/<idCurr>/del/<idCou>/')
def delCourseFromCurriculum(idCurr=None, idCou=None):
    with Model() as model:
        model.deleteCourseFromCurriculum(idCou, idCurr)
        return redirect(url_for('showCurriculum', id=idCurr))


################################################################
####              HANDLING OF COURSES                       ####
################################################################


@app.route('/course/', methods=['GET', 'POST'])
def showCourses():
    with Model() as model:
        addCourseForm = CourseForm(request.form)
        addCourseForm.setNames()
        if request.method == 'POST' and addCourseForm.validate():
            model.createCourse(addCourseForm.name.data,
                               addCourseForm.teacher.data)
        pers = model.listCourses()
        keys = [
            '', 'Name', '', 'Teacher lastname', 'Teacher firstname', 'Details',
            'Delete'
        ]
        return render_template(
            'listing.html',
            to_list=[(pers, keys, "Courses")],
            title='Courses',
            forms=[addCourseForm])


@app.route('/course/del/<id>/')
def delCourse(id=None):
    with Model() as model:
        model.deleteCourse(id)
        return redirect(url_for('showCourses'))


@app.route('/course/<id>/', methods=['GET', 'POST'])
def showCourse(id=None):
    with Model() as model:
        form = ValidationForm(request.form)
        if request.method == 'POST' and form.validate():
            model.addValidationToCourse(form.name.data, form.coef.data, form.date.data, id)
        exams = model.listValidationsOfCourse(id)
        grades = model.listGradesOfCourse(id)
        curri = model.listCurriculumsOfCourse(id)
        students = model.listStudentsOfCourse(id)
        keys_grades = [
            '', 'Date', 'Curriculum', 'Student lastname', 'Student firstname',
            'Validation', 'Grade', 'Coef'
        ]
        keys_exams = ['', 'Date', 'Name', 'Coef', 'Details']
        keys_curri = ['', 'Curriculum', 'ECTS']
        keys_students = ['', 'Lastname', 'Firstname']
        return render_template(
            'listing.html',
            to_list=[(curri, keys_curri,
                      "Curriculums of course " + model.getNameOfCourse(id)),
                     (exams, keys_exams,
                      "List of exams for course " + model.getNameOfCourse(id)),
                     (grades, keys_grades,
                      "Grades of course " + model.getNameOfCourse(id)),
                     (students, keys_students,
                      "Students of course " + model.getNameOfCourse(id))],
            forms=[form])


@app.route('/course/<idCourse>/<idValidation>/', methods=['GET', 'POST'])
def showValidation(idCourse=None, idValidation=None):
    with Model() as model:
        form = GradesForm(request.form)
        form.setNames(idCourse)
        if request.method == 'POST' and form.validate():
            try:
                model.addGrade(idValidation, form.student.data,
                               str(form.grade.data))
            except IntegrityError:
                form.errors['student'] = ([
                    "This student already has a grade!"
                ])

        grades = model.listGradesOfValidation(idValidation)
        keys_grades = ['Grade', 'Firstname', 'Lastname']
        return render_template(
            'listing.html',
            to_list=[(grades, keys_grades,
                      "Grades of " + model.getNameOfValidation(idValidation))],
            forms=[form])


if __name__ == '__main__':
    app.run(debug=True)

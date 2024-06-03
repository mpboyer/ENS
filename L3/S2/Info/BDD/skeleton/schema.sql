CREATE TABLE IF NOT EXISTS Persons(
	id SERIAL PRIMARY KEY , 
	fname TEXT NOT NULL,
	lname TEXT NOT NULL,
	address TEXT NOT NULL, 
	phone_number CHAR(10));

-- Pour l'instant, numéros américains ou français uniquement, mais pas les deux.  

CREATE TABLE IF NOT EXISTS Curriculums(
	id SERIAL PRIMARY KEY ,
	name TEXT UNIQUE NOT NULL, 
	secretary INTEGER REFERENCES Persons(id) ON DELETE CASCADE,
	director INTEGER REFERENCES Persons(id) ON DELETE CASCADE);

CREATE TABLE IF NOT EXISTS Courses(
	id SERIAL PRIMARY KEY, 
	name TEXT UNIQUE NOT NULL,
	teacher INTEGER NOT NULL REFERENCES Persons(id) ON DELETE CASCADE);


CREATE TABLE IF NOT EXISTS Validations(
	id SERIAL PRIMARY KEY ,
	class INTEGER NOT NULL REFERENCES Courses(id) ON DELETE CASCADE,
	name TEXT NOT NULL, 
	time DATE NOT NULL,
	coefficient INTEGER NOT NULL);

CREATE TABLE IF NOT EXISTS Credits(
	curriculum INTEGER REFERENCES Curriculums(id), 
	class INTEGER REFERENCES Courses(id),
	credits INTEGER, 
	unique(curriculum, class));

CREATE TABLE IF NOT EXISTS Grades(
	id SERIAL PRIMARY KEY, 
	validation INTEGER REFERENCES Validations(id) ON DELETE CASCADE, 
	student INTEGER REFERENCES Persons(id) ON DELETE CASCADE, 
	grade INTEGER CHECK (grade <= 100),
	unique(validation, student));

CREATE TABLE IF NOT EXISTS Programs(
	curriculum INTEGER REFERENCES Curriculums(id) ON DELETE CASCADE, 
	student INTEGER REFERENCES Persons(id) ON DELETE CASCADE, 
	unique(curriculum, student));


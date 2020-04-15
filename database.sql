CREATE TABLE employee(
username varchar(30) primary key,
password varchar(30),
name varchar(30),
email varchar(30)
); 

CREATE TABLE person_availability(
employee varchar(30),
day varchar(30),
time varchar(30),
foreign key (employee) references employee(username)
); 

CREATE TABLE admin(
username varchar(30) primary key,
password varchar(30),
name varchar(30),
email varchar(30)
);

CREATE TABLE shift(
permanent int,
shift_id int auto_increment primary key,
day varchar(30),
time varchar(30),
employee varchar(30),
foreign key (employee) references employee(username)
);

CREATE TABLE coverage(
request int,
covered int,
req_employee varchar(30),
cover_employee varchar(30),
shift int,
Foreign key(shift) references shift(shift_id),
Foreign key (req_employee) references employee(username),
Foreign key (cover_employee) references employee(username)
);

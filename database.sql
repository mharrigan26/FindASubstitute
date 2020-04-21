CREATE TABLE employee1(
username varchar(50) primary key,
password varchar(60),
name varchar(30),
email varchar(30)
); 

drop table if exists person_availability;
CREATE TABLE person_availability(
employee varchar(50),
day varchar(30),
time varchar(30),
foreign key (employee) references employee1(username)
); 

drop table if exists admin;
CREATE TABLE admin(
username varchar(50) primary key,
password varchar(60),
name varchar(30),
email varchar(30)
);


CREATE TABLE shift1(
permanent int,
shift_id int auto_increment primary key,
day varchar(30),
time varchar(30),
employee varchar(50),
foreign key (employee) references employee1(username)
);



drop table if exists coverage;
CREATE TABLE coverage(
request_id int auto_increment primary key,
covered int,
req_employee varchar(50),
cover_employee varchar(50),
shift int,
Foreign key(shift) references shift1(shift_id),
Foreign key (req_employee) references employee1(username),
Foreign key (cover_employee) references employee1(username)
);




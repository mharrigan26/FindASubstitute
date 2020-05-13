/* 
    FindASubstitute
    Bianca Pio, Alexandra Bullen-Smith, Margaret Harrigan
    CS 304 Final Project
    Submitted May 13, 2020

    insert_statements.sql has functions to input new data into the database
*/

Insert into shift1(permanent, day, time,employee) values (1, 'Monday', '5:00pm', 'bpio');
Insert into shift1(permanent, day, time,employee) values (1, 'Monday', '8:00am', 'wwellesley');

Insert into coverage(covered, req_employee, shift) values (0, 'bpio', 1);
Insert into coverage(covered, req_employee, shift) values (0, 'wwellesley', 2);

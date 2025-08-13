USE ClubStack;

INSERT INTO Member (ID, FirstName, LastName, GraduationYear, IsGradStudent, ActivationDate, CarPlate, CarState, CarPassCount, EmerContactName, EmerContactPhone) VALUES 
(10, 'Daniel', 'S', 2027, FALSE, '2025-01-01', NULL, NULL, 0, 'Jane', '555-1234');
INSERT INTO Member (ID, FirstName, LastName, GraduationYear, IsGradStudent, ActivationDate, CarPlate, CarState, CarPassCount, EmerContactName, EmerContactPhone) VALUES 
(11, 'Jonah', 'L', 2026, FALSE, '2025-01-01', NULL, NULL, 0, 'Bob', '555-1224');
INSERT INTO Member (ID, FirstName, LastName, GraduationYear, IsGradStudent, ActivationDate, CarPlate, CarState, CarPassCount, EmerContactName, EmerContactPhone) VALUES 
(12, 'Jacob', 'O', 2029, FALSE, '2025-01-01', NULL, NULL, 0, 'Josh', '555-1234');
INSERT INTO Member (ID, FirstName, LastName, GraduationYear, IsGradStudent, ActivationDate, CarPlate, CarState, CarPassCount, EmerContactName, EmerContactPhone) VALUES 
(13, 'Chance', 'B', 2027, FALSE, '2025-01-01', NULL, NULL, 0, 'Juha', '555-1234');

INSERT INTO Address (Member, Nickname, Line1, Line2, State, Zip) VALUES 
(10, 'Home', '123 Main St', NULL, 'CA', '90210');

INSERT INTO MemberPermissions (Permission, Member) VALUES (5, 10);
INSERT INTO MemberPermissions (Permission, Member) VALUES (28, 13);
INSERT INTO MemberPermissions (Permission, Member) VALUES (29, 12);
INSERT INTO MemberPermissions (Permission, Member) VALUES (30, 11);

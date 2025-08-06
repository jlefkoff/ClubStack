DROP DATABASE IF EXISTS ClubStack;
CREATE DATABASE ClubStack;
USE ClubStack;

-- General Membership
CREATE TABLE Member (
    ID INT PRIMARY KEY,
    FirstName VARCHAR(255) NOT NULL,
    LastName VARCHAR(255) NOT NULL,
    PreferredName VARCHAR(255),
    GraduationYear INT,
    IsGradStudent BOOLEAN NOT NULL DEFAULT FALSE,
    ActivationDate DATE,
    CarPlate VARCHAR(20),
    CarState VARCHAR(20),
    CarPassCount INT,
    EmerContactName VARCHAR(255) NOT NULL,
    EmerContactPhone VARCHAR(20) NOT NULL
);

CREATE TABLE Address (
    ID INT PRIMARY KEY,
    Member INT,
    Nickname VARCHAR(255),
    Line1 VARCHAR(255),
    Line2 VARCHAR(255),
    State VARCHAR(50),
    Zip VARCHAR(10),
    FOREIGN KEY (Member) REFERENCES Member(ID)
);

CREATE TABLE Allergy (
    ID INT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL
);

CREATE TABLE AllergyUsers (
    UserID INT,
    AllergyID INT,
    PRIMARY KEY (UserID, AllergyID),
    FOREIGN KEY (UserID) REFERENCES Member(ID),
    FOREIGN KEY (AllergyID) REFERENCES Allergy(ID)
);

CREATE TABLE Permission (
    ID INT PRIMARY KEY,
    Title VARCHAR(255) NOT NULL,
    PageAccess TEXT -- TODO: decide how this works
);

CREATE TABLE MemberPermissions (
    Permission INT,
    Member INT,
    PRIMARY KEY (Permission, Member),
    FOREIGN KEY (Permission) REFERENCES Permission(ID),
    FOREIGN KEY (Member) REFERENCES Member(ID)
);

CREATE TABLE Feedback (
    ID INT PRIMARY KEY,
    Member INT NOT NULL, -- Submitter
    Rating INT NOT NULL,
    Description TEXT,
    Anonymous BOOLEAN,
    FOREIGN KEY (Member) REFERENCES Member(ID)
);

-- Events
CREATE TABLE Event (
    ID INT PRIMARY KEY,
    Author INT,
    PartySize INT,
    MaxSize INT,
    EventLoc VARCHAR(255),
    Randomized BOOLEAN,
    Name VARCHAR(255),
    Description TEXT,
    MeetLoc VARCHAR(255),
    LeadOrg VARCHAR(255),
    EventType VARCHAR(255),
    RecItems TEXT,
    Picture TEXT,
    FOREIGN KEY (Author) REFERENCES Member(ID)
);

CREATE TABLE RSVP (
    ID INT PRIMARY KEY,
    Event INT NOT NULL,
    CanBringCar BOOLEAN NOT NULL DEFAULT FALSE,
    AvailStart DATETIME NOT NULL,
    AvailEnd DATETIME NOT NULL,
    FOREIGN KEY (Event) REFERENCES Event(ID)
);

CREATE TABLE EventRoster (
    ID INT PRIMARY KEY,
    Event INT NOT NULL,
    Member INT NOT NULL,
    DateRegistered DATETIME DEFAULT CURRENT_TIMESTAMP,
    Waitlisted BOOLEAN,
    FOREIGN KEY (Event) REFERENCES Event(ID),
    FOREIGN KEY (Member) REFERENCES Member(ID)
);

-- Comms
CREATE TABLE Communication (
    ID INT PRIMARY KEY,
    Subject VARCHAR(255) NOT NULL,
    Content TEXT NOT NULL,
    DateSent DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE CommunicationRecipients (
    Communication INT,
    Member INT,
    PRIMARY KEY (Communication, Member),
    FOREIGN KEY (Communication) REFERENCES Communication(ID),
    FOREIGN KEY (Member) REFERENCES Member(ID)
);

-- Voting
CREATE TABLE Term (
    ID INT PRIMARY KEY,
    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL,
    Name VARCHAR(255) NOT NULL
);

CREATE TABLE Position (
    ID INT PRIMARY KEY,
    Title VARCHAR(255),
    BallotOrder INT
);

CREATE TABLE Nomination (
    ID INT PRIMARY KEY,
    Nominator INT,
    Nominee INT,
    `Position` INT,
    Accepted BOOLEAN,
    FOREIGN KEY (Nominator) REFERENCES Member(ID),
    FOREIGN KEY (Nominee) REFERENCES Member(ID),
    FOREIGN KEY (Position) REFERENCES `Position`(ID)
);

CREATE TABLE Election (
    ID INT PRIMARY KEY,
    Date DATE NOT NULL,
    Term INT,
    NominateBy DATE NOT NULL,
    FOREIGN KEY (Term) REFERENCES Term(ID)
);

CREATE TABLE ElectionPositions (
    `Position` INT,
    Election INT,
    PRIMARY KEY (Position, Election),
    FOREIGN KEY (Position) REFERENCES `Position`(ID),
    FOREIGN KEY (Election) REFERENCES Election(ID)
);

CREATE TABLE Ballot (
    ID INT PRIMARY KEY,
    `Position` INT,
    Election INT,
    CreatedAt DATETIME NOT NULL,
    FOREIGN KEY (Position) REFERENCES `Position`(ID),
    FOREIGN KEY (Election) REFERENCES Election(ID)
);

CREATE TABLE Winner (
    ID INT PRIMARY KEY,
    Member INT,
    `Position` INT,
    FOREIGN KEY (Member) REFERENCES Member(ID),
    FOREIGN KEY (Position) REFERENCES `Position`(ID)
);

-- Treasury
CREATE TABLE Budget (
    ID INT PRIMARY KEY,
    ApprovedBy INT,
    Author INT,
    FiscalYear INT,
    Status ENUM('SUBMITTED', 'APPROVED', 'PAST') DEFAULT 'SUBMITTED',
    FOREIGN KEY (ApprovedBy) REFERENCES Member(ID),
    FOREIGN KEY (Author) REFERENCES Member(ID)
);

CREATE TABLE BudgetAccount (
    ID INT PRIMARY KEY,
    Budget INT,
    AcctCode VARCHAR(255),
    AcctTitle VARCHAR(255),
    FOREIGN KEY (Budget) REFERENCES Budget(ID)
);

CREATE TABLE Reimbursement (
    ID INT PRIMARY KEY,
    MemberID INT,
    Total DECIMAL(10,2),
    Type VARCHAR(255),
    Description TEXT,
    FOREIGN KEY (MemberID) REFERENCES Member(ID)
);

CREATE TABLE ReimbursementItem (
    ID INT PRIMARY KEY,
    Reimbursement INT,
    Description TEXT,
    ReceiptImage TEXT,
    Price DECIMAL(10,2),
    BudgetAccount INT,
    FOREIGN KEY (Reimbursement) REFERENCES Reimbursement(ID),
    FOREIGN KEY (BudgetAccount) REFERENCES BudgetAccount(ID)
);

CREATE TABLE Vendor (
    ID INT PRIMARY KEY,
    Address VARCHAR(255),
    Website VARCHAR(255),
    Contact VARCHAR(255)
);

CREATE TABLE PurchaseOrder (
    ID INT PRIMARY KEY,
    Vendor INT,
    Reimbursement INT,
    OrderDate DATE,
    FOREIGN KEY (Vendor) REFERENCES Vendor(ID),
    FOREIGN KEY (Reimbursement) REFERENCES Reimbursement(ID)
);

-- Gear/Merch Management
CREATE TABLE RentalItem (
    ID INT PRIMARY KEY,
    PurchaseOrder INT,
    Name VARCHAR(255),
    Price DECIMAL(10,2),
    Location VARCHAR(255),
    Quantity INT,
    Size VARCHAR(255),
    Availability VARCHAR(255),
    Status ENUM('AVAILABLE', 'CHECKED_OUT', 'DAMAGED', 'LOST', 'DEPRECATED') DEFAULT 'AVAILABLE',
    Picture TEXT,
    FOREIGN KEY (PurchaseOrder) REFERENCES PurchaseOrder(ID)
);

CREATE TABLE MerchItem (
    ID INT PRIMARY KEY,
    PurchaseOrder INT,
    Price DECIMAL(10,2),
    Quantity INT,
    Name VARCHAR(255),
    Description TEXT,
    Location VARCHAR(255),
    FOREIGN KEY (PurchaseOrder) REFERENCES PurchaseOrder(ID)
);

CREATE TABLE MerchSale (
    ID INT PRIMARY KEY,
    SaleDate DATE NOT NULL DEFAULT (CURRENT_DATE),
    Cash DECIMAL(10,2)
);

CREATE TABLE MerchSaleItems (
    MerchItem INT,
    MerchSale INT,
    PRIMARY KEY (MerchItem, MerchSale),
    FOREIGN KEY (MerchItem) REFERENCES MerchItem(ID),
    FOREIGN KEY (MerchSale) REFERENCES MerchSale(ID)
);

CREATE TABLE GearReservation (
    ID INT PRIMARY KEY,
    Member INT,
    CheckOutDate DATE,
    ReturnDate DATE,
    FOREIGN KEY (Member) REFERENCES Member(ID)
);

CREATE TABLE GearReservationItems (
    Reservation INT,
    Item INT,
    PRIMARY KEY (Reservation, Item),
    FOREIGN KEY (Reservation) REFERENCES GearReservation(ID),
    FOREIGN KEY (Item) REFERENCES RentalItem(ID)
);

-- Sample data for ClubStack database
-- Insert sample data with proper foreign key relationships

-- General Membership Data
INSERT INTO Member (ID, FirstName, LastName, PreferredName, GraduationYear, IsGradStudent, ActivationDate, CarPlate, CarState, CarPassCount, EmerContactName, EmerContactPhone) VALUES
(1, 'John', 'Smith', 'Johnny', 2025, FALSE, '2023-09-01', 'ABC123', 'MA', 2, 'Mary Smith', '555-0101'),
(2, 'Sarah', 'Johnson', NULL, 2024, FALSE, '2022-08-15', 'XYZ789', 'NH', 1, 'Bob Johnson', '555-0102'),
(3, 'Michael', 'Chen', 'Mike', 2026, FALSE, '2024-01-10', NULL, NULL, 0, 'Lisa Chen', '555-0103'),
(4, 'Emily', 'Rodriguez', NULL, 2023, TRUE, '2023-09-05', 'DEF456', 'MA', 3, 'Carlos Rodriguez', '555-0104'),
(5, 'David', 'Kim', 'Dave', 2025, FALSE, '2023-08-20', 'GHI789', 'VT', 1, 'Susan Kim', '555-0105');

-- Member addresses
INSERT INTO Address (ID, Member, Nickname, Line1, Line2, State, Zip) VALUES
(1, 1, 'Home', '123 Main St', 'Apt 4B', 'MA', '02115'),
(2, 1, 'School', '360 Huntington Ave', 'Dorm Room 501', 'MA', '02115'),
(3, 2, 'Home', '456 Oak Ave', NULL, 'NH', '03301'),
(4, 3, 'Campus', '110 Forsyth St', 'Suite 200', 'MA', '02115'),
(5, 4, 'Apartment', '789 Commonwealth Ave', 'Unit 12', 'MA', '02215');

-- Allergy information
INSERT INTO Allergy (ID, Name) VALUES
(1, 'Peanuts'),
(2, 'Shellfish'),
(3, 'Dairy'),
(4, 'Gluten'),
(5, 'Tree Nuts');

-- Link members to their allergies
INSERT INTO AllergyUsers (UserID, AllergyID) VALUES
(1, 1), -- John has peanut allergy
(1, 3), -- John also has dairy allergy
(2, 2), -- Sarah has shellfish allergy
(3, 4), -- Mike has gluten allergy
(4, 5); -- Emily has tree nut allergy

-- Permission levels for different user roles
INSERT INTO Permission (ID, Title, PageAccess) VALUES
(1, 'President', 'ALL_PAGES'),
(2, 'VP Org', 'EVENTS,MEMBERS,TREASURY'),
(3, 'VP Trips', 'PROFILE,EVENTS,MEMBERS'),
(4, 'Treasurer', 'PROFILE,TREASURY,BUDGET,REIMBURSEMENTS'),
(5, 'Member', 'PROFILE,EVENTS,REIMBURSEMENTS');

-- Link Permissions to Members
INSERT INTO MemberPermissions (Permission, Member) VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 4),
(5, 5);

-- Member feedback on club activities
INSERT INTO Feedback (ID, Member, Rating, Description, Anonymous) VALUES
(1, 1, 5, 'Great hiking trip last weekend! Well organized.', FALSE),
(2, 2, 4, 'Food at the event was good but could use more vegetarian options.', TRUE),
(3, 3, 5, 'Love the new gear rental system - very convenient.', FALSE),
(4, 4, 3, 'Meeting location was hard to find, better signage needed.', TRUE),
(5, 5, 5, 'Excellent leadership workshop, learned a lot!', FALSE);

-- Events Data
INSERT INTO Event (ID, Author, PartySize, MaxSize, EventLoc, Randomized, Name, Description, MeetLoc, LeadOrg, EventType, RecItems, Picture) VALUES
(1, 1, 15, 20, 'Loj', FALSE, 'Fall Foliage Hike', 'Day hike to see autumn colors', 'Curry Student Center', 'Hiking Club', 'Outdoor', 'Hiking boots, water bottle, snacks', 'fall_hike.jpg'),
(2, 2, 8, 12, 'Loj', FALSE, 'Rock Climbing Basics', 'Introduction to outdoor climbing', 'Marino Center', 'Climbing Committee', 'Educational', 'Climbing shoes, harness (provided)', 'climbing.jpg'),
(3, 3, 25, 30, 'Centennial', TRUE, 'Club Fair Booth', 'Recruit new members at fall fair', 'Student Center', 'Membership', 'Social', 'Club t-shirt', 'club_fair.jpg'),
(4, 4, 12, 15, 'Pub', FALSE, 'Monthly Social Dinner', 'Casual dinner and socializing', 'Ruggles Station', 'Social Committee', 'Social', 'Appetite and good mood', 'dinner.jpg'),
(5, 5, 6, 8, 'Gear Locker', FALSE, 'Gear Maintenance Workshop', 'Learn to maintain climbing gear', 'Marino Basement', 'Safety Committee', 'Educational', 'Old gear to practice on', 'maintenance.jpg');

-- RSVP responses for events
INSERT INTO RSVP (ID, Event, CanBringCar, AvailStart, AvailEnd) VALUES
(1, 1, TRUE, '2024-10-15 08:00:00', '2024-10-15 18:00:00'),
(2, 1, FALSE, '2024-10-15 09:00:00', '2024-10-15 17:00:00'),
(3, 2, FALSE, '2024-10-20 14:00:00', '2024-10-20 18:00:00'),
(4, 3, TRUE, '2024-09-25 10:00:00', '2024-09-25 16:00:00'),
(5, 4, FALSE, '2024-11-05 18:00:00', '2024-11-05 22:00:00');

-- Event attendance roster
INSERT INTO EventRoster (ID, Event, Member, DateRegistered, Waitlisted) VALUES
(1, 1, 1, '2024-10-01 14:30:00', FALSE),
(2, 1, 2, '2024-10-02 09:15:00', FALSE),
(3, 1, 3, '2024-10-03 20:45:00', TRUE), -- Waitlisted due to capacity
(4, 2, 2, '2024-10-10 11:20:00', FALSE),
(5, 3, 4, '2024-09-20 16:00:00', FALSE);

-- Communications Data
INSERT INTO Communication (ID, Subject, Content, DateSent) VALUES
(1, 'Welcome New Members!', 'Welcome to the outdoor club! Here''s what you need to know...', '2024-09-01 10:00:00'),
(2, 'Upcoming Hike This Weekend', 'Don''t forget about our fall foliage hike this Saturday!', '2024-10-14 18:30:00'),
(3, 'Gear Room Hours Update', 'New hours for gear checkout: Mon-Fri 4-6pm, Sat 10am-2pm', '2024-09-15 12:00:00'),
(4, 'Officer Elections Next Month', 'Nominations open for next year''s officer positions.', '2024-03-01 14:00:00'),
(5, 'Safety Reminder', 'Please review safety protocols before upcoming trips.', '2024-10-01 16:00:00');

-- Communication recipients (who received each message)
INSERT INTO CommunicationRecipients (Communication, Member) VALUES
(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), -- Welcome message to all
(2, 1), (2, 2), (2, 3), -- Hike announcement to participants
(3, 1), (3, 2), (3, 4), (3, 5), -- Gear room hours to gear users
(4, 1), (4, 2), (4, 3), (4, 4), (4, 5), -- Elections to all members
(5, 1), (5, 2); -- Safety reminder to trip leaders

-- Voting Data
INSERT INTO Term (ID, StartDate, EndDate, Name) VALUES
(1, '2023-09-01', '2023-12-31', 'Fall 23'),
(2, '2024-01-01', '2024-05-30', 'Spring 24'),
(3, '2024-06-01', '2024-08-31', 'Summer 24');

-- Officer positions available for election
INSERT INTO Position (ID, Title, BallotOrder) VALUES
(1, 'President', 1),
(2, 'VP Trips', 2),
(3, 'VP Org', 3),
(4, 'VP Comm', 4),
(5, 'Treasurer', 5);

-- Nominations for officer positions
INSERT INTO Nomination (ID, Nominator, Nominee, `Position`, Accepted) VALUES
(1, 2, 1, 1, TRUE), -- Sarah nominates John for President
(2, 3, 2, 2, TRUE), -- Mike nominates Sarah for VP
(3, 1, 4, 3, TRUE), -- John nominates Emily for Treasurer
(4, 4, 3, 4, FALSE), -- Emily nominates Mike for Secretary (declined)
(5, 5, 5, 5, TRUE); -- David nominates himself for Safety Officer

-- Election events
INSERT INTO Election (ID, Date, Term, NominateBy) VALUES
(1, '2023-08-22', 1, '2023-08-10'),
(2, '2023-11-15', 2, '2023-11-01'),
(3, '2024-04-29', 3, '2024-04-01');

-- Which positions are up for election in each election
INSERT INTO ElectionPositions (`Position`, Election) VALUES
(1, 1), (2, 1), (3, 1), (4, 1), (5, 1),
(1, 2), (2, 2), (3, 2), (4, 2),
(1, 3);

-- Ballots cast in elections
INSERT INTO Ballot (ID, `Position`, Election, CreatedAt) VALUES
(1, 1, 1, '2024-04-15 14:30:00'), -- President ballot
(2, 2, 1, '2024-04-15 14:31:00'), -- VP ballot
(3, 3, 1, '2024-04-15 14:32:00'), -- Treasurer ballot
(4, 1, 2, '2023-04-15 15:00:00'), -- Previous year President
(5, 5, 1, '2024-04-15 14:35:00'); -- Safety Officer ballot

-- Election winners
INSERT INTO Winner (ID, Member, `Position`) VALUES
(1, 1, 1),
(2, 2, 2),
(3, 4, 3),
(4, 3, 4),
(5, 5, 5);

-- Treasury Data
INSERT INTO Budget (ID, ApprovedBy, Author, FiscalYear, Status) VALUES
(1, 1, 4, 2024, 'APPROVED'), -- Emily authored, John approved
(2, 2, 4, 2025, 'SUBMITTED'), -- Emily authored, pending Sarah approval
(3, 1, 3, 2023, 'PAST'), -- Mike authored historical budget
(4, 4, 4, 2026, 'SUBMITTED'), -- Emily's future budget proposal
(5, 1, 2, 2024, 'APPROVED'); -- Sarah authored, John approved

-- Budget account categories
INSERT INTO BudgetAccount (ID, Budget, AcctCode, AcctTitle) VALUES
(1, 1, 'GEAR001', 'Climbing Equipment'),
(2, 1, 'TRANS001', 'Transportation'),
(3, 1, 'FOOD001', 'Event Catering'),
(4, 2, 'GEAR002', 'Camping Gear'),
(5, 2, 'MISC001', 'General Supplies');

-- Reimbursement requests
INSERT INTO Reimbursement (ID, MemberID, Total, Type, Description) VALUES
(1, 1, 156.78, 'Event Supplies', 'Rope and carabiners for climbing workshop'),
(2, 2, 89.45, 'Transportation', 'Gas for trip to White Mountains'),
(3, 4, 234.90, 'Food', 'Groceries for weekend camping trip'),
(4, 3, 67.23, 'Equipment', 'First aid kit refill supplies'),
(5, 5, 123.50, 'Gear Maintenance', 'Rope cleaning and inspection tools');

-- Individual items in reimbursement requests
INSERT INTO ReimbursementItem (ID, Reimbursement, Description, ReceiptImage, Price, BudgetAccount) VALUES
(1, 1, 'Dynamic climbing rope 60m', 'receipt_rope.jpg', 120.00, 1),
(2, 1, 'Locking carabiners (6 pack)', 'receipt_biners.jpg', 36.78, 1),
(3, 2, 'Gasoline for van rental', 'receipt_gas.jpg', 89.45, 2),
(4, 3, 'Trail mix and energy bars', 'receipt_snacks.jpg', 45.30, 3),
(5, 3, 'Camp stove fuel canisters', 'receipt_fuel.jpg', 28.60, 4);

-- Vendor information
INSERT INTO Vendor (ID, Address, Website, Contact) VALUES
(1, '123 Outdoor Gear St, Boston MA 02101', 'www.outdoorgearstore.com', 'sales@outdoorgearstore.com'),
(2, '456 Climbing Ave, Cambridge MA 02139', 'www.climbingpro.com', '617-555-CLIMB'),
(3, '789 Adventure Blvd, Newton MA 02458', 'www.adventuresupply.com', 'info@adventuresupply.com'),
(4, '321 Mountain Way, Burlington VT 05401', 'www.mountaingear.com', '802-555-GEAR'),
(5, '654 Trail Rd, Portsmouth NH 03801', 'www.trailoutfitters.com', 'contact@trailoutfitters.com');

-- Purchase orders linking vendors to reimbursements
INSERT INTO PurchaseOrder (ID, Vendor, Reimbursement, OrderDate) VALUES
(1, 1, 1, '2024-09-15'), -- Climbing gear from outdoor store
(2, 3, 2, '2024-10-01'), -- Gas purchase at adventure supply
(3, 2, 3, '2024-09-20'), -- Food from climbing pro (they sell snacks too)
(4, 4, 4, '2024-08-30'), -- First aid supplies from mountain gear
(5, 5, 5, '2024-10-05'); -- Maintenance tools from trail outfitters

-- Gear/Merch Management Data
INSERT INTO RentalItem (ID, PurchaseOrder, Name, Price, Location, Quantity, Size, Availability, Status, Picture) VALUES
(1, 1, 'Climbing Harness', 89.99, 'Gear Room A', 3, 'Medium', 'Available for checkout', 'AVAILABLE', 'harness_med.jpg'),
(2, 1, 'Climbing Harness', 89.99, 'Gear Room A', 2, 'Large', 'Available for checkout', 'AVAILABLE', 'harness_lg.jpg'),
(3, 4, 'Sleeping Bag', 156.50, 'Gear Room B', 5, 'Regular', 'Available for checkout', 'AVAILABLE', 'sleeping_bag.jpg'),
(4, 1, 'Climbing Helmet', 67.89, 'Gear Room A', 4, 'One Size', 'Currently checked out', 'CHECKED_OUT', 'helmet.jpg'),
(5, 4, 'Camping Stove', 78.99, 'Gear Room B', 2, 'Compact', 'Needs repair', 'DAMAGED', 'stove.jpg');

-- Merchandise items for sale
INSERT INTO MerchItem (ID, PurchaseOrder, Price, Quantity, Name, Description, Location) VALUES
(1, 2, 25.00, 15, 'Club T-Shirt', 'Cotton t-shirt with club logo', 'Merch Storage'),
(2, 2, 35.00, 8, 'Club Hoodie', 'Fleece hoodie with embroidered logo', 'Merch Storage'),
(3, 3, 15.00, 20, 'Water Bottle', 'Stainless steel with club design', 'Merch Storage'),
(4, 3, 12.00, 25, 'Sticker Pack', 'Outdoor-themed sticker collection', 'Merch Storage'),
(5, 5, 45.00, 5, 'Club Backpack', 'Daypack with club patches', 'Merch Storage');

-- Merchandise sales transactions
INSERT INTO MerchSale (ID, SaleDate, Cash) VALUES
(1, '2024-09-15', 75.00), -- Sold t-shirts and stickers
(2, '2024-09-20', 105.00), -- Sold hoodies and water bottles
(3, '2024-10-01', 45.00), -- Sold backpack
(4, '2024-10-05', 60.00), -- Mixed merchandise sale
(5, '2024-10-10', 90.00); -- Large sticker and t-shirt sale

-- Items sold in each transaction
INSERT INTO MerchSaleItems (MerchItem, MerchSale) VALUES
(1, 1), (4, 1), -- T-shirt and stickers in sale 1
(2, 2), (3, 2), -- Hoodie and water bottle in sale 2
(5, 3), -- Backpack in sale 3
(1, 4), (3, 4), -- T-shirt and water bottle in sale 4
(1, 5), (4, 5); -- T-shirt and multiple sticker packs in sale 5

-- Gear reservations by members
INSERT INTO GearReservation (ID, Member, CheckOutDate, ReturnDate) VALUES
(1, 1, '2024-10-15', '2024-10-17'), -- John's weekend climbing trip
(2, 2, '2024-09-28', '2024-09-30'), -- Sarah's camping weekend
(3, 3, '2024-10-20', '2024-10-22'), -- Mike's hiking trip
(4, 4, '2024-11-01', '2024-11-03'), -- Emily's outdoor workshop
(5, 5, '2024-10-08', '2024-10-10'); -- David's climbing practice

-- Specific items reserved in each reservation
INSERT INTO GearReservationItems (Reservation, Item) VALUES
(1, 1), (1, 4), -- John reserved harness and helmet
(2, 3), (2, 5), -- Sarah reserved sleeping bag and stove
(3, 3), -- Mike reserved sleeping bag
(4, 1), (4, 2), -- Emily reserved two different harnesses
(5, 4); -- David reserved helmet


-- End of sample data for ClubStack database

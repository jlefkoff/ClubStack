DROP DATABASE IF EXISTS ClubStack;
CREATE DATABASE ClubStack;
USE ClubStack;

-- General Membership
CREATE TABLE Member (
    ID INT PRIMARY KEY AUTO_INCREMENT,
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
    EmerContactPhone VARCHAR(80) NOT NULL
);

CREATE TABLE Address (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Member INT,
    Nickname VARCHAR(255),
    Line1 VARCHAR(255),
    Line2 VARCHAR(255),
    State VARCHAR(50),
    Zip VARCHAR(10),
    FOREIGN KEY (Member) REFERENCES Member(ID)
);

CREATE TABLE Allergy (
    ID INT PRIMARY KEY AUTO_INCREMENT,
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
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Title VARCHAR(255) NOT NULL,
    PageAccess TEXT
);

CREATE TABLE Page (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Slug VARCHAR(255) NOT NULL
);

CREATE TABLE PagePermissions (
    PageID INT,
    PermissionID INT,
    PRIMARY KEY (PageID, PermissionID),
    FOREIGN KEY (PageID) REFERENCES Page(ID),
    FOREIGN KEY (PermissionID) REFERENCES Permission(ID)
);

CREATE TABLE MemberPermissions (
    Permission INT,
    Member INT,
    PRIMARY KEY (Permission, Member),
    FOREIGN KEY (Permission) REFERENCES Permission(ID),
    FOREIGN KEY (Member) REFERENCES Member(ID)
);

CREATE TABLE Feedback (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Member INT NOT NULL,
    Rating INT NOT NULL,
    Description TEXT,
    Anonymous BOOLEAN,
    FOREIGN KEY (Member) REFERENCES Member(ID)
);

-- Events
CREATE TABLE Event (
    ID INT PRIMARY KEY AUTO_INCREMENT,
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
    EventDate DATE,
    FOREIGN KEY (Author) REFERENCES Member(ID)
);

CREATE TABLE RSVP (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Member INT NOT NULL,
    Event INT NOT NULL,
    CanBringCar BOOLEAN NOT NULL DEFAULT FALSE,
    AvailStart DATETIME NOT NULL,
    AvailEnd DATETIME NOT NULL,
    FOREIGN KEY (Event) REFERENCES Event(ID),
    FOREIGN KEY (Member) REFERENCES Member(ID)
);

CREATE TABLE EventRoster (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Event INT NOT NULL,
    Member INT NOT NULL,
    DateRegistered DATETIME DEFAULT CURRENT_TIMESTAMP,
    Waitlisted BOOLEAN,
    FOREIGN KEY (Event) REFERENCES Event(ID),
    FOREIGN KEY (Member) REFERENCES Member(ID)
);

-- Comms
CREATE TABLE Communication (
    ID INT PRIMARY KEY AUTO_INCREMENT,
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
    ID INT PRIMARY KEY AUTO_INCREMENT,
    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL,
    Name VARCHAR(255) NOT NULL
);

CREATE TABLE Position (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Title VARCHAR(255),
    BallotOrder INT
);

CREATE TABLE Nomination (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Nominator INT,
    Nominee INT,
    `Position` INT,
    Accepted BOOLEAN,
    FOREIGN KEY (Nominator) REFERENCES Member(ID),
    FOREIGN KEY (Nominee) REFERENCES Member(ID),
    FOREIGN KEY (Position) REFERENCES `Position`(ID)
);

CREATE TABLE Election (
    ID INT PRIMARY KEY AUTO_INCREMENT,
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
    ID INT PRIMARY KEY AUTO_INCREMENT,
    `Position` INT,
    Election INT,
    CreatedAt DATETIME NOT NULL,
    FOREIGN KEY (Position) REFERENCES `Position`(ID),
    FOREIGN KEY (Election) REFERENCES Election(ID)
);

-- Track which accepted nominations appear on each ballot
CREATE TABLE BallotOptions (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Ballot INT,
    Nomination INT,
    FOREIGN KEY (Ballot) REFERENCES Ballot(ID),
    FOREIGN KEY (Nomination) REFERENCES Nomination(ID)
);

-- Track individual member votes
CREATE TABLE Vote (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Ballot INT,
    Member INT,
    BallotOption INT,
    VotedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Ballot) REFERENCES Ballot(ID),
    FOREIGN KEY (Member) REFERENCES Member(ID),
    FOREIGN KEY (BallotOption) REFERENCES BallotOptions(ID),
    UNIQUE KEY unique_member_ballot (Member, Ballot) -- Ensures one vote per member per ballot
);

CREATE TABLE Winner (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Member INT,
    `Position` INT,
    FOREIGN KEY (Member) REFERENCES Member(ID),
    FOREIGN KEY (Position) REFERENCES `Position`(ID)
);

-- Treasury
CREATE TABLE Budget (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    ApprovedBy INT,
    Author INT,
    FiscalYear INT,
    Status ENUM('SUBMITTED', 'APPROVED', 'PAST') DEFAULT 'SUBMITTED',
    FOREIGN KEY (ApprovedBy) REFERENCES Member(ID),
    FOREIGN KEY (Author) REFERENCES Member(ID)
);

CREATE TABLE BudgetAccount (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Budget INT,
    AcctCode VARCHAR(255),
    AcctTitle VARCHAR(255),
    FOREIGN KEY (Budget) REFERENCES Budget(ID)
);

CREATE TABLE Reimbursement (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    MemberID INT,
    Total DECIMAL(10,2),
    Type VARCHAR(255),
    Description TEXT,
    Status ENUM('SUBMITTED', 'APPROVED', 'REJECTED') DEFAULT 'SUBMITTED',
    FOREIGN KEY (MemberID) REFERENCES Member(ID)
);

CREATE TABLE ReimbursementItem (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Reimbursement INT,
    Description TEXT,
    ReceiptImage TEXT,
    Price DECIMAL(10,2),
    BudgetAccount INT,
    FOREIGN KEY (Reimbursement) REFERENCES Reimbursement(ID),
    FOREIGN KEY (BudgetAccount) REFERENCES BudgetAccount(ID)
);

CREATE TABLE Vendor (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Address VARCHAR(255),
    Website VARCHAR(255),
    Contact VARCHAR(255)
);

CREATE TABLE PurchaseOrder (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Vendor INT,
    Reimbursement INT,
    OrderDate DATE,
    FOREIGN KEY (Vendor) REFERENCES Vendor(ID),
    FOREIGN KEY (Reimbursement) REFERENCES Reimbursement(ID)
);

-- Gear/Merch Management
CREATE TABLE RentalItem (
    ID INT PRIMARY KEY AUTO_INCREMENT,
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
    ID INT PRIMARY KEY AUTO_INCREMENT,
    PurchaseOrder INT,
    Price DECIMAL(10,2),
    Quantity INT,
    Name VARCHAR(255),
    Description TEXT,
    Location VARCHAR(255),
    FOREIGN KEY (PurchaseOrder) REFERENCES PurchaseOrder(ID)
);

CREATE TABLE MerchSale (
    ID INT PRIMARY KEY AUTO_INCREMENT,
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
    ID INT PRIMARY KEY AUTO_INCREMENT,
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

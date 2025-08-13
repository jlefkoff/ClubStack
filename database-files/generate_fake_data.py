#!/usr/bin/env python3
"""
Simple Fake Data Generator for ClubStack Database

This script uses the Faker library to generate realistic fake data
for all tables in the ClubStack database schema and outputs SQL INSERT statements.

Usage:
    pip install faker
    python simple_fake_data_generator.py

This will create a file called 'fake_data_inserts.sql' with INSERT statements
that you can run against your ClubStack database.
"""

import random
from faker import Faker
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()


def generate_fake_data():
    print("🎭 Generating fake data for ClubStack database...")

    # Store IDs for referential integrity
    member_ids = list(range(100, 200))  # 100 fake members
    event_ids = list(range(100, 150))  # 50 fake events

    sql_statements = []
    sql_statements.append("-- 🎭 Generated Fake Data for ClubStack Database")
    sql_statements.append(
        f"-- Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    sql_statements.append(
        "-- Run this file against your ClubStack database to populate with fake data"
    )
    sql_statements.append("USE ClubStack;")

    # 1. MEMBERS
    print("👥 Generating members...")
    sql_statements.append("-- 👥 MEMBERS")

    graduation_years = [2024, 2025, 2026, 2027, 2028]

    for member_id in member_ids:
        first_name = fake.first_name()
        last_name = fake.last_name()
        preferred_name = first_name if random.random() < 0.7 else fake.first_name()
        grad_year = random.choice(graduation_years)
        is_grad = "TRUE" if random.random() < 0.15 else "FALSE"
        activation_date = fake.date_between(
            start_date="-2y", end_date="today"
        ).strftime("%Y-%m-%d")

        # Car info (60% have cars)
        if random.random() < 0.6:
            car_plate = fake.license_plate().replace("'", "''")
            car_state = fake.state_abbr()
            car_pass_count = random.randint(0, 5)
        else:
            car_plate = "NULL"
            car_state = "NULL"
            car_pass_count = 0

        emergency_name = fake.name().replace("'", "''")
        emergency_phone = fake.phone_number().replace("'", "''")

        sql = f"""INSERT INTO Member (ID, FirstName, LastName, PreferredName, GraduationYear, IsGradStudent, ActivationDate, CarPlate, CarState, CarPassCount, EmerContactName, EmerContactPhone) VALUES ({member_id}, '{first_name}', '{last_name}', '{preferred_name}', {grad_year}, {is_grad}, '{activation_date}', {car_plate if car_plate == 'NULL' else f"'{car_plate}'"}, {car_state if car_state == 'NULL' else f"'{car_state}'"}, {car_pass_count}, '{emergency_name}', '{emergency_phone}');"""

        sql_statements.append(sql)

    sql_statements.append("")

    # 2. ADDRESSES
    print("🏠 Generating addresses...")
    sql_statements.append("-- 🏠 ADDRESSES")

    address_types = ["Home", "School", "Campus", "Apartment", "Dorm", "Parent Home"]
    states = ["MA", "NH", "VT", "CT", "RI", "ME", "NY"]
    address_id = 100

    for member_id in member_ids:
        # Each member has 1-2 addresses
        num_addresses = random.randint(1, 2)

        for _ in range(num_addresses):
            nickname = random.choice(address_types)
            line1 = fake.street_address().replace("'", "''")
            line2 = f"Apt {random.randint(1, 50)}" if random.random() < 0.3 else "NULL"
            state = random.choice(states)
            zip_code = fake.zipcode()

            sql = f"""INSERT INTO Address (ID, Member, Nickname, Line1, Line2, State, Zip) VALUES ({address_id}, {member_id}, '{nickname}', '{line1}', {line2 if line2 == 'NULL' else f"'{line2}'"}, '{state}', '{zip_code}');"""

            sql_statements.append(sql)
            address_id += 1

    sql_statements.append("")

    # 3. ALLERGIES & ALLERGY USERS
    print("🤧 Generating allergies...")
    sql_statements.append("-- 🤧 ALLERGIES")

    common_allergies = [
        "Shellfish",
        "Fish",
        "Eggs",
        "Soy",
        "Sesame",
        "Sulfites",
        "Latex",
        "Dust Mites",
        "Pet Dander",
        "Pollen",
        "Bee Stings",
        "Penicillin",
        "Aspirin",
        "Strawberries",
        "Chocolate",
    ]

    allergy_id = 20
    allergy_ids = []

    for allergy_name in common_allergies:
        sql = f"INSERT INTO Allergy (ID, Name) VALUES ({allergy_id}, '{allergy_name}');"
        sql_statements.append(sql)
        allergy_ids.append(allergy_id)
        allergy_id += 1

    sql_statements.append("")
    sql_statements.append("-- 🤧 ALLERGY USERS")

    # 25% of members have allergies
    for member_id in member_ids:
        if random.random() < 0.25:
            num_allergies = random.randint(1, 2)
            member_allergies = random.sample(allergy_ids, num_allergies)
            for allergy_id in member_allergies:
                sql = f"INSERT INTO AllergyUsers (UserID, AllergyID) VALUES ({member_id}, {allergy_id});"
                sql_statements.append(sql)

    sql_statements.append("")

    # 4. PAGES
    print("📄 Generating pages...")
    sql_statements.append("-- 📄 PAGES")

    page_slugs = [
        "home",
        "profile",
        "events",
        "members",
        "gear",
        "communications",
        "treasury",
        "budget",
        "reimbursements",
        "safety",
        "inventory",
        "social",
        "admin",
        "elections",
        "feedback",
        "reports",
    ]

    page_id = 1
    page_ids = []
    for slug in page_slugs:
        sql = f"INSERT INTO Page (ID, Slug) VALUES ({page_id}, '{slug}');"
        sql_statements.append(sql)
        page_ids.append(page_id)
        page_id += 1

    sql_statements.append("")

    # 5. PERMISSIONS
    print("🔐 Generating permissions...")
    sql_statements.append("-- 🔐 PERMISSIONS")

    new_permissions = [
        (5, "Member"),
        (20, "VP Comm"),
        (21, "Safety Officer"),
        (22, "Gear Manager"),
        (23, "Social Chair"),
        (24, "Alumni"),
        (25, "Inactive Member"),
        (26, "Trip Leader"),
        (27, "New Member"),
        (28, "President"),
        (29, "VP Trips"),
        (30, "Treasurer"),
    ]

    permission_ids = []
    for perm_id, title in new_permissions:
        sql = f"INSERT INTO Permission (ID, Title) VALUES ({perm_id}, '{title}');"
        sql_statements.append(sql)
        permission_ids.append(perm_id)

    sql_statements.append("")

    # 6. PAGE PERMISSIONS (Junction Table)
    print("🔗 Generating page permissions...")
    sql_statements.append("-- 🔗 PAGE PERMISSIONS")

    # Define which permissions can access which pages
    permission_page_mapping = {
        5: [
            1,
            2,
            3,
            5,
            6,
            14,
        ],  # Member: home, profile, events, gear, communications, feedback
        20: [1, 2, 3, 4, 6, 13, 15],  # VP Comm: + members, admin, reports
        21: [1, 2, 3, 4, 10, 15],  # Safety Officer: + members, safety, reports
        22: [1, 2, 5, 11, 15],  # Gear Manager: + inventory, reports
        23: [1, 2, 3, 4, 12],  # Social Chair: + members, social
        24: [1, 2, 3, 6],  # Alumni: limited access
        25: [2],  # Inactive Member: profile only
        26: [1, 2, 3, 4, 5, 10, 15],  # Trip Leader: + members, gear, safety, reports
        27: [1, 2, 3, 14],  # New Member: + feedback
        28: [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
        ],  # President: all pages
        29: [1, 2, 3, 4, 7, 8, 10, 15],  # VP Trips: + treasury, budget, safety, reports
        30: [
            1,
            2,
            7,
            8,
            9,
            15,
        ],  # Treasurer: + treasury, budget, reimbursements, reports
    }

    for perm_id, allowed_pages in permission_page_mapping.items():
        for page_id in allowed_pages:
            sql = f"INSERT INTO PagePermissions (PageID, PermissionID) VALUES ({page_id}, {perm_id});"
            sql_statements.append(sql)

    sql_statements.append("")

    # 7. MEMBER PERMISSIONS
    print("👤 Generating member permissions...")
    sql_statements.append("-- MEMBER PERMISSIONS")

    # Assign permissions to members
    permission_weights = {
        5: 0.65,  # Member (65%)
        20: 0.03,  # VP Comm (3%)
        21: 0.05,  # Safety Officer (5%)
        22: 0.02,  # Gear Manager (2%)
        23: 0.03,  # Social Chair (3%)
        24: 0.08,  # Alumni (8%)
        25: 0.02,  # Inactive (2%)
        26: 0.08,  # Trip Leader (8%)
        27: 0.03,  # New Member (3%)
        28: 0.005,  # President (0.5%)
        29: 0.005,  # VP Trips (0.5%)
        30: 0.01,  # Treasurer (1%)
    }

    for member_id in member_ids:
        # Weighted random choice
        rand = random.random()
        cumulative = 0
        selected_permission = 5  # Default to Member

        for perm_id, weight in permission_weights.items():
            cumulative += weight
            if rand <= cumulative:
                selected_permission = perm_id
                break

        sql = f"INSERT INTO MemberPermissions (Permission, Member) VALUES ({selected_permission}, {member_id});"
        sql_statements.append(sql)

    sql_statements.append("")

    # 8. EVENTS
    print("🎪 Generating events...")
    sql_statements.append("-- 🎪 EVENTS")

    event_names = [
      "Beginner Rock Climbing",
      "Advanced Mountaineering",
      "Weekend Backpacking",
      "Map and Compass Workshop",
      "Wilderness First Aid",
      "Gear Maintenance Session",
      "New Member BBQ",
      "Monthly Social Dinner",
      "Film Night: Mountain Movies",
      "Knot Tying Workshop",
      "Leave No Trace Training",
      "Winter Camping Prep",
      "Avalanche Safety Course",
      "Photography Workshop",
      "Trail Maintenance Day",
      "Club Fair Booth",
      "Officer Elections",
      "Budget Planning Meeting",
      "Gear Sale Event",
      "Trip Planning Session",
      "Safety Committee Meeting",
      "White Mountain Day Hike",
      "Ice Climbing Introduction",
      "Ski Touring Basics",
      "Camping Fundamentals",
      "Peak Bagging Challenge",
      "Sunrise Photography Hike",
    ]

    locations = [
      "White Mountains NH",
      "Loj",
      "Pub",
      "Centennial",
      "Campus",
      "Local Crag",
      "Gear Room",
      "Marino Center",
    ]
    meet_locations = [
      "Curry Student Center",
      "Marino Center",
      "Ruggles Station",
      "Back Bay Station",
      "Campus Quad",
    ]
    organizations = [
      "Hiking Committee",
      "Climbing Committee",
      "Social Committee",
      "Safety Committee",
      "Membership Committee",
    ]
    event_types = [
      "Outdoor",
      "Educational",
      "Social",
      "Training",
      "Meeting",
      "Competition",
    ]

    for event_id in event_ids:
      author_id = random.choice(member_ids)
      party_size = random.randint(5, 30)
      max_size = party_size + random.randint(5, 20)
      event_loc = random.choice(locations)
      randomized = "TRUE" if random.random() < 0.15 else "FALSE"
      name = random.choice(event_names)
      description = fake.text(max_nb_chars=150).replace("'", "''")
      meet_loc = random.choice(meet_locations)
      lead_org = random.choice(organizations)
      event_type = random.choice(event_types)

      # Generate relevant recommended items
      rec_items_options = [
        "hiking boots, water, snacks",
        "climbing shoes, harness, helmet",
        "sleeping bag, tent, camp stove",
        "warm layers, headlamp, map",
        "first aid kit, whistle, compass",
        "notebook, pen, enthusiasm",
      ]
      rec_items = random.choice(rec_items_options)
      picture = f"{name.lower().replace(' ', '_').replace(':', '')}.jpg"

      # Generate EventDate: from now to 90 days in the future
      event_date = fake.date_between(start_date="today", end_date="+90d").strftime("%Y-%m-%d")

      sql = f"""INSERT INTO Event (ID, Author, PartySize, MaxSize, EventLoc, Randomized, Name, Description, MeetLoc, LeadOrg, EventType, RecItems, Picture, EventDate) VALUES ({event_id}, {author_id}, {party_size}, {max_size}, '{event_loc}', {randomized}, '{name}', '{description}', '{meet_loc}', '{lead_org}', '{event_type}', '{rec_items}', '{picture}', '{event_date}');"""

      sql_statements.append(sql)

    sql_statements.append("")

    # 9. EVENT ROSTER (signups)
    print("📋 Generating event signups...")
    sql_statements.append("-- 📋 EVENT ROSTER")

    roster_id = 100
    for event_id in event_ids:
        # Random number of signups per event (50-90% of max capacity)
        max_capacity = random.randint(15, 40)
        lower = int(max_capacity * 0.5)
        upper = int(max_capacity * 0.9)
        if lower > upper:
            lower, upper = upper, lower
        num_signups = random.randint(lower, upper)
        event_members = random.sample(member_ids, min(num_signups, len(member_ids)))

        for member_id in event_members:
            date_registered = fake.date_time_between(
                start_date="-30d", end_date="now"
            ).strftime("%Y-%m-%d %H:%M:%S")
            waitlisted = "TRUE" if random.random() < 0.1 else "FALSE"  # 10% waitlisted

            sql = f"INSERT INTO EventRoster (ID, Event, Member, DateRegistered, Waitlisted) VALUES ({roster_id}, {event_id}, {member_id}, '{date_registered}', {waitlisted});"
            sql_statements.append(sql)
            roster_id += 1
    sql_statements.append("")

    # 10. FEEDBACK
    print("💬 Generating feedback...")
    sql_statements.append("-- 💬 FEEDBACK")

    feedback_comments = [
        "Excellent trip! Great weather and company.",
        "Well organized event. Trip leaders were knowledgeable.",
        "Beautiful views, would definitely do this again.",
        "Good introduction to the activity. Learned a lot.",
        "Equipment was in great condition. Thanks!",
        "Meeting location was easy to find.",
        "Food was delicious. Perfect amount.",
        "Safety briefing was thorough and helpful.",
        "Great group dynamic. Everyone was supportive.",
        "Challenging but rewarding experience.",
        "Perfect difficulty level for beginners.",
        "Wonderful social event. Met lots of new people.",
        "Informative workshop. Practical skills learned.",
        "Trip timing worked well with my schedule.",
        "Outstanding leadership from trip organizers.",
    ]

    feedback_id = 100
    # Generate feedback for about 30% of event attendees
    for _ in range(150):  # 150 feedback entries
        member_id = random.choice(member_ids)
        rating = random.choices([1, 2, 3, 4, 5], weights=[2, 5, 15, 35, 43])[
            0
        ]  # Mostly positive
        description = random.choice(feedback_comments)
        anonymous = "TRUE" if random.random() < 0.2 else "FALSE"  # 20% anonymous

        sql = f"INSERT INTO Feedback (ID, Member, Rating, Description, Anonymous) VALUES ({feedback_id}, {member_id}, {rating}, '{description}', {anonymous});"
        sql_statements.append(sql)
        feedback_id += 1

    sql_statements.append("")

    # 11. COMMUNICATIONS
    print("📧 Generating communications...")
    sql_statements.append("-- 📧 COMMUNICATIONS")

    communication_subjects = [
        "Weekly Club Update",
        "Upcoming Trip Reminder",
        "New Gear Available",
        "Officer Election Results",
        "Safety Reminder: Winter Conditions",
        "Club Meeting This Thursday",
        "Gear Checkout Hours Update",
        "New Member Welcome",
        "Budget Update",
        "Trip Cancellation Notice",
        "Weather Advisory",
        "Photo Contest Winners",
        "Volunteer Opportunity",
        "Club Social Event",
        "Training Workshop Available",
    ]

    comm_id = 100
    for _ in range(25):  # 25 communications
        subject = random.choice(communication_subjects)
        content = fake.text(max_nb_chars=300).replace("'", "''")
        date_sent = fake.date_time_between(start_date="-6m", end_date="now").strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        sql = f"INSERT INTO Communication (ID, Subject, Content, DateSent) VALUES ({comm_id}, '{subject}', '{content}', '{date_sent}');"
        sql_statements.append(sql)

        # Add recipients (random subset of members)
        num_recipients = random.randint(10, len(member_ids))
        recipients = random.sample(member_ids, num_recipients)

        for recipient_id in recipients:
            sql = f"INSERT INTO CommunicationRecipients (Communication, Member) VALUES ({comm_id}, {recipient_id});"
            sql_statements.append(sql)

        comm_id += 1

    sql_statements.append("")

    # 12. BUDGETS & ACCOUNTS
    print("💰 Generating budget data...")
    sql_statements.append("-- 💰 BUDGETS")

    budget_id = 20
    for year in [2023, 2024, 2025, 2026]:
        approved_by = random.choice(member_ids) if random.random() < 0.8 else "NULL"
        author_id = random.choice(member_ids)
        status_options = ["SUBMITTED", "APPROVED", "PAST"]
        status = random.choice(status_options)

        sql = f"INSERT INTO Budget (ID, ApprovedBy, Author, FiscalYear, Status) VALUES ({budget_id}, {approved_by}, {author_id}, {year}, '{status}');"
        sql_statements.append(sql)
        budget_id += 1

    sql_statements.append("")
    sql_statements.append("-- 💰 BUDGET ACCOUNTS")

    account_categories = [
        ("GEAR", "Equipment & Gear"),
        ("TRANS", "Transportation"),
        ("FOOD", "Food & Catering"),
        ("TRAIN", "Training & Certification"),
        ("INSUR", "Insurance"),
        ("ADMIN", "Administrative"),
        ("EVENT", "Event Supplies"),
        ("MAINT", "Maintenance & Repairs"),
    ]

    account_id = 20
    for budget_id in range(20, 24):  # For each budget
        # Each budget has 4-6 accounts
        selected_categories = random.sample(account_categories, random.randint(4, 6))

        for code, title in selected_categories:
            acct_code = f"{code}{random.randint(100, 999)}"

            sql = f"INSERT INTO BudgetAccount (ID, Budget, AcctCode, AcctTitle) VALUES ({account_id}, {budget_id}, '{acct_code}', '{title}');"
            sql_statements.append(sql)
            account_id += 1

    sql_statements.append("")

    # 13. VENDORS
    print("🏪 Generating vendors...")
    sql_statements.append("-- 🏪 VENDORS")

    vendor_names = [
        "REI Co-op",
        "Eastern Mountain Sports",
        "Outdoor Gear Exchange",
        "International Mountain Equipment",
        "Climb High",
        "Backcountry Gear",
        "Local Outdoor Store",
        "Mountain Warehouse",
        "Gear Coop",
        "Adventure Outpost",
        "Summit Sports",
        "Basecamp Outfitters",
    ]

    vendor_id = 20
    for name in vendor_names:
        address = fake.address().replace("\n", ", ").replace("'", "''")
        website = f"www.{name.lower().replace(' ', '').replace('-', '')}.com"
        contact = fake.email()

        sql = f"INSERT INTO Vendor (ID, Address, Website, Contact) VALUES ({vendor_id}, '{address}', '{website}', '{contact}');"
        sql_statements.append(sql)
        vendor_id += 1

    sql_statements.append("")

    # 14. REIMBURSEMENTS
    print("💳 Generating reimbursements...")
    sql_statements.append("-- 💳 REIMBURSEMENTS")

    reimbursement_types = [
        "Equipment",
        "Transportation",
        "Food",
        "Training",
        "Event Supplies",
        "Maintenance",
    ]

    reimb_id = 20
    for _ in range(30):  # 30 reimbursements
        member_id = random.choice(member_ids)
        total = round(random.uniform(25.00, 500.00), 2)
        reimb_type = random.choice(reimbursement_types)
        description = fake.text(max_nb_chars=100).replace("'", "''")

        sql = f"INSERT INTO Reimbursement (ID, MemberID, Total, Type, Description) VALUES ({reimb_id}, {member_id}, {total}, '{reimb_type}', '{description}');"
        sql_statements.append(sql)
        reimb_id += 1

    sql_statements.append("")

    # 14.5. PURCHASE ORDERS (needed for RentalItem and MerchItem foreign keys)
    print("🛒 Generating purchase orders...")
    sql_statements.append("-- 🛒 PURCHASE ORDERS")

    # Generate additional purchase orders (seed data has 1-5, we need 6-15)
    vendor_ids = list(range(20, 32))  # Our generated vendor IDs
    reimbursement_ids = list(range(20, 50))  # Our generated reimbursement IDs

    for po_id in range(1, 16):  # Purchase Orders 1-15
        vendor_id = random.choice(vendor_ids)
        reimbursement_id = (
            random.choice(reimbursement_ids) if random.random() < 0.8 else "NULL"
        )
        order_date = fake.date_between(start_date="-1y", end_date="today").strftime(
            "%Y-%m-%d"
        )

        sql = f"INSERT INTO PurchaseOrder (ID, Vendor, Reimbursement, OrderDate) VALUES ({po_id}, {vendor_id}, {reimbursement_id}, '{order_date}');"
        sql_statements.append(sql)

    sql_statements.append("")

    # 15. GEAR ITEMS
    print("🎒 Generating rental gear...")
    sql_statements.append("-- 🎒 RENTAL ITEMS")

    gear_items = [
        ("Climbing Harness", 75.00, ["Small", "Medium", "Large"], "Gear Room A"),
        ("Climbing Helmet", 50.00, ["One Size"], "Gear Room A"),
        ("Sleeping Bag", 140.00, ["Regular", "Long"], "Gear Room B"),
        ("Backpack", 95.00, ["40L", "50L", "60L", "70L"], "Gear Room B"),
        (
            "Climbing Shoes",
            85.00,
            ["6", "7", "8", "9", "10", "11", "12"],
            "Gear Room A",
        ),
        ("Camping Stove", 65.00, ["Single Burner", "Double Burner"], "Gear Room B"),
        ("Headlamp", 40.00, ["One Size"], "Gear Room C"),
        ("Climbing Rope", 200.00, ["60m Dynamic", "70m Dynamic"], "Gear Room A"),
        ("Tent", 180.00, ["2-Person", "3-Person", "4-Person"], "Gear Room B"),
        ("Crampons", 120.00, ["Small", "Medium", "Large"], "Gear Room A"),
        ("Ice Axe", 80.00, ["60cm", "70cm"], "Gear Room A"),
        ("Sleeping Pad", 60.00, ["Regular", "Long"], "Gear Room B"),
    ]

    statuses = ["AVAILABLE", "CHECKED_OUT", "DAMAGED", "DEPRECATED"]
    status_weights = [70, 20, 8, 2]  # Most items are available

    item_id = 50
    for _ in range(100):  # 100 rental items
        name, price, sizes, location = random.choice(gear_items)
        purchase_order = random.randint(1, 15)  # Reference existing POs
        size = random.choice(sizes)
        quantity = random.randint(1, 3)

        status = random.choices(statuses, weights=status_weights)[0]
        availability = (
            "Available for checkout" if status == "AVAILABLE" else f"Status: {status}"
        )

        picture = f"{name.lower().replace(' ', '_')}.jpg"

        sql = f"""INSERT INTO RentalItem (ID, PurchaseOrder, Name, Price, Location, Quantity, Size, Availability, Status, Picture) VALUES ({item_id}, {purchase_order}, '{name}', {price}, '{location}', {quantity}, '{size}', '{availability}', '{status}', '{picture}');"""

        sql_statements.append(sql)
        item_id += 1

    sql_statements.append("")

    # 16. MERCHANDISE
    print("🛍️ Generating merchandise...")
    sql_statements.append("-- 🛍️ MERCHANDISE")

    merch_items = [
        ("Club T-Shirt", 22.00, "Soft cotton t-shirt with club logo"),
        ("Club Hoodie", 42.00, "Warm fleece hoodie with embroidered logo"),
        ("Water Bottle", 18.00, "Insulated stainless steel bottle"),
        ("Club Stickers", 5.00, "Weather-resistant vinyl sticker pack"),
        ("Club Hat", 25.00, "Adjustable baseball cap with logo"),
        ("Club Mug", 16.00, "Ceramic mug perfect for camp coffee"),
        ("Club Patch", 8.00, "Iron-on embroidered patch"),
        ("Club Pin", 10.00, "Enamel pin with mountain design"),
        ("Club Buff", 20.00, "Versatile neck gaiter with logo"),
        ("Club Notebook", 12.00, "Weather-resistant field notebook"),
    ]

    merch_id = 50
    for _ in range(40):  # 40 merch items
        name, price, description = random.choice(merch_items)
        purchase_order = random.randint(
            1, 15
        )  # Reference existing POs (1-5 from seed, 6-15 from fake data)
        quantity = random.randint(5, 50)
        location = "Merch Storage"

        sql = f"""INSERT INTO MerchItem (ID, PurchaseOrder, Price, Quantity, Name, Description, Location) VALUES ({merch_id}, {purchase_order}, {price}, {quantity}, '{name}', '{description}', '{location}');"""

        sql_statements.append(sql)
        merch_id += 1

    sql_statements.append("")

    # 17. GEAR RESERVATIONS
    print("📅 Generating gear reservations...")
    sql_statements.append("-- 📅 GEAR RESERVATIONS")

    reservation_id = 20
    rental_item_ids = list(range(50, 150))  # Our generated rental item IDs

    # Generate 75 gear reservations
    for _ in range(75):
        member_id = random.choice(member_ids)

        # Generate realistic checkout periods
        checkout_date = fake.date_between(start_date="-60d", end_date="+30d")

        # Most reservations are 1-7 days, some longer weekend trips up to 14 days
        days_out = random.choices(
            [1, 2, 3, 4, 5, 6, 7, 10, 14], weights=[15, 20, 25, 10, 10, 8, 8, 3, 1]
        )[0]
        return_date = fake.date_between(
            start_date=checkout_date, end_date=checkout_date + timedelta(days=days_out)
        )

        checkout_str = checkout_date.strftime("%Y-%m-%d")
        return_str = return_date.strftime("%Y-%m-%d")

        sql = f"INSERT INTO GearReservation (ID, Member, CheckOutDate, ReturnDate) VALUES ({reservation_id}, {member_id}, '{checkout_str}', '{return_str}');"
        sql_statements.append(sql)
        reservation_id += 1

    sql_statements.append("")
    sql_statements.append("-- 📅 GEAR RESERVATION ITEMS")

    # Generate reservation items (which specific gear was reserved)
    reservation_id = 20
    for _ in range(75):  # For each reservation
        # Each reservation has 1-5 items (most have 2-3)
        num_items = random.choices([1, 2, 3, 4, 5], weights=[15, 30, 35, 15, 5])[0]
        reserved_items = random.sample(
            rental_item_ids, min(num_items, len(rental_item_ids))
        )

        for item_id in reserved_items:
            sql = f"INSERT INTO GearReservationItems (Reservation, Item) VALUES ({reservation_id}, {item_id});"
            sql_statements.append(sql)

        reservation_id += 1

    sql_statements.append("")
    sql_statements.append("-- ✅ End of generated fake data")
    sql_statements.append("")

    return sql_statements


def main():
    """Generate fake data and save to file"""
    try:
        sql_statements = generate_fake_data()

        filename = "fake_data_inserts.sql"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(sql_statements))

        print(
            f"\n✅ Success! Generated {len([s for s in sql_statements if s.startswith('INSERT')])} SQL INSERT statements"
        )
        print(f"📁 Saved to: {filename}")
        print(f"\n🚀 To load this data into your database:")
        print(f"   mysql -u your_username -p ClubStack < {filename}")
        print(f"\n📊 Generated data includes:")
        print(f"   • 100 fake members with addresses and contact info")
        print(f"   • 15 additional allergies with user assignments")
        print(f"   • 8 new permission levels with assignments")
        print(f"   • 50 diverse events with realistic details")
        print(f"   • Event signups and waitlists")
        print(f"   • 150+ feedback entries")
        print(f"   • Communications and recipients")
        print(f"   • Budget data for multiple years")
        print(f"   • 12 vendor profiles")
        print(f"   • 30 reimbursement requests")
        print(f"   • 10 additional purchase orders")
        print(f"   • 100 rental gear items")
        print(f"   • 40 merchandise items")

    except Exception as e:
        print(f"❌ Error generating fake data: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

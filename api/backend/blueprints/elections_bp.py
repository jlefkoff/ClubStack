from flask import Blueprint, jsonify, request
from backend.utils.db_utils import execute_query, execute_update
from backend.db_connection import db
from datetime import datetime

elections_bp = Blueprint("elections", __name__)


# ==================== TERMS ====================


# POST /terms - Create term
@elections_bp.route("/terms", methods=["POST"])
def create_term():
    data = request.get_json()
    name = data.get("name")
    start_date = data.get("start_date")
    end_date = data.get("end_date")

    if not name or not start_date or not end_date:
        return jsonify({"error": "Missing required fields"}), 400

    query = """
    INSERT INTO Term (Name, StartDate, EndDate)
    VALUES (%s, %s, %s);
    """
    term_id = execute_update(query, (name, start_date, end_date))

    return jsonify({"message": "Term created", "term_id": term_id}), 201


# GET /terms - View all terms
@elections_bp.route("/terms", methods=["GET"])
def view_terms():
    query = """
    SELECT ID, Name, StartDate, EndDate
    FROM Term
    ORDER BY StartDate DESC;
    """
    return execute_query(query)


# DELETE /<term_id> - Delete term
@elections_bp.route("/terms/<int:term_id>", methods=["DELETE"])
def delete_term(term_id):
    query = """
    DELETE FROM Term WHERE ID = %s;
    """
    execute_update(query, (term_id,))
    return jsonify({"message": "Term deleted successfully"}), 200


# ==================== POSITIONS ====================


# GET /positions - View all positions
@elections_bp.route("/positions", methods=["GET"])
def view_positions():
    query = """
    SELECT ID, Title, BallotOrder
    FROM Position
    ORDER BY BallotOrder;
    """
    return execute_query(query)


# POST /positions - Create position
@elections_bp.route("/positions", methods=["POST"])
def create_position():
    data = request.get_json()
    title = data.get("title")
    ballot_order = data.get("ballot_order")

    if not title or ballot_order is None:
        return jsonify({"error": "Missing required fields"}), 400

    query = """
    INSERT INTO Position (Title, BallotOrder)
    VALUES (%s, %s);
    """
    position_id = execute_update(query, (title, ballot_order))

    return jsonify({"message": "Position created", "position_id": position_id}), 201


# DELETE /positions/<position_id> - Delete position
@elections_bp.route("/positions/<int:position_id>", methods=["DELETE"])
def delete_position(position_id):
    try:
        query = """
    DELETE FROM Position WHERE ID = %s;
    """
        execute_update(query, (position_id,))
        return jsonify({"message": "Position deleted successfully"}), 200
    except Exception as e:
        return (
            jsonify(
                {"error": "Cannot delete due to existing references to this record"}
            ),
            409,
        )


# ==================== ELECTIONS ====================


# POST /elections - Create election
@elections_bp.route("/", methods=["POST"])
def create_election():
    data = request.get_json()
    term_id = data.get("term_id")
    positions = data.get("positions")  # List of position IDs
    date = data.get("date")
    nominate_by = data.get("nominate_by")

    if not term_id or not positions or not date or not nominate_by:
        return jsonify({"error": "Missing required fields"}), 400

    # Create election
    query = """
    INSERT INTO Election (Term, Date, NominateBy)
    VALUES (%s, %s, %s);
    """
    election_id = execute_update(query, (term_id, date, nominate_by))

    # Add positions to election
    for pos_id in positions:
        query = """
        INSERT INTO ElectionPositions (Election, `Position`)
        VALUES (%s, %s);
        """
        execute_update(query, (election_id, pos_id))

    return (
        jsonify(
            {
                "message": "Election created",
                "election_id": election_id,
                "term_id": term_id,
                "positions": positions,
                "date": date,
                "nominate_by": nominate_by,
            }
        ),
        201,
    )


# DELETE /<election_id> - Delete election
@elections_bp.route("/<int:election_id>", methods=["DELETE"])
def delete_election(election_id):
    query = """
    DELETE FROM Election WHERE ID = %s;
    """
    execute_update(query, (election_id,))
    return jsonify({"message": "Election deleted successfully"}), 200


# GET /elections - View all elections
@elections_bp.route("/", methods=["GET"])
def view_elections():
    query = """
    SELECT 
        E.ID,
        E.Date,
        E.NominateBy,
        T.Name as TermName,
        T.StartDate,
        T.EndDate,
        GROUP_CONCAT(P.Title ORDER BY P.BallotOrder) as Positions
    FROM Election E
    JOIN Term T ON E.Term = T.ID
    JOIN ElectionPositions EP ON E.ID = EP.Election
    JOIN Position P ON EP.Position = P.ID
    GROUP BY E.ID
    ORDER BY E.Date DESC;
    """
    return execute_query(query)


# GET /elections/<id> - Get specific election details
@elections_bp.route("/elections/<int:election_id>", methods=["GET"])
def get_election(election_id):
    query = """
    SELECT 
        E.ID,
        E.Date,
        E.NominateBy,
        T.Name as TermName,
        T.StartDate,
        T.EndDate
    FROM Election E
    JOIN Term T ON E.Term = T.ID
    WHERE E.ID = %s;
    """
    cursor = db.get_db().cursor()
    cursor.execute(query, (election_id,))
    election = cursor.fetchall()

    if not election:
        return jsonify({"error": "Election not found"}), 404

    # Get positions for this election
    positions_query = """
    SELECT P.ID, P.Title, P.BallotOrder
    FROM Position P
    JOIN ElectionPositions EP ON P.ID = EP.Position
    WHERE EP.Election = %s
    ORDER BY P.BallotOrder;
    """
    cursor.execute(positions_query, (election_id,))
    positions = cursor.fetchall()
    if not positions:
        return jsonify({"error": "No positions found for this election"}), 404

    return jsonify({"election": election, "positions": positions})


# ==================== NOMINATIONS ====================


# POST /nominations - Submit nomination
@elections_bp.route("/nominations", methods=["POST"])
def nominate_member():
    data = request.get_json()
    nominator = data.get("nominator")
    nominee = data.get("nominee")
    position = data.get("position")

    if not nominator or not nominee or not position:
        return jsonify({"error": "Missing required fields"}), 400

    query = """
    INSERT INTO Nomination (Nominator, Nominee, `Position`, Accepted)
    VALUES (%s, %s, %s, NULL);
    """
    nomination_id = execute_update(query, (nominator, nominee, position))

    return (
        jsonify({"message": "Nomination submitted", "nomination_id": nomination_id}),
        201,
    )


# PUT /nominations/<id>/accept - Accept/decline nomination
@elections_bp.route("/nominations/<int:nomination_id>/accept", methods=["PUT"])
def accept_nomination(nomination_id):
    data = request.get_json()
    accepted = data.get("accepted")  # True/False

    if accepted is None:
        return jsonify({"error": "Missing 'accepted' field"}), 400

    query = """
    UPDATE Nomination 
    SET Accepted = %s 
    WHERE ID = %s;
    """
    execute_update(query, (accepted, nomination_id))

    status = "accepted" if accepted else "declined"
    return jsonify({"message": f"Nomination {status}"}), 200


# GET /nominations/pending/<member_id> - Get pending nominations for member
@elections_bp.route("/nominations/pending/<int:member_id>", methods=["GET"])
def get_pending_nominations(member_id):
    query = """
    SELECT 
        N.ID,
        N.Nominator,
        N.Position,
        P.Title as PositionTitle,
        CONCAT(M1.FirstName, ' ', M1.LastName) as NominatorName,
        E.Date as ElectionDate,
        E.NominateBy
    FROM Nomination N
    JOIN Position P ON N.Position = P.ID
    JOIN Member M1 ON N.Nominator = M1.ID
    JOIN ElectionPositions EP ON N.Position = EP.Position
    JOIN Election E ON EP.Election = E.ID
    WHERE N.Nominee = %s AND N.Accepted IS NULL
    ORDER BY E.Date;
    """
    return execute_query(query, (member_id,))


# GET /nominations/election/<election_id> - Get all nominations for election
@elections_bp.route("/nominations/election/<int:election_id>", methods=["GET"])
def get_election_nominations(election_id):
    query = """
    SELECT 
        N.ID,
        N.Accepted,
        P.Title as PositionTitle,
        P.BallotOrder,
        CONCAT(M1.FirstName, ' ', M1.LastName) as NominatorName,
        CONCAT(M2.FirstName, ' ', M2.LastName) as NomineeName,
        M2.ID as NomineeID
    FROM Nomination N
    JOIN Position P ON N.Position = P.ID
    JOIN Member M1 ON N.Nominator = M1.ID
    JOIN Member M2 ON N.Nominee = M2.ID
    JOIN ElectionPositions EP ON N.Position = EP.Position
    WHERE EP.Election = %s
    ORDER BY P.BallotOrder, M2.LastName;
    """
    return execute_query(query, (election_id,))


# ==================== BALLOTS ====================


# POST /elections/<election_id>/generate-ballots - Generate ballots for election
@elections_bp.route("/elections/<int:election_id>/generate-ballots", methods=["POST"])
def generate_ballots(election_id):
    # Get positions for this election in ballot order
    positions_query = """
    SELECT P.ID, P.Title, P.BallotOrder
    FROM Position P
    JOIN ElectionPositions EP ON P.ID = EP.Position
    WHERE EP.Election = %s
    ORDER BY P.BallotOrder;
    """
    cursor = db.get_db().cursor()
    cursor.execute(positions_query, (election_id,))
    positions = cursor.fetchall()

    print(positions)  # Debugging line to check positions

    if not positions:
        return jsonify({"error": "No positions found for election"}), 400

    ballots_created = []

    for position in positions:
        # Check if already won by someone in this election
        winner_check_query = """
        SELECT COUNT(*) as count
        FROM Winner W
        JOIN ElectionPositions EP ON W.Position = EP.Position
        WHERE EP.Election = %s AND W.Position = %s;
        """
        cursor = db.get_db().cursor()
        cursor.execute(winner_check_query, (election_id, position["ID"]))
        winner_result = cursor.fetchall()

        if winner_result[0]["count"] > 0:
            continue  # Skip if position already has winner

        # Get accepted nominations for this position
        nominations_query = """
        SELECT N.ID
        FROM Nomination N
        JOIN ElectionPositions EP ON N.Position = EP.Position
        WHERE EP.Election = %s AND N.Position = %s AND N.Accepted = TRUE;
        """
        cursor.execute(nominations_query, (election_id, position["ID"]))
        nominations = cursor.fetchall()

        if len(nominations) == 0:
            continue  # Skip if no accepted nominations

        # Create ballot
        ballot_query = """
        INSERT INTO Ballot (`Position`, Election, CreatedAt)
        VALUES (%s, %s, %s);
        """
        ballot_id = execute_update(
            ballot_query, (position["ID"], election_id, datetime.now())
        )

        # Add ballot options
        for nomination in nominations:
            option_query = """
            INSERT INTO BallotOptions (Ballot, Nomination)
            VALUES (%s, %s);
            """
            execute_update(option_query, (ballot_id, nomination["ID"]))

        ballots_created.append(
            {
                "ballot_id": ballot_id,
                "position": position["Title"],
                "options_count": len(nominations),
            }
        )

    return (
        jsonify(
            {
                "message": f"Generated {len(ballots_created)} ballots",
                "ballots": ballots_created,
            }
        ),
        201,
    )


# GET /ballots/member/<member_id> - Get available ballots for member
@elections_bp.route("/ballots/member/<int:member_id>", methods=["GET"])
def get_member_ballots(member_id):
    query = """
    SELECT 
        B.ID as BallotID,
        P.Title as PositionTitle,
        P.BallotOrder,
        E.Date as ElectionDate,
        T.Name as TermName,
        CASE WHEN V.ID IS NOT NULL THEN TRUE ELSE FALSE END as HasVoted
    FROM Ballot B
    JOIN Position P ON B.Position = P.ID
    JOIN Election E ON B.Election = E.ID
    JOIN Term T ON E.Term = T.ID
    LEFT JOIN Vote V ON B.ID = V.Ballot AND V.Member = %s
    ORDER BY P.BallotOrder;
    """
    # WHERE E.Date >= CURDATE()  -- Only show future/current elections
    return execute_query(query, (member_id,))


# GET /ballots/<ballot_id> - Get ballot details with options
@elections_bp.route("/ballots/<int:ballot_id>", methods=["GET"])
def get_ballot_details(ballot_id):
    # Get ballot info
    ballot_query = """
    SELECT 
        B.ID,
        B.CreatedAt,
        P.Title as PositionTitle,
        E.Date as ElectionDate,
        T.Name as TermName
    FROM Ballot B
    JOIN Position P ON B.Position = P.ID
    JOIN Election E ON B.Election = E.ID
    JOIN Term T ON E.Term = T.ID
    WHERE B.ID = %s;
    """
    cursor = db.get_db().cursor()
    cursor.execute(ballot_query, (ballot_id,))
    ballot = cursor.fetchall()

    if not ballot:
        return jsonify({"error": "Ballot not found"}), 404

    # Get ballot options
    options_query = """
    SELECT 
        BO.ID as OptionID,
        CONCAT(M.FirstName, ' ', M.LastName) as CandidateName,
        M.ID as CandidateID
    FROM BallotOptions BO
    JOIN Nomination N ON BO.Nomination = N.ID
    JOIN Member M ON N.Nominee = M.ID
    WHERE BO.Ballot = %s
    ORDER BY M.LastName;
    """
    cursor.execute(options_query, (ballot_id,))
    options = cursor.fetchall()

    return jsonify({"ballot": ballot[0], "options": options})


# ==================== VOTING ====================


# POST /votes - Submit vote
@elections_bp.route("/votes", methods=["POST"])
def submit_vote():
    data = request.get_json()
    member_id = data.get("member_id")
    ballot_id = data.get("ballot_id")
    ballot_option_id = data.get("ballot_option_id")

    if not member_id or not ballot_id or not ballot_option_id:
        return jsonify({"error": "Missing required fields"}), 400

    # Check if member already voted on this ballot
    check_query = """
    SELECT COUNT(*) as count
    FROM Vote
    WHERE Member = %s AND Ballot = %s;
    """
    cursor = db.get_db().cursor()
    cursor.execute(check_query, (member_id, ballot_id))
    existing = cursor.fetchall()

    if existing[0]["count"] > 0:
        return jsonify({"error": "Member has already voted on this ballot"}), 400

    # Submit vote
    vote_query = """
    INSERT INTO Vote (Ballot, Member, BallotOption, VotedAt)
    VALUES (%s, %s, %s, %s);
    """
    vote_id = execute_update(
        vote_query, (ballot_id, member_id, ballot_option_id, datetime.now())
    )

    return jsonify({"message": "Vote submitted successfully", "vote_id": vote_id}), 201


# GET /ballots/<ballot_id>/results - Get voting results
@elections_bp.route("/ballots/<int:ballot_id>/results", methods=["GET"])
def get_ballot_results(ballot_id):
    query = """
    SELECT 
        CONCAT(M.FirstName, ' ', M.LastName) as CandidateName,
        M.ID as CandidateID,
        COUNT(V.ID) as VoteCount
    FROM BallotOptions BO
    JOIN Nomination N ON BO.Nomination = N.ID
    JOIN Member M ON N.Nominee = M.ID
    LEFT JOIN Vote V ON BO.ID = V.BallotOption
    WHERE BO.Ballot = %s
    GROUP BY BO.ID, M.ID
    ORDER BY VoteCount DESC, M.LastName;
    """
    cursor = db.get_db().cursor()
    cursor.execute(query, (ballot_id,))
    results = cursor.fetchall()

    # Get total vote count
    total_query = """
    SELECT COUNT(*) as TotalVotes
    FROM Vote V
    JOIN BallotOptions BO ON V.BallotOption = BO.ID
    WHERE BO.Ballot = %s;
    """
    cursor.execute(total_query, (ballot_id,))
    total_result = cursor.fetchall()
    total_votes = total_result[0]["TotalVotes"] if total_result else 0

    return jsonify({"results": results, "total_votes": total_votes})


# ==================== WINNERS ====================


# POST /ballots/<ballot_id>/declare-winner - Declare winner of ballot
@elections_bp.route("/ballots/<int:ballot_id>/declare-winner", methods=["POST"])
def declare_winner(ballot_id):
    data = request.get_json()
    member_id = data.get("member_id")  # Winner's member ID

    if not member_id:
        return jsonify({"error": "Missing member_id"}), 400

    # Get ballot position
    position_query = """
    SELECT Position FROM Ballot WHERE ID = %s;
    """
    cursor = db.get_db().cursor()
    cursor.execute(position_query, (ballot_id,))
    position_result = cursor.fetchall()

    if not position_result:
        return jsonify({"error": "Ballot not found"}), 404

    position_id = position_result[0]["Position"]

    # Record winner
    winner_query = """
    INSERT INTO Winner (Member, `Position`)
    VALUES (%s, %s);
    """
    winner_id = execute_update(winner_query, (member_id, position_id))

    return (
        jsonify({"message": "Winner declared successfully", "winner_id": winner_id}),
        201,
    )


# GET /elections/<election_id>/winners - Get all winners for election
@elections_bp.route("/elections/<int:election_id>/winners", methods=["GET"])
def get_election_winners(election_id):
    query = """
    SELECT 
        CONCAT(M.FirstName, ' ', M.LastName) as WinnerName,
        M.ID as MemberID,
        P.Title as PositionTitle,
        P.BallotOrder
    FROM Winner W
    JOIN Member M ON W.Member = M.ID
    JOIN Position P ON W.Position = P.ID
    JOIN ElectionPositions EP ON P.ID = EP.Position
    WHERE EP.Election = %s
    ORDER BY P.BallotOrder;
    """
    return execute_query(query, (election_id,))

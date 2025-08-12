from flask import Blueprint, jsonify, request
from backend.utils.db_utils import execute_query, execute_update

elections_bp = Blueprint("elections", __name__)


# POST /election - Create election
@elections_bp.route("/election", methods=["POST"])
def create_election():
  data = request.get_json()
  term_id = data.get("term_id")
  positions = data.get("positions")  # List of position IDs
  date = data.get("date")
  nominate_by = data.get("nominate_by")

  if not term_id or not positions or not date or not nominate_by:
    return jsonify({"error": "Missing required fields"}), 400

  query = """
  INSERT INTO Election (Term, Date, NominateBy)
  VALUES (%s, %s, %s);
  """
  election_id = execute_update(query, (term_id, date, nominate_by))

  for pos_id in positions:
      query = """      INSERT INTO ElectionPositions (Election, `Position`)
      VALUES (%s, %s);
      """
      execute_update(query, (election_id, pos_id))

  return jsonify({
    "message": "Election created",
    "term_id": term_id,
    "positions": positions,
    "date": date,
    "nominate_by": nominate_by
  }), 201

# GET /election - View existing elections
@elections_bp.route("/election", methods=["GET"])
def view_elections():
    query = """
    SELECT E.ID, E.Term, E.Date, E.NominateBy, GROUP_CONCAT(P.Title) AS Positions
    FROM Election E
    JOIN ElectionPositions EP ON E.ID = EP.Election
    JOIN Position P ON EP.Position = P.ID
    GROUP BY E.ID;
    """
    return execute_query(query)

# POST /term - Create term
@elections_bp.route("/term", methods=["POST"])
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
    execute_update(query, (name, start_date, end_date))

    return jsonify({"message": "Term created", "name": name}), 201


# GET /term - View existing terms
@elections_bp.route("/term", methods=["GET"])
def view_terms():
    query = """
    SELECT ID, Name, StartDate, EndDate
    FROM Term;
    """
    return execute_query(query)


# POST /nominations - Nominate member
@elections_bp.route("/nominations", methods=["POST"])
def nominate_member():
  data = request.get_json()
  nominator = data.get("nominator")
  nominee = data.get("nominee")
  position = data.get("position")
  accepted = data.get("accepted", False)

  if not nominator or not nominee or not position:
    return jsonify({"error": "Missing required fields"}), 400

  query = """
  INSERT INTO Nomination (Nominator, Nominee, `Position`, Accepted)
  VALUES (%s, %s, %s, %s);
  """
  execute_update(query, (nominator, nominee, position, accepted))

  return jsonify({
    "message": "Member nominated",
    "nominator": nominator,
    "nominee": nominee,
    "position": position,
    "accepted": accepted
  }), 201


# GET /ballott/<member_id> - Get all ballots available to that member
@elections_bp.route("/ballott/<member_id>", methods=["GET"])
def get_ballotts_for_member(member_id):
    return jsonify({"ballotts": f"List of ballots for member {member_id} (stub)"}), 200


# GET /ballot/<id> - Get a ballot
@elections_bp.route("/ballot/<id>", methods=["GET"])
def get_ballot(id):
    query = """
    SELECT * FROM Ballot WHERE ID = %s;
    """
    return execute_query(query, (id,))

# POST /vote - Vote on Ballot
@elections_bp.route("/vote", methods=["POST"])
def vote_on_ballot():
    data = request.get_json()
    member_id = data.get("member_id")
    ballot_id = data.get("ballot_id")
    choice = data.get("choice")

    if not member_id or not ballot_id or not choice:
        return jsonify({"error": "Missing required fields"}), 400

    query = """
    INSERT INTO Vote (MemberID, BallotID, Choice)
    VALUES (%s, %s, %s);
    """
    execute_update(query, (member_id, ballot_id, choice))

    return jsonify({"message": "Vote submitted"}), 201

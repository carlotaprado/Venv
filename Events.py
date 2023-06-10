from flask import Flask, make_response, jsonify, request
from Flask_MYSQLdb import MySQL
from flask_mysqldb import MySQLdb
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
auth = HTTPBasicAuth()

USER_DATA = {"Login": "Login"}

@auth.verify_password
def verify(username, password):
    if not (username and password):
        return False
    return USER_DATA.get(username) == password


app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PASSWORD'] = '12345678'
app.config['MYSQL_DB'] = 'Events'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

@app.route('/')
def hello_world():
    return "<p>This is my list!</p>"

def data_fetch(query):
    cur = mysql.connection.cursor()
    cur.execute(query)
    data = cur.fetchall()
    return data

@app.route("/events", methods=["GET"])
@auth.login_required
def get_events():
    data = data_fetch("""SELECT * FROM events""")
    return make_response(jsonify(data), 200)

@app.route("/events/<int:id>", methods=["GET"])
@auth.login_required
def get_event_by_id(id):
    data = data_fetch("""SELECT * FROM events WHERE event_id = {}""".format(id))
    return make_response(jsonify(data), 200)

@app.route("/events", methods=['POST'])
@auth.login_required
def add_event():
    cur = mysql.connection.cursor()
    json = request.get_json(force=True)
    event_name = json["event_name"]
    event_date = json["event_date"]
    event_location = json["event_location"]
    cur.execute(
        """ INSERT INTO events (event_name, event_date, event_location) VALUES (%s, %s, %s)""",
        (event_name, event_date, event_location),
    )
    mysql.connection.commit()
    cur.close()
    return make_response(jsonify({"message": "Event added successfully!"}), 200)

@app.route("/events/<int:id>", methods=["PUT"])

@auth.login_required
def update_event_by_id(id):
    cur = mysql.connection.cursor()
    json = request.get_json(force=True)
    event_name = json["event_name"]
    event_date = json["event_date"]
    event_location = json["event_location"]
    cur.execute(
        """UPDATE events SET event_name = %s, event_date = %s, event_location = %s WHERE event_id = %s""",
        (event_name, event_date, event_location, id),
    )
    mysql.connection.commit()
    cur.close()
    return make_response(jsonify({"message": "Event updated successfully!"}), 200)

@app.route("/events/<int:id>", methods=["DELETE"])
@auth.login_required
def delete_event(id):
    cur = mysql.connection.cursor()
    cur.execute("""DELETE FROM events WHERE event_id = %s""", (id,))
    mysql.connection.commit()
    cur.close()
    return make_response(jsonify({"message": "Event deleted successfully"}), 200)

@app.errorhandler(404)
def show_message(error=None):
    message = {
        'status': 404,
        'message': 'Record not found: ' + request.url,
    }
    response = jsonify(message)
    response.status_code = 404
    return response

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, jsonify, redirect, send_file, request
# from flask_cors import CORS for some reason causes error? like wont compile
import bill_tracker_core as core
# import db_interactions as database  # TODO FIX

app = Flask(__name__)
# CORS(app)
# Get config from core
CONFIG = core.CONFIG

global db
# db = database.init_connection_engine()  # TODO FIX


# initialises database pool as a global variable

# example call: database.interact("INSERT INTO bills_db VALUES (1,3,'large bill text')")

# Add more config constants
# CONFIG.update({
#     "key": "value"
# })


# region Bill actions.
# Todo: These could be placed in Bill class, or in core file?
# Returns n in upper case
def cap(n):
    return n.upper()


# Returns n with spaces between each character.
def space(n):
    return " ".join(n)


# Returns the bill with given id in JSON form
def find_bill(id):
    bill = core.Bill(
        "Sample bill",
        "This is a sample bill: a placeholder. Probably for debugging and testing purposes.",
        "1/1/2021",
        "2/1/2022",
        "active",
        short_desc="Sample Bill"
    )
    return bill.to_dict()


def get_top_bills(range):
    bill1 = core.Bill(
        "id_1",
        "Sample bill",
        "This is a sample bill: a placeholder. Probably for debugging and testing purposes.",
        "1/1/2021",
        "2/1/2022",
        "active",
        short_desc="Sample Bill"
    )
    bill2 = core.Bill(
        "id_2",
        "Another Sample bill",
        "This is a different sample bill: an example. Probably for testing purposes.",
        "1/2/2121",
        "2/1/2122",
        "inactive",
        short_desc="Different Sample Bill"
    )

    return [bill1.to_dict(), bill2.to_dict()]


# endregion

# Mapping of "actions" (from URL) to their respective functions
# !! Any function referenced in this dict can be run by anyone !!
safe_actions = {
    "capitalise": cap,
    "space": space,
    "get": find_bill,
}


# Sample private function
# We don't want private functions to be accessible from the internet, so this function should NOT be put in the actions
#   array.
def unsafe_function(n):
    # Do something that shouldn't be accessible publicly
    print("oh dear!")


# Perform action on given bill
@app.route('/<bill_id>/<action>')
def handle_request(bill_id, action):
    # not case-sensitive
    action = action.lower()

    # Run requested action if valiid
    if action in safe_actions:
        result = safe_actions[action](bill_id)
    else:
        result = f"unknown or forbidden action: {action}"

    # Construct output
    output = {
        "bill_id": bill_id,
        "action": action,
        "result": result
    }

    # Convert to json and return
    return jsonify(output)


@app.route('/top')
def top():
    result = get_top_bills(10)
    # Construct output
    output = {
        "result": result
    }

    # Convert to json and return
    return jsonify(output)


@app.route('/')
def landing_page():
    return redirect(CONFIG["default_url"])


# Old (placeholder) login
@app.route('/old_login/<username>/<password>/<notification_token>')  # TODO Delete
def old_login(username, password, notification_token):
    user = core.User("sg2295", "password", "notification token")  # TODO fetch the actual user from DB
    if user.verify_password(password):
        return redirect('/logged_in')  # Placeholder - proof of concept
    else:
        return redirect('/garbage')  # Placeholder - proof of concept


# New login
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    print(username, password)
    # Find user by username in the database. Look at their cookie/session, if it is expired create a new one.
    # Otherwise return it

    return jsonify({'token': 'token_placeholder'})


# New Register
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email_address']
    notifications = request.form['notification_token']
    postcode = request.form['postcode']
    print(username, password, email, notifications, postcode)
    # TODO create and store user

    # log in the user and return the session token

    return jsonify({'token': 'token_placeholder'})


# Deliver requested resource.
# todo: generalise so works with filetypes other than image
('/' + CONFIG["external_res_path"] + '/<name>')
def get_res(name):
    # print(request.mimetype)
    # todo: sort out mimetype. This might affect retrieving images in the future.
    return send_file(CONFIG["img_dir"] + name)

    # return send_file("CONFIG["img_dir"] + core.CONFIG["invalid_img"], mimetype='image/gif')


@app.route("/")
def demo_table_test():
    database.interact("INSERT INTO demo (demo_id, demo_txt) VALUES (123, 'pizza time')")
    return database.select("SELECT * FROM demo_tbl")


if __name__ == '__main__':
    app.run()

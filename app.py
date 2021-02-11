from flask import Flask, jsonify, redirect
import User

app = Flask(__name__)


# region Example bill actions.
# These can be replaced with actions to be performed on the bills (i.e. get, vote, hide)

# Returns n in upper case
def cap(n):
    return n.upper()


# Returns n with spaces between each character.
def space(n):
    return " ".join(n)


# endregion

# Safe public actions to be performed on bills.
# Any function referenced in this dict can be run by anyone
safe_actions = {
    "capitalise": cap,
    "space": space
}


# Sample private function
# We don't want private functions to be accessible from the internet, so this function should NOT be put in the actions
#   array.
def unsafe_function(n):
    # Do something that shouldn't be accessible publicly
    print("hacked!")


@app.route('/<bill_id>/<action>')
def handle_request(bill_id, action):
    # not case-sensitive
    action = action.lower()

    if action in safe_actions:
        result = safe_actions[action](bill_id)
    else:
        result = f"unknown or forbidden action: {action}"

    output = {
        "bill_id": bill_id,
        "action": action,
        "result": result
    }

    return jsonify(output)

# TO MAKE IT WORK. TYPE IN THE LOGIN/USERNAME/PASSWORD and hit enter
# It will then redirect you to the logged_in or garbage page, depending on if you gave it the right password or not
@app.route('/login/<username>/<password>')  # TODO change this it is a really bad practice
def login(username, password):
    user = User.User("sg2295", "password")  # TODO fetch the actual user, no DB setup yet :(
    return redirect('/logged_in') if user.verify_password(password) else redirect('/garbage')


@app.route('/logged_in')
def successful_login():
    return "<h1> you logged in successfully </h1> nice."


@app.route('/garbage')
def garbage_page():
    return "<h1> this is a garbage page </h1> If you are here, you are garbage."


if __name__ == '__main__':
    app.run()

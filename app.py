from flask import Flask, jsonify

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
# We don't want all functions to bes accessible from the internet, so this function should NOT be put in the actions
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


if __name__ == '__main__':
    app.run()

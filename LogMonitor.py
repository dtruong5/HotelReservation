import json
from datetime import date, datetime



def logger(username):
    """
        keep a log of all fail log in attempts under users.json
    """
    with open("users.json", encoding="utf8") as file:
        users = json.loads(file.read())
        for user in users["users"]:
            if user["username"] == username:
                if "attempts" in user.keys():
                    user["attempts"].append({
                        "date": str(date.today()),
                        "time": str(datetime.now().strftime("%H:%M:%S")),
                    })
                else:
                    user["attempts"] = [{
                        "date": str(date.today()),
                        "time": str(datetime.now().strftime("%H:%M:%S")),
                    }]
        json_object = json.dumps(users, indent = 4)
        with open("users.json", "w", encoding="utf8") as outfile:
            outfile.write(json_object)


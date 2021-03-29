def checkNewData(donorDetails, list):
    output = {"isValid": True, "message": " "}
    if donorDetails["password"] != donorDetails["rePassword"]:
        output["isValid"] = False
        output["message"] = " THE PASSWORD DOES NOT MATCH<br> PLEASE TRY AGAIN"

    if len(donorDetails["password"]) <= 8:
        output["isValid"] = False

        output["message"] = "PLEASE ENTER A PASSWORD OF LENGTH ATLEAST 8"

    u, l, n, s = 0, 0, 0, 0

    for i in donorDetails["password"]:
        if i.isupper():
            u += 1
        if i.islower():
            l += 1
        if i.isdigit():
            n += 1
        if i == "@" or i == "$" or i == "_":
            s += 1

    if u == 0 or l == 0 or n == 0 or s == 0:
        output["isValid"] = False

        output[
            "message"
        ] = "PASSWORD MUST HAVE ATLEAST 1 UPPER CASE LETTER, 1 LOWER CASE LETTER AND 1 NUMBER"

    if (u + l + n + s) != len(donorDetails["password"]):
        output["isValid"] = False

        output[
            "message"
        ] = "PASSWORD MUST ONLY CONTAIN LOWER CASE, UPPER CASE, DIGIT AND ($, @, _)"

    if len(donorDetails["userName"]) <= 6:
        output["isValid"] = False

        output["message"] = "PLEASE ENTER A USERNAME OF LENGTH ATLEAST 6"

    count = 0

    for i in donorDetails["userName"]:
        if i.isupper() or i.islower() or i.isdigit() or i == "_":
            count += 1

    if count != len(donorDetails["userName"]):
        output["isValid"] = False

        output[
            "message"
        ] = "USERNAME MUST ONLY CONTAIN LOWER CASE, UPPER CASE, DIGIT AND UNDERSCORE ('_')"

    for i in list:
        if i == donorDetails["userName"]:
            output["isValid"] = False
            output[
                "message"
            ] = "<h5>THIS USERNAME ALREADY EXISTS<br> TRY ANOTHER USER NAME</h5>"
    return output


def checkPassword(passDetails):
    output = {"isValid": True, "message": " "}
    if passDetails["newPassword"] != passDetails["reNewPassword"]:
        output["isValid"] = False
        output[
            "message"
        ] = "<h5>THE NEW PASSWORD DOES NOT MATCH WITH THE RE-ENTERED PASSWORD <br> PLEASE TRY AGAIN</h5>"
    if len(passDetails["newPassword"]) <= 8:
        output["isValid"] = False

        output["message"] = "<h5>PLEASE ENTER A PASSWORD OF LENGTH ATLEAST 8</h5>"

    u, l, n, s = 0, 0, 0, 0

    for i in passDetails["newPassword"]:
        if i.isupper():
            u += 1
        if i.islower():
            l += 1
        if i.isdigit():
            n += 1
        if i == "@" or i == "$" or i == "_":
            s += 1

    if u == 0 or l == 0 or n == 0 or s == 0:
        output["isValid"] = False

        output[
            "message"
        ] = "<h5>PASSWORD MUST HAVE ATLEAST 1 UPPER CASE LETTER, 1 LOWER CASE LETTER AND 1 NUMBER</h5>"

    if (u + l + n + s) != len(passDetails["newPassword"]):
        output["isValid"] = False

        output[
            "message"
        ] = "<h5>PASSWORD MUST ONLY CONTAIN LOWER CASE, UPPER CASE, DIGIT AND ($, @, _)</h5>"
    return output

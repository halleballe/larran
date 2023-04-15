from app import *
import pickle
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from random import choice
app.secret_key = "hemugvgvikgvyxutxlig"
app.config['PERMANENT_SESSION_LIFETIME'] = 9999999999

path_to_users="database/users"
path_to_passwords="database/password_list"
"""welcome. this file handles everything having to do with accunt login, editing and such"""

# before request will run before any page is loaded. Right now it only saves the user in g.
@app.before_request
def before_request():
    nice=False
    if "user_room_nr" in session and "password" in session:
        users = get_all_users()
        for user in users:
            if user.room_nr == session["user_room_nr"] and user.password == session["password"]:
                nice=True
    if not nice:
        session.pop("user_room_nr", None)
        session.pop("password", None)

def require_login():
    if "user_room_nr" in session:
        users = get_all_users()
        for user in users:
            if user.room_nr == session["user_room_nr"]:
                return False
    return True
#this will return the login page
@app.route("/login", methods=["GET"])
def return_login_page():
    session.pop("user_room_nr", None)
    return render_template("Login.html", failed_login = False)

#this will handle login attempt
@app.route("/login", methods=["POST"])
def attempt_login():
    #get room name and password from form
    room_nr = request.form.get("room_nr").upper()
    password = request.form.get("password")
    print(room_nr, password)
    users = get_all_users()
    for user in users:
        print(user.room_nr, user.password)
        print(user.room_nr == room_nr , user.password == password)
        if user.room_nr == room_nr and user.password == password:
            session["user_room_nr"]=room_nr
            session["password"] = password
            return redirect("/timetable")
    return render_template("Login.html" ,failed_login=True)

# this will return the users overview
@app.route("/overview", methods=["GET"])
def users_overview():
    if require_login(): return redirect("/login")
    user = get_user_by_room_nr(session["user_room_nr"])
    admin = user.role=="admin"
    if not admin:
        return "du måste vara inloggad som admin"

    msg=request.args.get('msg')
    print("ooh")
    users = get_all_users()
    print("found", len(users), "users")
    for user in users:
        print(user.room_nr)

    return render_template("user_overview.html", users=get_all_users(), msg=msg, admin=admin)

# this will find the user and then send an email with their passord, if it hasnt been done to many times
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        name = request.form['name'].upper()
        print("Name:", name)
        email = request.form['email']
        print("Email:", email)

        user = get_user_by_room_nr(name)
        if user:
            print(email, user.email)
            if email == user.email:
                date_past=user.emails_sent[0]
                now_date = datetime.now()
                delta = now_date - date_past

                if delta.total_seconds() > (24 * 60 * 60):
                    send_email(user.password, email)
                    user.emails_sent[0]=user.emails_sent[1]
                    user.emails_sent[1]=now_date
                    update_user(user)
                    return render_template('forgot.html', msg="Skickade ett mail. kolla inboxen (och spam)")
                else:
                    return render_template('forgot.html', msg="Whoah! Sakta i backarna. För många mail på 24 timmar.")


            return render_template('forgot.html', msg="rumsnummer och email matchade inte")
        return render_template('forgot.html', msg="rummsnumret finns inte")
    return render_template('forgot.html', msg=False)
# this will handle login attempt
@app.route("/add_new_user", methods=["POST"])
# only god can create new users. creates a new user with room nr and a basic password and saves to Accounts file
def create_new_user():
    print("ok", file=sys.stdout)

    room_nr=request.form["room_nr"].upper()
    if room_nr=="":
        msg="please enter room number"
        return redirect(f"/overview?msg={msg}")
    print(room_nr)

    # check if room nr already has a user ascociated with it
    # get all users
    duplicate = False
    try:
        with open(path_to_users, "rb") as tf:
            users = pickle.load(tf)
    except:
        users = []

    # check if user already exists
    for user in users:
        if user.room_nr == room_nr:
            duplicate = True
            print("duplicate")
            msg= "there is already a user with that room nr. There can only be one user per room nr"

    # check every user for that room nr. If anyone has it, return false, otherwise continue
    if not duplicate:
        new_user = User(room_nr)
        update_user(new_user)

    msg= "successfully created user"

    return redirect(f"/overview?msg={msg}")

@app.route("/handle_user", methods=["POST"])
def handle_user():
    msg=""
    if request.form.get('save') == 'save':
        print("SAVE", request.form)
        # Do something when button 1 is pressed in form 1
        room_nr = request.form["room_nr"]
        if room_nr == session["user_room_nr"]:
            msg="för att ändra i ditt eget konto gå till 'Mitt konto'"
            return redirect(f"/overview?msg={msg}")

        print("so far")
        # create a new user and replace it with the old, effectively resetting it
        password = request.form["text"]
        email = request.form["email"]
        print("ok")


        user = get_user_by_room_nr(room_nr)
        user.password = password
        user.email=email
        user.role = "not admin"
        admin = request.form.get("addd")
        if admin =="on":
            print("he is admin")
            user.role = "admin"

        update_user(user)
        msg="uppdatedare uppgifterna!"
        return redirect(f"/overview?msg={msg}")
    if request.form.get('revert') == 'revert':
        pass

    elif request.form.get('delete') == 'delete':
        print("deletin user")

        # Do something when button 2 is pressed in form 1
        room_nr = request.form["room_nr"]
        if room_nr == session["user_room_nr"]:
            msg="Man kan inte radera sitt egna konto"
            return redirect(f"/overview?msg={msg}")
        user = get_user_by_room_nr(room_nr)
        delete_user(user)
        msg = "deleted user"
    print("oki")
    return redirect(f"/overview?msg={msg}")
class User:
    def __init__(self, room_nr):
        # important stuff
        self.room_nr = room_nr
        #with open(path_to_passwords, "r", encoding="utf-8") as f:
            #all_passwords = f.readlines()
            #password = choice(all_passwords).lower()[:-1]

        #self.password = password
        self.email=""
        self.password="tvätta"+datetime.now().strftime("%Y")
        self.role="not admin"

        yesterday = datetime.now()-timedelta(hours=25)
        self.emails_sent = [yesterday, yesterday]


# function that reads Accounts file and returrn all user objects
def get_all_users():
    try:
        with open(path_to_users, "rb") as tf:
            all_users = pickle.load(tf)

        all_users.sort(key=lambda x: x.room_nr, reverse=False)
        return all_users

    except:
        return []


# function to update users file
def update_user(updated_user):
    try:
        with open(path_to_users, "rb") as tf:
            users = pickle.load(tf)
    except:
        users = []

    # check if user already exists
    for user in users:
        if user.room_nr == updated_user.room_nr:
            users.remove(user)
    users.append(updated_user)

    with open(path_to_users, "wb") as tf:
        pickle.dump(users, tf)


# function to delete a user
def delete_user(user_to_delete):
    try:
        with open(path_to_users, "rb") as tf:
            users = pickle.load(tf)
    except:
        users = []

    # check if user already exists
    for user in users:
        if user.room_nr == user_to_delete.room_nr:
            users.remove(user)

    with open(path_to_users, "wb") as tf:
        pickle.dump(users, tf)


# function to get user by room_nr
def get_user_by_room_nr(room_nr):
    try:
        with open(path_to_users, "rb") as tf:
            users = pickle.load(tf)
    except:
        users = []

    # check if user already exists
    for user in users:
        if user.room_nr == room_nr:
            return user

@app.route("/handle_account", methods=["GET"])
def manage_account(msg="hantera ditt konto", tone="primary"):
    print(msg)
    if require_login(): return redirect("/login")
    user=get_user_by_room_nr(session["user_room_nr"])
    return render_template("handle_account.html", msg = msg, tone=tone, username=user.room_nr ,email=user.email)

@app.route("/handle_account", methods=["POST"])
def handle_account():
    if require_login(): return redirect("/login")

    if "password" in request.form:
        password = request.form.get("password")
        repeat_password=request.form.get("repeat_password")
        print("hejhallå",password, repeat_password)
        room_nr = session["user_room_nr"]
        users = get_all_users()
        for user in users:
            if user.room_nr == room_nr:
                if password and repeat_password:
                    if password == repeat_password:
                        user.password = password
                        session["password"]=password
                        update_user(user)
                        return manage_account(msg="uppdaterade ditt lösenord!", tone="success")
                    else:
                        return manage_account(msg="lösenord och bekräfta lösenord matchade inte.", tone="danger")


    email = request.form.get("email")
    print (email)
    room_nr = session["user_room_nr"]
    users = get_all_users()
    for user in users:
        if user.room_nr == room_nr:
            if email:
                user.email=email
                update_user(user)
                print(email)
                return manage_account(msg="uppdaterade din mailaddress!", tone="success")
            else:
                return manage_account(msg="Det är viktigt att ha en mailaddress om du glömmer ditt lösenord", tone="danger")

    return manage_account(msg="Hantera ditt konto", tone="primary")

@app.route("/logout", methods=["GET"])
def logout():
    session.pop("user_room_nr", None)
    return redirect("/timetable")


def send_email(password, recipient):
    gmail_user = 'spelare.nr.1@gmail.com'
    gmail_password = 'vlmxbggmcpcultmv'


    # Create message container - the correct MIME type is multipart/alternative
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Glömt lösenord'
    msg['From'] = gmail_user
    msg['To'] = recipient

    # Create the HTML message
    html = f"""
    <!DOCTYPE html>
<html lang="en"><head>
  <title>Logga in</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>

  <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/popper.js@1.14.7/dist/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
</head>

<body class="bg-light">
<div class="container-sm-3 p-0">
  <div class="d-flex justify-content-center">
      <div class="border p-5 bg-white" style="max-width:500px">
        <form method="POST">

          

          <!-- Password input -->
          <div class="form-outline mb-4">
              <label class="form-label" for="form2Example2">Glömde du ditt lösenord till larrans tvättider? Här är ditt lösenord:</label>
              <input type="text" name="password" id="form2Example2" class="form-control" placeholder="jättehemligtlösenord" value={password}>
          </div>


          
          <div class="row pe-3 ps-3">

          </div>
          <div class="row ">
            <a href="/forgot-password"> tvättider</a>
            <p><br>Begärde du inte det här mailet är det bara att ignorera.<br> Får du många sådana här mail, kontakta mig, Leo Lindahl<br>iMessage: Leo Lindahl<br>mail: leo.lindahl@gmail.com</p>
          </div>

        </form>
      </div>
  </div>
</div>
</body></html>
       """

    # Record the MIME type - text/html
    part1 = MIMEText(html, 'html')

    # Attach parts into message container
    msg.attach(part1)

    # Send the message via Gmail SMTP server
    try:
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.ehlo()
        smtp_server.login(gmail_user, gmail_password)
        smtp_server.sendmail(gmail_user, msg['To'], msg.as_string())
        smtp_server.close()
        print('Email sent successfully!')
    except Exception as ex:
        print('Something went wrong: ', ex)


@app.route("/password/<password>", methods=["GET"])
def show_password(password):
    return render_template("password.html", password = password)
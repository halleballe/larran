from app import *
from bookmaker import *
from account_manager import require_login, get_user_by_room_nr
@app.route('/timetable', methods=["GET"])
def show_timetable():
    login_first =  require_login()
    #hey, do we need to add more timeslots?
    timeslots = get_all_timeslots()
    if len(timeslots)<49*2:
        generate_timeslots()
    if len(timeslots)<49*2:
        generate_timeslots()
    clear_up()
    # get all timeslots. figure oyt thier weekday. append them to a 3 dimensional list with N weeks and 7 days
    weeks = 3
    timetable = []
    timeslots = get_all_timeslots()

    n_week = -1
    has_increased_week = False
    for slot in timeslots:
        # every monday, increase n_week
        if slot.start_time.weekday() == 0 and not has_increased_week:
            n_week+=1
            timetable.append([[] for y in range(7)])
            has_increased_week = True

        if slot.start_time.weekday() == 1:
            has_increased_week = False

        timetable[-1][slot.start_time.weekday()].append(slot)


    #is teh user an admin?
    admin=False
    if not require_login():
        user = get_user_by_room_nr(session["user_room_nr"])
        if user.role=="admin":
            admin = True
    print("timetable ", timetable)

    #har användaren en redan bokad tid?
    user_bookings= []
    msg=""
    if not login_first:
        email = user.email
        if email =="":
            msg = "Impotant! Please enter your email <a href='/manage_account'>here</a>. In case you forget your password"
        all_timeslots=get_all_timeslots()
        for timeslot in all_timeslots:
            if session["user_room_nr"]==timeslot.booker[0]:
                #du har bokat rum (slot, tvättsuga nr)
                user_bookings.append((timeslot,"1"))
            if session["user_room_nr"]==timeslot.booker[1]:
                #du har bokat rum 2
                user_bookings.append((timeslot, "2"))


    return render_template("Schedule.html", timetable=timetable, login_first=login_first, user_bookings=user_bookings, admin=admin, msg = msg)

@app.route("/timetable/<slot_id>", methods=["GET"])
def booking_popup(slot_id):
    try:
        msg  = request.args.get("msg")
    except:
        msg=""

    if require_login(): return redirect("/login")
    print(slot_id)

    # get the timeslot
    timeslot = 0
    all_timeslots = get_all_timeslots()
    for slot in all_timeslots:
        if slot.start_time.strftime("%y%m%d%H") == slot_id:
            timeslot = slot
            break
    h1=timeslot.start_time+timedelta(hours=1)
    h2 = timeslot.end_time + timedelta(hours=1)
    h1=h1.strftime("%H")
    h2 = h2.strftime("%H")
    # display the popup
    if timeslot.booker[0]:
        msg1 = f"Tvättrum 1: bokat av {timeslot.booker[0]}"
    else:
        msg1 = "Tvättrum 1: ledigt"
    if timeslot.booker[1]:
        msg2 = f"Tvättrum 2: bokat av {timeslot.booker[1]}"
    else:
        msg2 = "Tvättrum 2: ledigt"

    return render_template("book_popup.html", slot = timeslot, msg1=msg1, msg2=msg2,msg=msg, user= session["user_room_nr"], h1=h1, h2=h2)

@app.route("/timetable/<slot_id>", methods=["POST"])
def try_to_book(slot_id):
    if require_login(): return redirect("/login")
    # get the timeslot object from sessions
    # get the button that was pressd
    # book the timeslot for the room that was pressed
    print(slot_id)
    # get the timeslot
    timeslot = 0
    all_timeslots = get_all_timeslots()
    for slot in all_timeslots:
        if slot.start_time.strftime("%y%m%d%H") == slot_id:
            timeslot = slot
            break

    # can the user book?
    user_bookings=0
    all_timeslots = get_all_timeslots()
    for tumslot in all_timeslots:
        if session["user_room_nr"] == tumslot.booker[0]:
            # du har bokat rum (slot, tvättsuga nr)
            user_bookings+=1
        if session["user_room_nr"] == tumslot.booker[1]:
            # du har bokat rum 2
            user_bookings+=1

    max_bookings = get_max_bookings()





    if request.form.get('1') == '1':
        if user_bookings >= max_bookings:
            msg = f"you can only have {max_bookings} reservations at a time. cancel one of your existing reservations first"
            return redirect(f"/timetable/{slot_id}?msg={msg}")
        else:
            print(timeslot.book(1,session["user_room_nr"]))
            print("bookin")
    if request.form.get('2') == '2':
        if user_bookings >= max_bookings:
            msg = f"you can only have {max_bookings} bookings at a time. cancel one of your existing reservations first"
            return redirect(f"/timetable/{slot_id}?msg={msg}")
        else:
            print(timeslot.book(2, session["user_room_nr"]))
            print("bookin")
    if request.form.get('2avboka') == '2avboka':
        print(timeslot.cancel(2, session["user_room_nr"]))
        print("CANCEL")
    if request.form.get('1avboka') == '1avboka':
        print(timeslot.cancel(1, session["user_room_nr"]))
        print("CANCEL")

    return redirect(f"/timetable/{slot_id}")

@app.route("/template", methods=["POST"])
def start_over():
    admin=False
    if not require_login():
        user = get_user_by_room_nr(session["user_room_nr"])
        if user.role=="admin":
            admin = True
    if not admin:
        return "only admin allowed, please <a href='/login'>Login</a"


    if request.form.get("start"):
        start_hour = int(request.form["start"])
        end_hour = int(request.form["end"])
        generate_generic_template(start_hour, 2,  end_hour)
        return redirect("/template")
    else:
        max_bookings = request.form["nr"]
        max_bookings = int(max_bookings)
        set_max_bookings(max_bookings)
        return redirect("/template")

@app.route("/template", methods=["GET"])
def template():
    login_first = require_login()
    # hey, do we need to add more timeslots?

    # get all timeslots. figure oyt thier weekday. append them to a 3 dimensional list with N weeks and 7 days
    weeks = 1
    timetable = []
    timeslots = get_template()

    n_week = -1
    has_increased_week = False
    for slot in timeslots:
        # every monday, increase n_week
        if slot.start_time.weekday() == 0 and not has_increased_week:
            n_week += 1
            timetable.append([[] for y in range(7)])
            has_increased_week = True

        if slot.start_time.weekday() == 1:
            has_increased_week = False

        timetable[-1][slot.start_time.weekday()].append(slot)
    print("timetable ", timetable)

    # har användaren en redan bokad tid?
    user_bookings = []
    if not login_first:
        all_timeslots = get_all_timeslots()
        for timeslot in all_timeslots:
            if session["user_room_nr"] == timeslot.booker[0]:
                # du har bokat rum (slot, tvättsuga nr)
                user_bookings.append((timeslot, "1"))
            if session["user_room_nr"] == timeslot.booker[1]:
                # du har bokat rum 2
                user_bookings.append((timeslot, "2"))

    admin=False
    if not require_login():
        user = get_user_by_room_nr(session["user_room_nr"])
        if user.role=="admin":
            admin = True
    if not admin:
        return "only admin allowed, please <a href='/login'>Login</a"

    return render_template("template_maker.html", timetable=timetable, login_first=login_first, admin=admin, max_bookings=get_max_bookings())

@app.route("/template/<slot_id>", methods=["GET", "POST"])
def toggle_bookable(slot_id):
    if require_login(): return "Bara admin får ändra mallen"
    # toggle bookable
    #find slot in templates
    slots = get_template()
    for slot in slots:
        if slot.start_time.strftime("%y%m%d%H")==slot_id:
            if slot.rooms_left==2:
                slot.rooms_left=0
                slot.booker=["ingen", "ingen"]
            else:
                slot.rooms_left=2
    save_template(slots)

    return redirect("/template")


@app.route("/symbols", methods=["GET","POST"])
def symbols():
    return render_template("laundry_guide.html")

@app.route("/stains", methods=["GET","POST"])
def stains():
    return render_template("stains.html")
from app import *
from datetime import datetime
from account_manager import *
from timetable import *
@app.route('/')
def hello_world():
    return redirect("/timetable")

@app.route('/f')
def hi():
    return 'din mamma på pizza'

#app.run()


# getting the time from the current date and time in the given format
#app.run()


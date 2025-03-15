# Importing the Flask Framework

from flask import *
import database
import configparser
import random



# appsetup

page = {}
session = {}

# Initialise the FLASK application
app = Flask(__name__)
app.secret_key = 'SoMeSeCrEtKeYhErE'



# Debug = true if you want debug output on error ; change to false if you dont
app.debug = True


# Read my unikey to show me a personalised app
config = configparser.ConfigParser()
config.read('config.ini')
dbuser = config['DATABASE']['user']
portchoice = config['FLASK']['port']
if portchoice == '10000':
    print('ERROR: Please change config.ini as in the comments or Lab instructions')
    exit(0)

session['isadmin'] = False

###########################################################################################
###########################################################################################
####                                 Database operative routes                         ####
###########################################################################################
###########################################################################################



#####################################################
##  INDEX
#####################################################

# What happens when we go to our website (home page)
@app.route('/')
def index():
    # If the user is not logged in, then make them go to the login page
    if( 'logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    page['username'] = dbuser
    page['title'] = 'Welcome'
    return render_template('welcome.html', session=session, page=page)

#####################################################
# User Login related                        
#####################################################
# login
@app.route('/login', methods=['POST', 'GET'])
def login():
    page = {'title' : 'Login', 'dbuser' : dbuser}
    # If it's a post method handle it nicely
    if(request.method == 'POST'):
        # Get our login value
        val = database.check_login(request.form['userid'], request.form['password'])
        print(val)
        print(request.form)
        # If our database connection gave back an error
        if(val == None):
            errortext = "Error with the database connection."
            errortext += "Please check your terminal and make sure you updated your INI files."
            flash(errortext)
            return redirect(url_for('login'))

        # If it's null, or nothing came up, flash a message saying error
        # And make them go back to the login screen
        if(val is None or len(val) < 1):
            flash('There was an error logging you in')
            return redirect(url_for('login'))

        # If it was successful, then we can log them in :)
        print(val[0])
        session['name'] = val[0]['firstname']
        session['userid'] = request.form['userid']
        session['logged_in'] = True
        session['isadmin'] = val[0]['isadmin']
        return redirect(url_for('index'))
    else:
        # Else, they're just looking at the page :)
        if('logged_in' in session and session['logged_in'] == True):
            return redirect(url_for('index'))
        return render_template('index.html', page=page)

# logout
@app.route('/logout')
def logout():
    session['logged_in'] = False
    flash('You have been logged out')
    return redirect(url_for('index'))



########################
#List All Items#
########################

@app.route('/users')
def list_users():
    '''
    List all rows in users by calling the relvant database calls and pushing to the appropriate template
    '''
    # connect to the database and call the relevant function
    users_listdict = database.list_users()

    # Handle the null condition
    if (users_listdict is None):
        # Create an empty list and show error message
        users_listdict = []
        flash('Error, there are no rows in users')
    page['title'] = 'List Contents of users'
    return render_template('list_users.html', page=page, session=session, users=users_listdict)
    

########################
#List Single Items#
########################


@app.route('/users/<userid>')
def list_single_users(userid):
    '''
    List all rows in users that match a particular id attribute userid by calling the 
    relevant database calls and pushing to the appropriate template
    '''

    # connect to the database and call the relevant function
    users_listdict = None
    users_listdict = database.list_users_equifilter("userid", userid)

    # Handle the null condition
    if (users_listdict is None or len(users_listdict) == 0):
        # Create an empty list and show error message
        users_listdict = []
        flash('Error, there are no rows in users that match the attribute "userid" for the value '+userid)
    page['title'] = 'List Single userid for users'
    return render_template('list_users.html', page=page, session=session, users=users_listdict)


########################
#List Search Items#
########################

@app.route('/consolidated/users')
def list_consolidated_users():
    '''
    List all rows in users join userroles 
    by calling the relvant database calls and pushing to the appropriate template
    '''
    # connect to the database and call the relevant function
    users_userroles_listdict = database.list_consolidated_users()

    # Handle the null condition
    if (users_userroles_listdict is None):
        # Create an empty list and show error message
        users_userroles_listdict = []
        flash('Error, there are no rows in users_userroles_listdict')
    page['title'] = 'List Contents of Users join Userroles'
    return render_template('list_consolidated_users.html', page=page, session=session, users=users_userroles_listdict)

@app.route('/user_stats')
def list_user_stats():
    '''
    List some user stats
    '''
    # connect to the database and call the relevant function
    user_stats = database.list_user_stats()

    # Handle the null condition
    if (user_stats is None):
        # Create an empty list and show error message
        user_stats = []
        flash('Error, there are no rows in user_stats')
    page['title'] = 'User Stats'
    return render_template('list_user_stats.html', page=page, session=session, users=user_stats)

@app.route('/users/search', methods=['POST', 'GET'])
def search_users_byname():
    '''
    List all rows in users that match a particular name
    by calling the relevant database calls and pushing to the appropriate template
    '''
    if(request.method == 'POST'):

        search = database.search_users_customfilter(request.form['searchfield'],"~",request.form['searchterm'])
        print(search)
        
        users_listdict = None

        if search == None:
            errortext = "Error with the database connection."
            errortext += "Please check your terminal and make sure you updated your INI files."
            flash(errortext)
            return redirect(url_for('index'))
        if search == None or len(search) < 1:
            flash(f"No items found for search: {request.form['searchfield']}, {request.form['searchterm']}")
            return redirect(url_for('index'))
        else:
            
            users_listdict = search
            # Handle the null condition'
            print(users_listdict)
            if (users_listdict is None or len(users_listdict) == 0):
                # Create an empty list and show error message
                users_listdict = []
                flash('Error, there are no rows in users that match the searchterm '+request.form['searchterm'])
            page['title'] = 'Users search by name'
            return render_template('list_users.html', page=page, session=session, users=users_listdict)
            

    else:
        return render_template('search_users.html', page=page, session=session)



@app.route('/users/delete/<userid>')
def delete_user(userid):
    '''
    Delete a user
    '''
    # connect to the database and call the relevant function
    resultval = database.delete_user(userid)
    
    page['title'] = f'List users after user {userid} has been deleted'
    return redirect(url_for('list_consolidated_users'))
    
@app.route('/users/update', methods=['POST','GET'])
def update_user():
    """
    Update details for a user
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    
    # Need a check for isAdmin

    page['title'] = 'Update user details'

    userslist = None

    print("request form is:")
    newdict = {}
    print(request.form)

    validupdate = False
    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that at least one value is available:
        if ('userid' not in request.form):
            # should be an exit condition
            flash("Can not update without a userid")
            return redirect(url_for('list_users'))
        else:
            newdict['userid'] = request.form['userid']
            print("We have a value: ",newdict['userid'])

        if ('firstname' not in request.form):
            newdict['firstname'] = None
        else:
            validupdate = True
            newdict['firstname'] = request.form['firstname']
            print("We have a value: ",newdict['firstname'])

        if ('lastname' not in request.form):
            newdict['lastname'] = None
        else:
            validupdate = True
            newdict['lastname'] = request.form['lastname']
            print("We have a value: ",newdict['lastname'])

        if ('userroleid' not in request.form):
            newdict['userroleid'] = None
        else:
            validupdate = True
            newdict['userroleid'] = request.form['userroleid']
            print("We have a value: ",newdict['userroleid'])

        if ('password' not in request.form):
            newdict['password'] = None
        else:
            validupdate = True
            newdict['password'] = request.form['password']
            print("We have a value: ",newdict['password'])

        print('Update dict is:')
        print(newdict, validupdate)

        if validupdate:
            #forward to the database to manage update
            userslist = database.update_single_user(newdict['userid'],newdict['firstname'],newdict['lastname'],newdict['userroleid'],newdict['password'])
        else:
            # no updates
            flash("No updated values for user with userid")
            return redirect(url_for('list_users'))
        # Should redirect to your newly updated user
        return list_single_users(newdict['userid'])
    else:
        return redirect(url_for('list_consolidated_users'))

######
## Edit user
######
@app.route('/users/edit/<userid>', methods=['POST','GET'])
def edit_user(userid):
    """
    Edit a user
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    
    # Need a check for isAdmin

    page['title'] = 'Edit user details'

    users_listdict = None
    users_listdict = database.list_users_equifilter("userid", userid)

    # Handle the null condition
    if (users_listdict is None or len(users_listdict) == 0):
        # Create an empty list and show error message
        users_listdict = []
        flash('Error, there are no rows in users that match the attribute "userid" for the value '+userid)

    userslist = None
    print("request form is:")
    newdict = {}
    print(request.form)
    user = users_listdict[0]
    validupdate = False

    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that at least one value is available:
        if ('userid' not in request.form):
            # should be an exit condition
            flash("Can not update without a userid")
            return redirect(url_for('list_users'))
        else:
            newdict['userid'] = request.form['userid']
            print("We have a value: ",newdict['userid'])

        if ('firstname' not in request.form):
            newdict['firstname'] = None
        else:
            validupdate = True
            newdict['firstname'] = request.form['firstname']
            print("We have a value: ",newdict['firstname'])

        if ('lastname' not in request.form):
            newdict['lastname'] = None
        else:
            validupdate = True
            newdict['lastname'] = request.form['lastname']
            print("We have a value: ",newdict['lastname'])

        if ('userroleid' not in request.form):
            newdict['userroleid'] = None
        else:
            validupdate = True
            newdict['userroleid'] = request.form['userroleid']
            print("We have a value: ",newdict['userroleid'])

        if ('password' not in request.form):
            newdict['password'] = None
        else:
            validupdate = True
            newdict['password'] = request.form['password']
            print("We have a value: ",newdict['password'])

        print('Update dict is:')
        print(newdict, validupdate)

        if validupdate:
            #forward to the database to manage update
            userslist = database.update_single_user(newdict['userid'],newdict['firstname'],newdict['lastname'],newdict['userroleid'],newdict['password'])
        else:
            # no updates
            flash("No updated values for user with userid")
            return redirect(url_for('list_users'))
        # Should redirect to your newly updated user
        return list_single_users(newdict['userid'])
    else:
        # assuming GET request, need to setup for this
        return render_template('edit_user.html',
                           session=session,
                           page=page,
                           userroles=database.list_userroles(),
                           user=user)


######
## add items
######

    
@app.route('/users/add', methods=['POST','GET'])
def add_user():
    """
    Add a new User
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    
    # Need a check for isAdmin

    page['title'] = 'Add user details'

    userslist = None
    print("request form is:")
    newdict = {}
    print(request.form)

    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that all values are available:
        if ('userid' not in request.form):
            # should be an exit condition
            flash("Can not add user without a userid")
            return redirect(url_for('add_user'))
        else:
            newdict['userid'] = request.form['userid']
            print("We have a value: ",newdict['userid'])

        if ('firstname' not in request.form):
            newdict['firstname'] = 'Empty firstname'
        else:
            newdict['firstname'] = request.form['firstname']
            print("We have a value: ",newdict['firstname'])

        if ('lastname' not in request.form):
            newdict['lastname'] = 'Empty lastname'
        else:
            newdict['lastname'] = request.form['lastname']
            print("We have a value: ",newdict['lastname'])

        if ('userroleid' not in request.form):
            newdict['userroleid'] = 1 # default is traveler
        else:
            newdict['userroleid'] = request.form['userroleid']
            print("We have a value: ",newdict['userroleid'])

        if ('password' not in request.form):
            newdict['password'] = 'blank'
        else:
            newdict['password'] = request.form['password']
            print("We have a value: ",newdict['password'])

        print('Insert parametesrs are:')
        print(newdict)

        database.add_user_insert(newdict['userid'], newdict['firstname'],newdict['lastname'],newdict['userroleid'],newdict['password'])
        # Should redirect to your newly updated user
        print("did it go wrong here?")
        return redirect(url_for('list_consolidated_users'))
    else:
        # assuming GET request, need to setup for this
        return render_template('add_user.html',
                           session=session,
                           page=page,
                           userroles=database.list_userroles())

########################
#List All Items#
########################

@app.route('/airports')
def list_airports():
    page_no = request.args.get('page_no',1, type = int)
    per_page = 10
    start = (page_no-1)*per_page
    end = start + per_page
    '''
    List all rows in airport by calling the relvant database calls and pushing to the appropriate template
    '''
    # connect to the database and call the relevant function
    airports_listdict = database.list_airports()
    # airports_listdict = []
    
    total = (len(airports_listdict) + per_page -1)//per_page
    items_on_page = airports_listdict[start:end]
    # Handle the null condition
    if (airports_listdict is None):
        # Create an empty list and show error message
        airports_listdict = []
        flash('Error, there are no rows in airports')
    if (airports_listdict == []):
        flash('No Airports found')
        page_no = 0
    page['title'] = 'List Contents of airports'
    return render_template('list_airports.html', page=page, session=session, airports=items_on_page, total = total, page_no = page_no)

@app.route('/airports/delete/<airportid>')
def delete_airport(airportid):
    '''
    Delete a user
    '''
    # connect to the database and call the relevant function
    if( session['isadmin'] != True ):
        flash(f"Error, Unable to view")
        return redirect(url_for('index'))
    
    resultval = database.delete_airport(airportid)
    
    page['title'] = f'List users after user {airportid} has been deleted'
    return redirect(url_for('list_airports'))

def check_iatacode(iatacode, airportid = -1): # not repeats of iatacode 
    dict = database.list_airports()
    try:
        airportid = int(airportid)
        for airport in dict:
            curr_iatacode = airport['iatacode']
            if curr_iatacode == iatacode:
                if airportid == -1 or int(airport['airportid'])!= airportid:
                    return False
        return True
    except:
        return False

@app.route('/airports/add', methods=['POST','GET'])
def add_airport():
    """
    Add a new Airport
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    
    if( session['isadmin'] != True ):
        flash(f"Error unable to view")
        return redirect(url_for('index'))
    
    page['title'] = 'Add airport details'

    userslist = None
    print("request form is:")
    newdict = {}
    print(request.form)

    # Check your incoming parameters
    if(request.method == 'POST'):

        
        if ('name' not in request.form):
            flash("Can not add airport without a Aiport name")
            return redirect(url_for('add_airport'))
        else:
            newdict['name'] = str(request.form['name'])
            if len(newdict['name'])==0 or len(newdict['name'])>100:
                print("Airport name not present")
                flash("Invalid Airport Name")
                return redirect(url_for('add_airport'))
            print("We have a value: ",newdict['name'])

        if ('iatacode' not in request.form):
            flash("Can not add airport without a IATACODE")
            return redirect(url_for('add_airport'))
        else:
            newdict['iatacode'] = str(request.form['iatacode'])
            if not (len(newdict['iatacode'])==3):
                print("too long")
                flash("IATA Code too short/long")
                return redirect(url_for('add_airport'))
            if not check_iatacode(newdict['iatacode']):
                print("IATA Code already in database")
                flash("IATA Code is invalid") # already in use
                return redirect(url_for('add_airport'))
            print("We have a value: ",newdict['iatacode'])

        if ('city' not in request.form):
            # newdict['city'] = 1
            flash("Can not add airport without a city")
            return redirect(url_for('add_airport'))
        else:
            newdict['city'] = str(request.form['city'])
            if len(newdict['city'])==0 or len(newdict['city'])>100:
                print("City not present")
                flash("Invalid City")
                return redirect(url_for('add_airport'))
            print("We have a value: ",newdict['city'])

        if ('country' not in request.form):
            # newdict['country'] = 'blank'
            flash("Can not add airport without a country")
            return redirect(url_for('add_airport'))
        else:
            newdict['country'] = str(request.form['country'])
            if len(newdict['country'])==0 or len(newdict['country'])>100:
                print("Country not present")
                flash("Invalid Country")
                return redirect(url_for('add_airport'))
            print("We have a value: ",newdict['country'])

        print('Insert parametesrs are:')
        print(newdict)
        new_id = airportid_genrate()
        database.add_airport(str(new_id), newdict['name'],newdict['iatacode'],newdict['city'],newdict['country'])
        # Should redirect to your newly updated user
        print("did it go wrong here?")
        return redirect(url_for('list_airports'))
    else:
        # assuming GET request, need to setup for this
        return render_template('add_airport.html',
                           session=session,
                           page=page)
    
@app.route('/airports/search', methods=['POST', 'GET'])
def search_airports_byID():
    '''
    List all rows in airports that match a particular name
    by calling the relevant database calls and pushing to the appropriate template
    '''
    if( session['isadmin'] != True ):
        flash(f"Error, Unable to view")
        return redirect(url_for('index'))
    
    if(request.method == 'POST'):
        try:
            search = database.search_airports_customfilter("=",int(request.form['searchterm']))
        except:
            flash(f"No items found for search: {request.form['searchterm']}")
            return redirect(url_for('index'))
        
        print(search)
        
        airport_listdict = None

        if search == None or len(search) < 1:
            flash(f"No items found for search: {request.form['searchterm']}")
            return redirect(url_for('index'))
        else:
            airport_listdict = search
            page_no = request.args.get('page_no',1, type = int)
            per_page = 10
            start = (page_no-1)*per_page
            end = start + per_page
            total = (len(airport_listdict) + per_page -1)//per_page
            items_on_page = airport_listdict[start:end]
            
            # Handle the null condition'
            print(airport_listdict)
            if (airport_listdict is None or len(airport_listdict) == 0):
                # Create an empty list and show error message
                airport_listdict = []
                flash('Error, there are no rows in airports that match the searchterm '+request.form['searchterm'])
            page['title'] = 'Airports search by name'
            return render_template('list_airports.html', page=page, session=session, airports=items_on_page, total=total,page_no=page_no)
    else:
        return render_template('search_airports.html', page=page, session=session)
    
######
## Update Airport
######
@app.route('/airports/update/<airportid>', methods=['POST','GET'])
def update_airport(airportid):
    """
    Update a Airport
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    
    if( session['isadmin'] != True ):
        flash(f"Error, Unable to view")
        return redirect(url_for('list_airports'))
    
    page['title'] = 'Update airport details'

    airport_listdict = None
    airport_listdict = database.list_airports_equifilter("airportid", airportid)

    # Handle the null condition
    if (airport_listdict is None or len(airport_listdict) == 0):
        # Create an empty list and show error message
        airport_listdict = []
        flash('Error, there are no rows in users that match the attribute "airportid" for the value '+airportid)
    else:
       
        print("request form is:")
        newdict = {}
        print(request.form)
        airport = airport_listdict[0]
        validupdate = False

        # Check your incoming parameters
        if(request.method == 'POST'):

            if ('name' not in request.form):
                newdict['name'] = None
            else:
                validupdate = True
                newdict['name'] = request.form['name']
                if len(newdict['name'])==0 or len(newdict['name'])>100:
                    print("Airport name not present")
                    flash("Invalid Airport name")
                    return redirect(url_for('list_airports'))
                print("We have a value: ",newdict['name'])

            if ('iatacode' not in request.form):
                newdict['iatacode'] = None
            else:
                validupdate = True
                newdict['iatacode'] = request.form['iatacode']
                if not len(newdict['iatacode'])==3:
                    print("too long")
                    flash("IATACODE too short/long")
                    return redirect(url_for('list_airports'))
                if not check_iatacode(newdict['iatacode'], airportid):
                    print("IATA Code already in database")
                    flash("IATA Code is invalid") # already in use
                    return redirect(url_for('list_airports'))
                print("We have a value: ",newdict['iatacode'])

            if ('city' not in request.form):
                newdict['city'] = None
            else:
                validupdate = True
                newdict['city'] = request.form['city']
                if len(newdict['city'])==0 or len(newdict['city'])>100:
                    print("City not present")
                    flash("Invalid City")
                    return redirect(url_for('list_airports'))
                print("We have a value: ",newdict['city'])

            if ('country' not in request.form):
                newdict['country'] = None
            else:
                validupdate = True
                newdict['country'] = request.form['country']
                if len(newdict['country'])==0 or len(newdict['country'])>100:
                    print("Country not present")
                    flash("Invalid Country")
                    return redirect(url_for('list_airports'))
                print("We have a value: ",newdict['country'])

            print('Update dict is:')
            print(newdict, validupdate)

            if validupdate:
                #forward to the database to manage update
                userslist = database.update_single_airport(airportid,newdict['name'],newdict['iatacode'],newdict['city'],newdict['country'])
            else:
                # no updates
                flash(f"No updated values for airport with {airportid}")
                return redirect(url_for('list_airports'))
            # Should redirect to your newly updated Airport
            return list_single_airport(airportid)
        else:
            # assuming GET request, need to setup for this
            return render_template('update_airport.html',
                            session=session,
                            page=page,
                            airport=airport)
    


@app.route('/airports/<airportid>')
def list_single_airport(airportid):
    '''
    List all rows in airports that match a particular id attribute airportid by calling the 
    relevant database calls and pushing to the appropriate template
    '''
    if( session['isadmin'] != True ):
        flash(f"Error, unable to view")
        return redirect(url_for('index'))
    airports_listdict = None
    airports_listdict = database.list_airports_equifilter("airportid", airportid)

    # Handle the null condition
    if (airports_listdict is None or len(airports_listdict) == 0):
        # Create an empty list and show error message
        flash('Error, there are no rows in users that match the attribute "airportid" for the value '+airportid)
    

    page_no = request.args.get('page_no',1, type = int)
    per_page = 10
    start = (page_no-1)*per_page
    end = start + per_page
    total = (len(airports_listdict) + per_page -1)//per_page
    items_on_page = airports_listdict[start:end]
    page['title'] = 'Updated Airport'
    return render_template('list_airports.html', page=page, session=session, airports=items_on_page, total=total, page_no=page_no)

def airportid_genrate():
    airport_dict = database.list_airports()
    while True:
        id = random.randint(1, len(airport_dict)+100)
        for airport in airport_dict:
            curr_id = airport['airportid']
            if curr_id == id:
                break
        else:
            print(id)
            return id

@app.route('/airports/summary')
def airport_summary():
    '''
    List all the countries together with the number of airports in them
    '''
    # connect to the database and call the relevant function
    if( session['isadmin'] != True ):
        flash(f"Error Unable to view")
        return redirect(url_for('index'))
    
    airports_listdict = database.airport_summary()
    page_no = request.args.get('page_no',1, type = int)
    per_page = 10
    start = (page_no-1)*per_page
    end = start + per_page
    total = (len(airports_listdict) + per_page -1)//per_page
    
    items_on_page = airports_listdict[start:end]
    

    # Handle the null condition
    if (airports_listdict is None):
        # Create an empty list and show error message
        airports_listdict = []
        flash('Error, there are no rows in airports')
    if (airports_listdict == []):
        flash('No Airports found')
        page_no = 0
    page['title'] = 'Airport summary based on Country'
    return render_template('airport_summary.html', page=page, session=session, airports=items_on_page,total=total,page_no=page_no)
            
@app.route('/airports/summarycity')
def airport_summary_city():
    '''
    List all the countries together with the number of airports in them
    '''
    if( session['isadmin'] != True ):
        flash(f"Error, Unable to view")
        return redirect(url_for('index'))
    
    # connect to the database and call the relevant function
    airports_listdict = database.airport_summary_city()
    page_no = request.args.get('page_no',1, type = int)
    print(page_no)
    per_page = 10
    start = (page_no-1)*per_page
    end = start + per_page
    total = (len(airports_listdict) + per_page -1)//per_page
    items_on_page = airports_listdict[start:end]

    # Handle the null condition
    if (airports_listdict is None):
        # Create an empty list and show error message
        airports_listdict = []
        flash('Error, there are no rows in airports')
    if (airports_listdict == []):
        flash('No Airports found')
        page_no = 0
    page['title'] = 'Airport summary based on City'
    return render_template('airport_summary_city.html', page=page, session=session, airports=items_on_page,total=total,page_no=page_no)
            

#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask import Flask
from models import app, db, Venue, Artist, Shows
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------
@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  def venues(city, state):
    venues = []
    for venue in Venue.query.filter(Venue.city==city, Venue.state==state).all():
      num_upcoming_shows = Shows.query.filter(Shows.venue_id==venue.id,Shows.start_time>datetime.today()).all()
      venues.append({'id': venue.id, 'name': venue.name,'num_upcoming_shows': len(num_upcoming_shows)} )
    return venues

  data = []

#append method for appending the dictionaries into list
  for area in Venue.query.with_entities(Venue.city,Venue.state).distinct().all():
    data.append({'city': area.city, 'state': area.state, 'venues': venues(area.city, area.state)} )


  
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  query = request.form.get('search_term')
  results = Venue.query.filter(Venue.name.ilike('%'+query+'%')).all()
  def search_query(query):
    data=[]
    for result in results:
      num_upcoming_shows = Shows.query.filter(Shows.venue_id==result.id,Shows.start_time>datetime.today()).all()
      data.append({'id': result.id, 'name': result.name, 'num_upcoming_shows': len(num_upcoming_shows)} )
    return data 
  response = {} 
  data = search_query(query)
  response["count"] = len(results) 
  response["data"] = data 
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  def past_shows(id):
    past_shows = []
    query = Shows.query\
              .join(Artist,Shows.artist_id == Artist.id) \
              .join(Venue,Shows.venue_id == Venue.id) \
              .with_entities(Shows.start_time,Shows.artist_id,Shows.venue_id,Artist.name.label('artist_name'),Venue.name.label('venue_name'),Artist.image_link.label('artist_image_link')).filter(Shows.venue_id==id,Shows.start_time<datetime.today()).all()
    for show in query:
      past_shows.append({'artist_id': show.artist_id, 'artist_name': show.artist_name, 'artist_image_link': show.artist_image_link, 'start_time': show.start_time.strftime("%d/%m/%Y, %H:%M")} )
    return past_shows
  def upcoming_shows(id):
    upcoming_shows = []
    query = Shows.query\
              .join(Artist,Shows.artist_id == Artist.id) \
              .join(Venue,Shows.venue_id == Venue.id) \
              .with_entities(Shows.start_time,Shows.artist_id,Shows.venue_id,Artist.name.label('artist_name'),Venue.name.label('venue_name'),Artist.image_link.label('artist_image_link')).filter(Shows.venue_id==id,Shows.start_time>datetime.today()).all()
    for show in query:
      upcoming_shows.append({'artist_id': show.artist_id, 'artist_name': show.artist_name, 'artist_image_link': show.artist_image_link, 'start_time': show.start_time.strftime("%d/%m/%Y, %H:%M")} )
    return upcoming_shows
  
  datax = []
  
  for venue in Venue.query.all():
    datax.append({'id': venue.id, 'name': venue.name, 'genres': venue.genres,'address': venue.address, 'city': venue.city, 'state': venue.state, 'phone': venue.phone, 'website': venue.website, 'facebook_link': venue.facebook_link, 'seeking_talent': venue.seeking_talent, 'seeking_description': venue.seeking_description, 'image_link': venue.image_link, 'past_shows': past_shows(venue.id), 'upcoming_shows': upcoming_shows(venue.id), 'past_shows_count': len(past_shows(venue.id)), 'upcoming_shows_count': len(upcoming_shows(venue.id))} )
  data = list(filter(lambda d: d['id'] == venue_id, datax))[0]
  return render_template('pages/show_venue.html', venue=data)
  
  

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    genres = request.form.getlist('genres')
    facebook_link = request.form.get('facebook_link')
    image_link=('https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png')
    venue = Venue(name=name, city=city, state=state, phone=phone, address=address, genres=genres, facebook_link=facebook_link,image_link=image_link)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + artist.name + ' could not be listed.') 
    abort(500)     
  else:
    return render_template('pages/home.html')
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  error = False
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue was successfully deleted!')
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue could not be deleted.')
    abort(500)      
  else:
    return redirect(url_for('index'))  
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  
  data = []

#append method for appending the dictionaries into list
  for artist in Artist.query.with_entities(Artist.id,Artist.name).all():
    data.append({'id': artist.id, 'name': artist.name} )

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  query = request.form.get('search_term')
  results = Artist.query.filter(Artist.name.ilike('%'+query+'%')).all()
  def search_query(query):
    data=[]
    for result in results:
      num_upcoming_shows = Shows.query.filter(Shows.artist_id==result.id,Shows.start_time>datetime.today()).all()
      data.append({'id': result.id, 'name': result.name, 'num_upcoming_shows': len(num_upcoming_shows)} )
    return data
  response = {} 
  data = search_query(query)
  response["count"] = len(results) 
  response["data"] = data 
  

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  def past_shows(id):
    past_shows = []
    query = Shows.query\
              .join(Artist,Shows.artist_id == Artist.id) \
              .join(Venue,Shows.venue_id == Venue.id) \
              .with_entities(Shows.start_time,Shows.artist_id,Shows.venue_id,Artist.name.label('artist_name'),Venue.name.label('venue_name'),Venue.image_link.label('venue_image_link')).filter(Shows.artist_id==id,Shows.start_time<datetime.today()).all()
    for show in query:
      past_shows.append({'venue_id': show.venue_id, 'venue_name': show.venue_name, 'venue_image_link': show.venue_image_link, 'start_time': show.start_time.strftime("%d/%m/%Y, %H:%M")} )
    return past_shows
  def upcoming_shows(id):
    upcoming_shows = []
    query = Shows.query\
              .join(Artist,Shows.artist_id == Artist.id) \
              .join(Venue,Shows.venue_id == Venue.id) \
              .with_entities(Shows.start_time,Shows.artist_id,Shows.venue_id,Artist.name.label('artist_name'),Venue.name.label('venue_name'),Venue.image_link.label('venue_image_link')).filter(Shows.artist_id==id,Shows.start_time>datetime.today()).all()
    for show in query:
      upcoming_shows.append({'venue_id': show.venue_id, 'venue_name': show.venue_name, 'venue_image_link': show.venue_image_link, 'start_time': show.start_time.strftime("%d/%m/%Y, %H:%M")} )
    return upcoming_shows
  
  datax = []
  
  for artist in Artist.query.all():
    datax.append({'id': artist.id, 'name': artist.name, 'genres': artist.genres,'city': artist.city, 'state': artist.state, 'phone': artist.phone, 'website': artist.website, 'facebook_link': artist.facebook_link, 'seeking_venue': artist.seeking_venue, 'seeking_description': artist.seeking_description, 'image_link': artist.image_link, 'past_shows': past_shows(artist.id), 'upcoming_shows': upcoming_shows(artist.id), 'past_shows_count': len(past_shows(artist.id)), 'upcoming_shows_count': len(upcoming_shows(artist.id))} )
    
  data = list(filter(lambda d: d['id'] == artist_id, datax))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  d_artist = Artist.query.filter_by(id=artist_id).all()
  artist={
    "id": d_artist[0].id,
    "name": d_artist[0].name,
    "genres": d_artist[0].genres,
    "city": d_artist[0].city,
    "state": d_artist[0].state,
    "phone": d_artist[0].phone,
    "website": d_artist[0].website,
    "facebook_link": d_artist[0].facebook_link,
    "seeking_venue": d_artist[0].seeking_venue,
    "seeking_description": d_artist[0].seeking_description,
    "image_link": d_artist[0].image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  try:
    artist = Artist.query.filter_by(id=artist_id).first()
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form.get('facebook_link')
    artist.image_link=('https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png')
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + artist.name + ' could not be updated.')
    abort(500)      
  else:
    return redirect(url_for('show_artist', artist_id=artist_id))  
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  d_venue = Venue.query.filter_by(id=venue_id).all()
  venue={
    "id": d_venue[0].id,
    "name": d_venue[0].name,
    "genres": d_venue[0].genres,
    "city": d_venue[0].city,
    "state": d_venue[0].state,
    "address": d_venue[0].address,
    "phone": d_venue[0].phone,
    "website": d_venue[0].website,
    "facebook_link": d_venue[0].facebook_link,
    "seeking_talent": d_venue[0].seeking_talent,
    "seeking_description": d_venue[0].seeking_description,
    "image_link": d_venue[0].image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  try:
    venue = Venue.query.filter_by(id=venue_id).first()
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.phone = request.form.get('phone')
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form.get('facebook_link')
    venue.image_link=('https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png')
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + venue.name + ' could not be updated.')
    abort(500)      
  else:
    return redirect(url_for('show_venue', venue_id=venue_id))
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    genres = request.form.getlist('genres')
    facebook_link = request.form.get('facebook_link')
    image_link=('https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png')
    artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link,image_link=image_link)
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
    abort(500)
  else:
    return render_template('pages/home.html')
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  query = Shows.query\
            .join(Artist,Shows.artist_id == Artist.id) \
            .join(Venue,Shows.venue_id == Venue.id) \
            .with_entities(Shows.start_time,Shows.artist_id,Shows.venue_id,Artist.name.label('artist_name'),Venue.name.label('venue_name'),Artist.image_link.label('artist_image_link')).all()

  #append method for appending the dictionaries into list
  for show in query:
    data.append({'venue_id': show.venue_id, 'venue_name': show.venue_name, 'artist_id': show.artist_id, 'artist_name': show.artist_name, 'artist_image_link': show.artist_image_link, 'start_time': show.start_time.strftime("%d/%m/%Y, %H:%M")} )
  return render_template('pages/shows.html', shows=data)

  

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try:
    artist_id = request.form.get('artist_id')
    venue_id = request.form.get('venue_id')
    start_time = request.form.get('start_time')
    show = Shows(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Show could not be listed.')
    abort(500)
  else:
    return render_template('pages/home.html')
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
  Flask,
  render_template,
  request,
  Response,
  flash,
  redirect,
  url_for,
  jsonify)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import os
import sys

from models import db, Venue, Show, Artist




#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
#db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app,db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Imported from models.py



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value,str):
    date = dateutil.parser.parse(value)
  else:
    date = value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  ----------------------------------------------------------------
#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    venues = Venue.query.distinct(Venue.city).all()
    data =[]
    
    for i in venues:
      ven_city = Venue.query.filter_by(city=i.city).all()
      data += [{
        "city":i.city,"state":i.state,"venues": ven_city
        }]
    
    return render_template('pages/venues.html', areas=data)

 

@app.route('/venues/search', methods=['POST'])
def search_venues():
  
  data =[]

  search_term = request.form.get('search_term', '')
  search =  "%{}%".format(search_term)
  venues = Venue.query.filter(Venue.name.ilike(search)).all()
  
  for i in venues:
    data.append({
      "id": i.id,
      "name": i.name,
    })
    
  response = { "count":len(venues),"data": data }
     
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))




@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):



  #past_show_query = Show.query.join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time < datetime.now()).distinct(Show.start_time).all()
  #upcoming_show_query = Show.query.join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time > datetime.now()).distinct(Show.start_time).all()
  venue = Venue.query.get_or_404(venue_id)
  past_shows = []
 # past_count = 0
  #upcoming_count = 0
  upcoming_shows = []

  for show in venue.shows:
    temp_show = {
        'artist_id': show.artist_id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
    if show.start_time <= datetime.now():
        past_shows.append(temp_show)
    else:
        upcoming_shows.append(temp_show)
  
  data = vars(venue)
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)



  #for i in past_show_query:
  #  past_shows.append ({
  #     "artist_id": i.artist_id,
  #     "artist_name": i.artist.name,
  #     "artist_image_link": i.artist.image_link,
  #     "start_time": i.start_time
  #  })
  #  past_count+=1
#
  #for j in upcoming_show_query:
  #  upcoming_shows.append ({
  #     "artist_id": j.artist_id,
  #     "artist_name": j.artist.name,
  #     "artist_image_link": j.artist.image_link,
  #     "start_time": j.start_time
  #  })
  #  upcoming_count+=1
#
#
  #data_query = Venue.query.filter_by(id=venue_id).first()
#
  #data = {
  #  "id": data_query.id,
  #  "name": data_query.name,
  #  "genres": data_query.genres,
  #  "city" : data_query.city,
  #  "state": data_query.state,
  #  "address": data_query.address,
  #  'image_link' : data_query.image_link,
  #  "phone": data_query.phone,
  #  "website": data_query.website,
  #  "facebook_link": data_query.facebook_link,
  #  "seeking_talent": data_query.seeking_talent,
  #  "seeking_description": data_query.seeking_description,
  #  "upcoming_shows": upcoming_shows, 
  #  "past_shows": past_shows, 
  #  "upcoming_shows_count": upcoming_count,
  #  "past_shows_count": past_count 
#
  #}
#
  print (data)
  
  return render_template('pages/show_venue.html', venue=data)

#  ----------------------------------------------------------------
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    form = VenueForm(request.form,csrf_enabled=False)
  
    if form.validate_on_submit():
      venue = Venue(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        image_link=form.image_link.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        website=form.website_link.data,
        seeking_talent=form.seeking_talent.data,
        seeking_description=form.seeking_description.data
        )
    else: 
      flash(form.errors)

    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')

  finally:
    db.session.close()
    return render_template('pages/home.html')



@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue_id + ' was successfully deleted!')

  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + venue_id + ' could not be deleted.')
  finally:
    db.session.close()
    return jsonify({'success': True })

  



#  ----------------------------------------------------------------
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  
  data= Artist.query.all()
  return render_template('pages/artists.html', artists=data)



@app.route('/artists/search', methods=['POST'])
def search_artists():
  
  data =[]

  search_term = request.form.get('search_term', '')
  search =  "%{}%".format(search_term)
  artisits = Artist.query.filter(Artist.name.ilike(search)).all()
  
  for i in artisits:
    data.append({
      "id": i.id,
      "name": i.name,
    })
    
  response = { "count":len(artisits),"data": data }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  past_show_query = Show.query.join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time < datetime.now()).distinct(Show.start_time).all()
  upcoming_show_query = Show.query.join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time > datetime.now()).distinct(Show.start_time).all()
  past_shows = []
  past_count = 0
  upcoming_count = 0
  upcoming_shows = []

  for i in past_show_query:
    past_shows.append ({
       "artist_id": i.artist_id,
       "venue_name": i.venue.name,
       "venue_image_link": i.venue.image_link,
       "start_time": i.start_time
    })
    past_count+=1

  for j in upcoming_show_query:
    upcoming_shows.append ({
       "artist_id": j.artist_id,
       "venue_name": j.venue.name,
       "venue_image_link": j.venue.image_link,
       "start_time": j.start_time
    })
    upcoming_count+=1


  data_query = Artist.query.filter_by(id=artist_id).first()


  data = {
    'id' : data_query.id,
    "name": data_query.name,
    'image_link' : data_query.image_link,
    "genres": data_query.genres,
    "city" : data_query.city,
    "state": data_query.state,
    "phone": data_query.phone,
    "website": data_query.website,
    "facebook_link": data_query.facebook_link,
    "seeking_venue": data_query.seeking_venue,
    "seeking_description": data_query.seeking_description,
    "upcoming_shows": upcoming_shows, 
    "past_shows": past_shows, 
    "upcoming_shows_count": upcoming_count,
    "past_shows_count": past_count 

  }
  
  return render_template('pages/show_artist.html', artist=data)

#  ----------------------------------------------------------------
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  
  data_query = Artist.query.filter_by(id=artist_id).first()
  form = ArtistForm(request.form,csrf_enabled=False)

  
  form.name.data = data_query.name
  form.image_link.data = data_query.image_link
  form.genres.data = data_query.genres
  form.city.data = data_query.city
  form.state.data = data_query.state
  form.phone.data = data_query.phone
  form.website_link.data = data_query.website
  form.facebook_link.data = data_query.facebook_link
  form.seeking_venue.data = data_query.seeking_venue
  form.seeking_description.data = data_query.seeking_description
 

  artist={
    "id": artist_id,
    "name": form.name.data,
    "genres": form.genres.data,
    "city": form.city.data,
    "state": form.state.data,
    "phone": form.phone.data,
    "website": form.website_link.data,
    "facebook_link": form.facebook_link.data,
    "seeking_venue": form.seeking_venue.data,
    "seeking_description": form.seeking_description.data,
    "image_link": form.image_link.data
  }

  
  return render_template('forms/edit_artist.html', form=form, artist=artist)



@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  try:
    form = ArtistForm(request.form,csrf_enabled=False)
    artist =Artist.query.get(artist_id)
  
    if form.validate_on_submit():
      
      artist.name=form.name.data
      artist.city=form.city.data
      artist.state=form.state.data
      artist.phone=form.phone.data
      artist.image_link=form.image_link.data
      artist.genres=form.genres.data
      artist.facebook_link=form.facebook_link.data
      artist.website=form.website_link.data
      artist.seeking_venue=form.seeking_venue.data
      artist.seeking_description=form.seeking_description.data

    
    else: 
      flash(form.errors)

    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
    print(sys.exc_info())

  finally:
    db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))



@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  form = VenueForm(request.form,csrf_enabled=False)

  data_query = Venue.query.get(venue_id)

  form.name.data = data_query.name
  form.image_link.data = data_query.image_link
  form.genres.data = data_query.genres
  form.city.data = data_query.city
  form.address.data = data_query.address
  form.state.data = data_query.state
  form.phone.data = data_query.phone
  form.website_link.data = data_query.website
  form.facebook_link.data = data_query.facebook_link
  form.seeking_talent.data = data_query.seeking_talent
  form.seeking_description.data = data_query.seeking_description
 

  venue = {
    "id": venue_id,
    "name": form.name.data,
    "genres": form.genres.data,
    "city": form.city.data,
    "state": form.state.data,
    "address": form.address.data,
    "phone": form.phone.data,
    "website": form.website_link.data,
    "facebook_link": form.facebook_link.data,
    "seeking_talent": form.seeking_talent.data,
    "seeking_description": form.seeking_description.data,
    "image_link": form.image_link.data
  }

  
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  try:
    form = VenueForm(request.form,csrf_enabled=False)
    venue =Venue.query.get(venue_id)
  
    if form.validate_on_submit():
      
      venue.name=form.name.data
      venue.city=form.city.data
      venue.state=form.state.data
      venue.phone=form.phone.data
      venue.image_link=form.image_link.data
      venue.genres=form.genres.data
      venue.facebook_link=form.facebook_link.data
      venue.website=form.website_link.data
      venue.seeking_talent=form.seeking_talent.data
      venue.seeking_description=form.seeking_description.data
      venue.address=form.address.data

    
    else: 
      flash(form.errors)

    db.session.add(venue)
    db.session.commit()
    flash('venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. venue ' + form.name.data + ' could not be listed.')
    print(sys.exc_info())

  finally:
    db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))


#  ----------------------------------------------------------------
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    form = ArtistForm(request.form,csrf_enabled=False)
  
    if form.validate_on_submit():
      artist = Artist(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        image_link=form.image_link.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        website=form.website_link.data,
        seeking_venue=form.seeking_venue.data,
        seeking_description=form.seeking_description.data
        )
    else: 
      flash(form.errors)

    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
    print(sys.exc_info())


  finally:
    db.session.close()
    return render_template('pages/home.html')



#  ----------------------------------------------------------------
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  #data_query = Show.query.distinct(Show.venue_id).distinct(Show.artist_id).distinct(Show.start_time).all()
  data_query = Show.query.join(Artist).join(Venue).distinct(Show.start_time).all()
  data = []

  for i in data_query:
    data.append({
      "venue_id": i.venue_id ,
      "venue_name": i.venue.name,
      "artist_id": i.artist_id,
      "artist_name": i.artist.name,
      "artist_image_link": i.artist.image_link,
      "start_time": i.start_time
      })
    

  print (data_query)
  return render_template('pages/shows.html', shows=data)



@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    form = ShowForm(request.form,csrf_enabled=False)
  
    if form.validate_on_submit():
      show = Show(
        artist_id=form.artist_id.data,
        venue_id=form.venue_id.data,
        start_time=form.start_time.data
        )
    else: 
      flash(form.errors)

    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. show could not be listed.')
    error = sys.exc_info()
    error = str(error[1])
    error_detail =error[error.find('DETAIL:'):error.find('[')]
    print (error)
    
    flash(error_detail)

  finally:
    db.session.close()
    return render_template('pages/home.html')



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
    app.run(host='0.0.0.0', port=5000)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

from flask import render_template,flash, redirect,url_for,request,g,jsonify,current_app
from werkzeug.urls import url_parse
from app import db
from app.main.forms import LoginForm,RegistrationForm,EditProfileForm,PostForm,ResetPasswordRequestForm,ResetPasswordForm
from flask_login import current_user, login_required
from app.models import User,Post
from datetime import datetime
from flask_babel import _,get_locale
from guess_language import guess_language
from app.translate import translate
from app.main import bp
from app.main.forms import SearchForm


@bp.route('/',methods=['GET','POST'])
@bp.route('/index',methods=['GET','POST'])
@login_required
def index():
	#return render_template('index.html',title='Home',user=user)
	form=PostForm()
	if form.validate_on_submit():
		language=guess_language(form.post.data)
		if language == 'UNKNOWN' or len(langauge) >5:
			language=''
		post=Post(body=form.post.data,author=current_user,language=language)	
		db.session.add(post)
		db.session.commit()
		flash('Your post is live now!!')
		return redirect(url_for('main.index'))
	posts=current_user.followed_posts().all()
	'''posts=[
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]'''
	page=request.args.get('page',1,type=int)
	posts=current_user.followed_posts().paginate(page,current_app.config['POSTS_PER_PAGE'], False)
	next_url=url_for('main.index',page=posts.next_num) if posts.has_next else None
	prev_url=url_for('main.index',page=posts.prev_num) if posts.has_prev else None
	return render_template('index.html',title='Home Page',form=form,posts=posts.items,next_url=next_url,prev_url=prev_url)
@bp.route('/user/<username>')
@login_required
def user(username):
	user=User.query.filter_by(username=username).first_or_404()
	'''posts=[
	{'author':user,'body':'Test post #1'},
	{'author':user,'body':'Test post #2'}
	]'''
	page=request.args.get('page',1,type=int)
	posts=user.posts.order_by(Post.timestamp.desc()).paginate(page,current_app.config['POSTS_PER_PAGE'],False)
	next_url=url_for('main.user',username=user.username,page=posts.next_num) if posts.has_next else None
	prev_url=url_for('main.user',username=user.username,page=posts.prev_num) if posts.has_prev else None
	return render_template('user.html',user=user,posts=posts.items,next_url=next_url,prev_url=prev_url)
@bp.before_app_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen=datetime.utcnow()
		db.session.commit()
		g.search_form=SearchForm()
	g.locale=str(get_locale())
@bp.route('/edit_profile',methods=['GET','POST'])
@login_required
def edit_profile():
	form=EditProfileForm(current_user.username)
	if form.validate_on_submit():
		current_user.username=form.username.data
		current_user.about_me=form.about_me.data
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('main.edit_profile'))
	elif request.method=='GET':
		form.username.data=current_user.username
		form.about_me.data=current_user.about_me
	return render_template('edit_profile.html',title='Edit Profile',form=form)
@bp.route('/follow/<username>')
@login_required
def follow(username):
	user=User.query.filter_by(username=username).first()
	if user is None:
		flash("User {} not found.".format(username))
		return redirect(url_for('main.index'))
	if user == current_user:
		flash("You cannot follow yourself")
		return redirect(url_for('main.user',username=username))
	current_user.follow(user)
	db.session.commit()
	flash('You are following {}!'.format(username))
	return redirect(url_for('main.user',username=username))

@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
	user=User.query.filter_by(username=username).first()
	if user is None:
		flash("User {} not found.".format(username))
		return redirect(url_for('main.index'))
	if user == current_user:
		flash('You cannot unfollow yourself!')
		return redirect(url_for('main.user',username=username))
	current_user.unfollow(user)
	db.session.commit()
	flash('You are not following {}.'.format(username))
	return redirect(url_for('main.user',username=username))

@bp.route('/explore')
@login_required
def explore():
	posts=Post.query.order_by(Post.timestamp.desc()).all()
	page=request.args.get('page',1,type=int)
	posts=Post.query.order_by(Post.timestamp.desc()).paginate(page,current_app.config['POSTS_PER_PAGE'],False)
	next_url=url_for('main.explore',page=posts.next_num) if posts.has_next else None
	prev_url=url_for('main.explore',page=posts.prev_num) if posts.has_prev else None
	return render_template('index.html',title='Explore',posts=posts.items,next_url=next_url, prev_url=prev_url)
@bp.before_request
def before_request():
	g.locale=str(get_locale())
@bp.route('/translate',methods=['GET','POST'])
@login_required
def translate_text():
	return jsonify({'text' : translate(request.form['text'],request.form['source_language'],request.form['dest_language'])})
@bp.route('/search')
@login_required
def search():
	if not g.search_form.validate():
		return redirect(url_for('main.explore'))
	page=request.args.get('page',1,type=int)
	posts,total=Post.search(g.search_form.q.data,page,current_app.config['POSTS_PER_PAGE'])
	next_url=url_for('main.search',q=g.search_form.q.data,page=page+1) if total > page * current_app.config['POSTS_PER_PAGE'] else None
	prev_url=url_for('main.search',q=g.search_form.q.data,page=page-1) if page  > 1 else None
	return render_template('search.html',title=_('Search'),posts=posts,next_url=next_url,prev_url=prev_url)
'''def login():
	form=LoginForm()
	if form.validate_on_submit():
		flash('Login requested for user {},remember_me={}'.format(form.username.data,form.remember_me.data))
		return redirect(url_for('index'))
	return render_template('login.html',title='Sign In',form=form)'''

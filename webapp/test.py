import csv
import json

from flask import Flask, render_template, Response, stream_template
import calcolo_sensori_stazioni
import AQI_versione_definitiva
import grafico_media_mobile_tasti
import folium
import plotly
import os

from flask import Flask, render_template, request, redirect, url_for, flash, abort, make_response
from flask_bootstrap import Bootstrap
from flask_caching import Cache

from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, TextAreaField, SelectField, ValidationError
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp
from threading import Thread
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user, AnonymousUserMixin
import jwt
import datetime
from flask_mail import Message, Mail
from functools import wraps
import hashlib
from faker import Faker
from random import randint
from sqlalchemy.exc import IntegrityError
from flask_pagedown import PageDown
from flask_pagedown.fields import PageDownField
from markdown import markdown
import bleach
from flask_migrate import Migrate
# >>>>>>FLASK<<<<<<<<<<<<<<<<<<<<<<<<


app = Flask(__name__, template_folder='templates')
"app.config['SECRET_KEY'] = os.environ['SECRET_KEY']"
app.config['SECRET_KEY'] = "somehtingcool"
app.config['SQLALCHEMY_DATABASE_URI'] = \
    "mysql+mysqlconnector://root@localhost/projectwork5"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

# Mail parameters

"""app.config['MAIL_SERVER']='sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']"""
app.config['MAIL_SERVER'] = 'sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = 'efc022e88519de'
app.config['MAIL_PASSWORD'] = '137e5d4efb99a4'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['dapollution-mail'] = 'dapollution@dapollution.it'

app.config['DAPOLLUTION_MAIL_SUBJECT_PREFIX'] = '[DAPOLLUTION]'
app.config['DAPOLLUTION_MAIL_SENDER'] = 'Da pollution <dapollution@example.com>'
app.config['POST'] = 10
app.config['FOLLOWERS'] = 10
app.config['COMMENTS'] = 10
app.config['CACHE_TYPE'] = 'simple'
mail = Mail()
mail.init_app(app)

pagedown = PageDown(app)
cache = Cache(app)
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['DAPOLLUTION_MAIL_SUBJECT_PREFIX'] + subject, sender=app.config['DAPOLLUTION_MAIL_SENDER'],
                  recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    print("MAIL POSSIBILMENTE INVIATA")
    return thr


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(mail):
    return User.query.get((mail))


""">>>>>>>>>>>>>>>>>>>>>>>> USERS - ROLES <<<<<<<<<<<<<<<<<<<<"""
class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16

class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), unique=True, index=True)
    mail = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(200))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(100))
    bio = db.Column(db.Text())
    location = db.Column(db.String(64))
    member_since = db.Column(db.DateTime(), default=datetime.datetime.now)
    last_seen = db.Column(db.DateTime(), default=datetime.datetime.now)
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.mail == app.config['dapollution-mail']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.mail is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()

    @property
    def password(self):
        raise AttributeError("password is not readable")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return self.mail

    def generate_confirmation_token(self, expiration=18_000):
        reset_token = jwt.encode(
            {
                "confirm": self.id,
                "exp": datetime.datetime.now(tz=datetime.timezone.utc)
                       + datetime.timedelta(seconds=expiration),
            },
            app.config["SECRET_KEY"],
            algorithm="HS256",
        )
        return reset_token

    def confirm(self, token):
        try:
            data = jwt.decode(
                token,
                app.config["SECRET_KEY"],
                leeway=datetime.timedelta(seconds=10),
                algorithms=["HS256"],
            )
        except:
            return False
        if data.get("confirm") != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def ping(self):
        self.last_seen = datetime.datetime.now()
        db.session.add(self)
        db.session.commit()

    def change_email(self, token):
        try:
            data = jwt.decode(
                token,
                app.config["SECRET_KEY"],
                leeway=datetime.timedelta(seconds=10),
                algorithms=["HS256"],
            )
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_mail = data.get('new_email')
        if new_mail is None:
            return False
        if self.query.filter_by(mail=new_mail).first() is not None:
            return False
        self.mail = new_mail
        self.avatar_hash = self.gravatar_hash()
        db.session.add(self)
        db.session.commit(self)
        return True

    def gravatar_hash(self):
        return hashlib.md5(self.mail.lower().encode('utf-8')).hexdigest()

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hashed = self.avatar_hash or self.gravatar_hash()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hashed, size=size, default=default, rating=rating)

    #Follower methods
    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
    def is_following(self, user):
        if user.id is None:
            return False
        return self.followed.filter_by(
            followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        if user.id is None:
            return False

        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id).filter(Follow.follower_id == self.id)




class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT,
                          Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT,
                              Permission.WRITE, Permission.MODERATE,
                              Permission.ADMIN],
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()





class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))


db.event.listen(Post.body, 'set', Post.on_changed_body)







def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def admin_required(f):
    return permission_required(Permission.ADMIN)(f)


class LoginForm(FlaskForm):
    mail = StringField('Mail', validators=[Email(), DataRequired(), Length(1, 64)])
    password = StringField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log In')


class RegisterForm(FlaskForm):
    nickname = StringField('Nickname', validators=[DataRequired(), Length(1, 64),
                                                   Regexp('^[A-Za-z][A-Za-z0-9_.%$/-]*$', 0,
                                                          'Nicknames must have only letters and _.%$/-')])
    mail = StringField('Mail', validators=[Email(), DataRequired()])
    password1 = StringField('Password',
                            validators=[DataRequired(), EqualTo('password2', message="Passwords don't match.")])
    password2 = StringField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Register')


class EditProfileForm(FlaskForm):
    nickname = StringField('Nickname', validators=[Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.%$/-]*$', 0,'Nicknames must have only letters and _.%$/-')])
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    bio = TextAreaField('My bio')
    submit = SubmitField('Submit')


class EditProfileAdminForm(FlaskForm):
    mail = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    nickname = StringField('Nickname', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Nicknames must have only letters, numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    bio = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):

        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_nickname(self, field):
        if field.data != self.user.nickname and User.query.filter_by(nickname=field.data).first():
            raise ValidationError('Nickname already in use.')

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.now)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i', 'strong']
        target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'), tags=allowed_tags, strip=True))

db.event.listen(Comment.body, 'set', Comment.on_changed_body)

class CommentForm(FlaskForm):
    body = StringField('', validators=[DataRequired()])
    submit = SubmitField('Submit')


login_manager.anonymous_user = AnonymousUser

"""appHasRunBefore: bool = False"""
def users(count=100):
    fake = Faker('it_IT')
    i = 0
    while i < count:
        u = User(mail=fake.email(),
            nickname=fake.user_name(),
            password='password',
            confirmed=True,
            name=fake.name(),
            location=fake.city(),
            bio=fake.text(),
            member_since=fake.past_date())
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()

def posts(count=100):
    fake = Faker()
    user_count = User.query.count()
    for i in range(count):
        u = User.query.offset(randint(0, user_count - 1)).first()
        p = Post(body=fake.text(),
              timestamp=fake.past_date(),
              author=u)
        db.session.add(p)
    db.session.commit()

class PostForm(FlaskForm):
    body = PageDownField("What's on your mind?", validators=[DataRequired()])
    submit = SubmitField('Submit')


migrate = Migrate(app, db)

"""@app.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)"""


@app.before_request
def before_request():
    """db.drop_all()"""
    #db.create_all()
    #users()
    #posts()
    if (not current_user.is_anonymous) and current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed:
            flash("Please, confirm your mail.")

# def user_data():


@app.route('/', methods=['GET', 'POST'])
@cache.cached(timeout=120)
def index():
    #flash("Your name has changed")
    #Role.insert_roles()
    form = PostForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=app.config['POST'], error_out=False)
    posts = pagination.items
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>CALCOLO I
    mappa = AQI_versione_definitiva.crea_mappa()
    iframe = mappa.get_root()._repr_html_()

    return render_template('index.html', form=form, posts=posts, show_followed=show_followed, pagination=pagination, Permission=Permission, iframe=iframe)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():  # checks if the fields in the form are ok
        # Login check
        user_database = User.query.filter_by(mail=form.mail.data).first()
        if user_database and user_database.mail == form.mail.data and user_database.verify_password(form.password.data):
            print('yes')
            login_user(user_database, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):  # validation against malicious users
                print("next is here")
                next = url_for('index')
            form.mail.data = ''
            form.password.data = ''
            return redirect(next)

        flash("The login is not correct")

    return render_template('auth/login.html', form=form, Permission=Permission)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():  # checks if the fields in the form are ok

        # Add object to database
        new_user = User(nickname=form.nickname.data,
                        mail=form.mail.data,
                        password=form.password1.data, )

        user_in_database = User.query.filter_by(mail=new_user.mail).first()
        if str(new_user) != str(user_in_database):
            print('yes')
            db.session.add(new_user)
            db.session.commit()
            form.mail.data = ''
            form.password1.data = ''
            form.password2.data = ''
            flash("""Thank you for Signing Up!
            You will soon receive a confirmation email.""")
            token = new_user.generate_confirmation_token()
            send_email(new_user.mail, 'Confirm Account', 'email/confirm', user=new_user, token=token)

            return redirect(url_for('index'))
        else:
            flash("This e-mail already exists.")

    return render_template('auth/login.html', form=form, Permission=Permission)


@app.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account')
    else:
        flash('The link is invalid or expired.')
    return redirect(url_for('login'))


@app.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html', Permission=Permission)


@app.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.mail, 'Confirm Your Account', 'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))


@app.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "For administrators!"


@app.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
    page=page, per_page=app.config['COMMENTS'],
    error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments, pagination=pagination, page=page, Permission=Permission)



@app.route('/user/<nickname>')
def user(nickname):
    user = User.query.filter_by(nickname=nickname).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=app.config['POST'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination, Permission=Permission)


@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.nickname = form.nickname.data
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.bio = form.bio.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', nickname=current_user.nickname))
    form.nickname.data = current_user.nickname
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.bio.data = current_user.bio
    return render_template('/auth/edit_profile.html', form=form, Permission=Permission)

@app.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.mail = form.mail.data
        user.nickname = form.nickname.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.bio = form.bio.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user', nickname=user.nickname))
    form.mail.data = user.mail
    form.nickname.data = user.nickname
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.bio.data = user.bio
    return render_template('/auth/edit_profile.html', form=form, user=user, Permission=Permission)

@app.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
        post=post,
        author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published.')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // app.config['COMMENTS'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page = page, per_page=app.config['COMMENTS'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form, comments=comments, pagination=pagination, Permission=Permission)

@app.route('/unfollow/<nickname>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('.user', nickname=nickname))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following %s anymore.' % nickname)
    return redirect(url_for('.user', nickname=nickname))

@app.route('/follow/<nickname>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('.user', nickname=nickname))
    current_user.follow(user)
    db.session.commit()
    flash('You are now following %s.' % nickname)
    return redirect(url_for('.user', nickname=nickname))

@app.route('/followers/<nickname>')
def followers(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(page=page, per_page=app.config['FOLLOWERS'], error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of", endpoint='.followers', pagination=pagination, follows=follows, Permission=Permission)

@app.route('/followed_by/<nickname>')
def followed_by(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page=page, per_page=app.config['FOLLOWERS'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows, Permission=Permission)

@app.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60) # 30 days
    return resp

@app.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60) # 30 days
    return resp

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMIN):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form, Permission=Permission)

@app.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))

@app.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))

@app.route("/prova_searchbar")
def prova_searchbar():
    lista_comuni = []
    with open("comuni_search_bar.csv", "r", encoding="utf-8") as file:
        lettore = csv.reader(file)
        for elem in lettore:
            lista_comuni.append(elem[0])
    return render_template("search_bar.html", comuni=json.dumps(lista_comuni))

@app.route("/grafico")
def grafico():
    fig = grafico_media_mobile_tasti.crea_grafico()
    json_fig = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template("grafico.html",Permission=Permission, grafico=json_fig)

if __name__ == '__main__':
    app.run(debug=True)
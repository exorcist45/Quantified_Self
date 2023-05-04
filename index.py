
import os
from datetime import timedelta, datetime
from flask import Flask, redirect, render_template, request, session,redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_table import Table, Col, LinkCol
from sqlalchemy import and_, desc

current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = "hellothere"
app.permanent_session_lifetime = timedelta(minutes = 15)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir, "maindb.db")
db = SQLAlchemy(app)


#Database Tables Declarations
class User(db.Model):
    __tablename__ = 'user'
    userid = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, unique = True)
    firstname = db.Column(db.String)
    lastname = db.Column(db.String)
    password = db.Column(db.String)
    #trackerids = db.relationship('Tracker', cascade = 'all, delete', backref = 'user', lazy = True)
   
class Tracker(db.Model):
    __tablename__ = "tracker"
    trackerid = db.Column(db.Integer, primary_key = True)
    userid = db.Column(db.Integer)
    trackername = db.Column(db.String)
    trackertype =db.Column(db.String)
    description = db.Column(db.String)
    setting = db.Column(db.String)

class Log(db.Model):
    __tablename__ = "log"
    logid = db.Column(db.Integer, primary_key = True)
    userid = db.Column(db.Integer)
    trackerid = db.Column(db.Integer)
    value = db.Column(db.String)
    note = db.Column(db.String)
    time = db.Column(db.String)
#Database Table End 
    
#Table For display - Declarations    
class ItemTable(Table):
    classes = ['table','table-striped', 'text-center']
    
    
    trackername = LinkCol(name='Tracker', attr='trackername' , endpoint='stat', url_kwargs=dict(stat='trackerid'), anchor_attrs={'type': 'button', 'class': 'btn btn-primary'}, column_html_attrs={'width': '265px'})
    description = Col('Description', attr='description')
    update = LinkCol(name= "Update",endpoint="update", url_kwargs=dict(update="trackerid"), anchor_attrs={'type': 'button', 'class': 'btn btn-primary'}, column_html_attrs={'width': '50px'})
    add = LinkCol(name= "Add", endpoint="add", url_kwargs=dict(add="trackerid"), anchor_attrs={'type': 'button', 'class': 'btn btn-primary'}, column_html_attrs={'width': '50px'})
    delete = LinkCol(name= "Delete", endpoint="delete", url_kwargs=dict(delt="trackerid"), anchor_attrs={'type': 'button', 'class': 'btn btn-primary'},column_html_attrs={'width': '50px'})
    

class ValueTable(Table):
    classes = ['table', 'table-striped', 'text-center' ]
    
    
    value = Col('Value', attr='value',column_html_attrs={'width': '260px'})
    note = Col('Note', attr='note')
    time = Col('Time Logged', attr='time', column_html_attrs={'width': '200px'})
    update = LinkCol(name= "Update", endpoint="update_log", url_kwargs=dict(trackid="trackerid",update="logid"), anchor_attrs={'type': 'button', 'class': 'btn btn-primary'}, column_html_attrs={'width': '50px'})
    add = LinkCol(name= "Add", endpoint="add", url_kwargs=dict(add="trackerid"), anchor_attrs={'type': 'button', 'class': 'btn btn-primary'}, column_html_attrs={'width': '50px'})
    delete = LinkCol(name= "Delete", endpoint="delete_log", url_kwargs=dict(delt="logid"), anchor_attrs={'type': 'button', 'class': 'btn btn-primary'},column_html_attrs={'width': '50px'})
#Table Model End   


#App routes:
#Home
@app.route("/")
def front():
    if "userid" in session:
        items=Tracker.query.filter(Tracker.userid==session["userid"]).all()
        i=Tracker.query.filter(Tracker.userid==session['userid']).first()
        if i is None:
            return redirect(url_for("addtracker"))
        table=ItemTable(items)
        if 'message' in session:
            m=session['message']
            session.pop('message', None)
            return render_template("index.html",tab=table,mes=m)
        
        return render_template("index.html", tab=table)
    return render_template("login.html")

#Login
@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == 'POST':
        session.permanent = True
        username = request.form.get("username")
        password = request.form.get("password")
        
        condition =  User.query.filter_by(username = username).first()
        if condition is None:
            return render_template("login.html", error = "notfound")
        else:
            check = User.query.filter(and_(User.username==username, User.password == password)).first()
            if check is not None:
                session['username'] = username
                userid = check.userid
                session['userid'] = userid
                return redirect("/")
            return render_template("login.html", error = "notfound")
    if "username" in session:
        return redirect("/")
    return render_template("login.html")


@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        first = request.form.get("firstname")
        last = request.form.get("lastname")
        username = request.form.get("username")
        password = request.form.get("password")

        condition = User.query.filter_by(username=username).first()
        if condition is None:
            me = User(__tablename__="user",username=username, firstname=first, lastname=last, password=password)
            db.session.add(me)
            db.session.commit()
        else: 
            return render_template("login.html", error = "alreadyexist")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("userid", None)
    session.pop("message",None)
    return redirect("/")
#Login End


#For Adding Tracker
@app.route("/addtracker", methods = ["GET", "POST"])
def addtracker():
    if "userid" in session:
        if request.method == "POST":
            trackername = request.form.get("trackername")
            description = request.form.get("description")
            trackertype = request.form.get("trackert")
            setting = request.form.get("setting")
        
            
            condition = Tracker.query.filter_by(trackername=trackername).first()
            if condition is None:
                content = Tracker(__tablename__="tracker", userid=session["userid"], trackername=trackername, trackertype=trackertype, description=description, setting=setting)
                db.session.add(content)
                db.session.commit()
                return redirect("/")
            else:
                session["message"]="Tracker Name already Exist"
                return redirect("/")
            
        items=Tracker.query.filter(Tracker.userid==session["userid"]).all()
        table=ItemTable(items)
        
        q=Tracker.query.order_by(desc(Tracker.trackerid)).first()       
              
        return render_template("addtracker.html",lastid=(q.trackerid)+1,tab=table)
    return redirect(url_for("login"))

#For Updating Tracker
@app.route("/update/<int:update>", methods=["GET", "POST"])
def update(update):
    if 'userid' in session:
        if request.method == "POST":
            trackername = request.form.get("trackername")
            query=Tracker.query.filter(and_(Tracker.trackername == trackername, Tracker.trackerid !=update)).first()
            if query is not None:
                session["message"]="Tracker already exist with the same name"
                return redirect("/")
            description = request.form.get("description")
            Tracker.query.filter(Tracker.trackerid == update).update({Tracker.trackername : trackername, Tracker.description : description})
            db.session.commit()
            return redirect("/")
        
        q = Tracker.query.filter(Tracker.trackerid == update).first()
        
        items=Tracker.query.filter(and_(Tracker.userid==session["userid"], Tracker.trackerid != update)).all()
        
        table=ItemTable(items)
        return render_template("update_tracker.html", tab= table,tid=update, tname=q.trackername, tdesc =q.description)
    return redirect(url_for("login"))
        
#For deleting tracker
@app.route("/delete/<int:delt>")
def delete(delt):
    if 'userid' in session:
        track_del = Tracker.query.filter(and_(Tracker.trackerid == delt, Tracker.userid== session['userid'])).first()
        if track_del is not None:
            Tracker.query.filter(and_(Tracker.trackerid == delt, Tracker.userid== session['userid'])).delete()
        else:
            session['message'] = "Tracker Not Found"
            return redirect("/")
        log_del = Log.query.filter(and_(Log.trackerid == delt, Log.userid == session['userid'])).first()
        if log_del is not None:
            Log.query.filter(and_(Log.trackerid == delt, Log.userid == session['userid'])).delete()
            
        db.session.commit()
        session['message'] = "Tracker Found and Deleted Successfully"
        return redirect("/")
    return redirect(url_for("login"))


#For Displaying Log and Stats
@app.route("/<int:stat>")
def stat(stat):
    if 'userid' in session:
        q = Log.query.filter(and_(Log.userid==session['userid'], Log.trackerid==stat))
        som=Tracker.query.filter(Tracker.trackerid==stat).first()
        query= q.with_entities(Log.time, Log.value)
        if som.trackertype=="num":
            labels=[r[0] for r in query]
            values=[r[1] for r in query]
        else:
            o=som.setting.split(",")
            amount=len(o)
            d=dict()
            
            for r in query:
                d[r[1]]=d.get(r[1],0)+1
            labels=[r[1] for r in query]
            values=[d[key] for key in d]
        if q.first() is None:
            return redirect(url_for("add",add=stat))
            
            
        table=ValueTable(q.all())
        if 'message' in session:
            m=session['message']
            session.pop('message', None)
            return render_template("stats.html",tab=table, name=som.trackername, mes=m, labels=labels,values=values, ttype=som.trackertype)
        
        return render_template("stats.html", tab=table, name=som.trackername,labels=labels,values=values, ttype=som.trackertype)
    return redirect(url_for('login'))

#For Adding new Log
@app.route("/addtracker/<int:add>", methods=["GET", "POST"])
def add(add):
    if 'userid' in session:
        if request.method == "POST":
            value=request.form.get("tvalue")
            note=request.form.get("note")
            time=datetime.now()
            content=Log(__tablename__="log", userid=session["userid"], trackerid=add, value=value, note=note, time=time)
            db.session.add(content)
            db.session.commit()
            session['message']="Added New Log Successfully"
            return redirect(url_for("stat",stat=add))
        
        query=Log.query.filter(and_(Log.trackerid==add, Log.userid==session['userid']))
        t=Tracker.query.filter(Tracker.trackerid==add).first()
        if t.trackertype=="multiple":
            opt=t.setting.split(',')
        else:
            opt=None
        
        if query.first() is None:
            return render_template("trackvalue.html", tname= t.trackername, tid=add, ttype=t.trackertype,option=opt)
        
        table=ValueTable(query.all())
        return render_template("trackvalue.html", tname= t.trackername, tid=add, tab=table, ttype=t.trackertype, option=opt)
    return redirect(url_for("login"))

#For Updating Log
@app.route("/update_log/<int:trackid>/<int:update>", methods=["GET", "POST"])
def update_log(trackid, update):
    if 'userid' in session:
        if request.method == "POST":
            value = request.form.get("value")
            note = request.form.get("note")
            Log.query.filter(Log.logid == update).update({Log.value : value, Log.note : note})
            db.session.commit()
            return redirect(url_for("stat", stat=trackid))
        
        q = Tracker.query.filter(and_(Tracker.trackerid == trackid, Tracker.userid == session['userid'])).first()
        l = Log.query.filter(Log.logid == update).first()
        if q.trackertype=="multiple":
            opt=q.setting.split(",")
        else:
            opt=None
        items=Log.query.filter(and_(Log.userid==session["userid"], Log.trackerid == trackid, Log.logid != update))
        if items.first() is None:
            return render_template("update_log.html", tid=trackid, tname=q.trackername, tvalue=l.value, tnote=l.note, up=update, ttype=q.trackertype,option=opt)
        table=ValueTable(items.all())
        return render_template("update_log.html", tab= table,tid=trackid, tname=q.trackername, tvalue=l.value, tnote=l.note, up=update, ttype=q.trackertype,option=opt)
    return redirect(url_for("login"))

#For Deleting Log
@app.route("/delete_log/<int:delt>")
def delete_log(delt):
    if 'userid' in session:
        log_del = Log.query.filter(Log.logid == delt).first()
        if log_del is not None:
            Log.query.filter(Log.logid == delt).delete()
        else:
            session['message'] = "Log Not Found"
            return redirect("/")
        log_del = Log.query.filter(and_(Log.trackerid == delt, Log.userid == session['userid'])).first()
        if log_del is not None:
            Log.query.filter(and_(Log.trackerid == delt, Log.userid == session['userid'])).delete()
            
        db.session.commit()
        session['message'] = "Log Found and Deleted Successfully"
        return redirect(url_for("stat"), stat=log_del.trackerid)
    return redirect(url_for("login"))



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
    


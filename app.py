
from io import BytesIO
import requests as r, random, json

from flask import Flask,render_template,redirect, send_file
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inbox_msg.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class inbox_msg(db.Model):
    no= db.Column(db.Integer,primary_key=True)
    sender= db.Column(db.String(200),nullable=False)
    senderName= db.Column(db.String(200),nullable=False)
    subject= db.Column(db.String(200),nullable=False)
    date= db.Column(db.String(200),nullable=False)
    content=db.Column(db.String(200),nullable=True)
    fileName=db.Column(db.String(200),nullable=True)
    file=db.Column(db.LargeBinary)
   

domains_list = ["vintomaper.com","mentonit.net"]
API = "https://cryptogmail.com/api/emails"

def get_random(digit):
	lis = list("abcdefghijklmnopqrstuvwxyz0123456789")
	dig = [random.choice(lis) for _ in range(digit)]
	return "".join(dig), random.choice(domains_list)

def get_teks(accept, key):
	cek = r.get(f'{API}/{key}', headers={"accept": accept}).text
	if "error" in cek:
		return "-"
	else:
		return cek.strip()


def deleteMail():
   pass


def inbox_data(email): 
    raw_data = r.get(f'{API}?inbox={email}').text
    if "404" in raw_data:
        pass
    elif "data" in raw_data:
        z = json.loads(raw_data)
        for data in z["data"]:
            raw_msg = json.loads(r.get(f'{API}/{data["id"]}').text)  
            sender_name = raw_msg["data"]["sender"]["display_name"]  
            sender = raw_msg["data"]["sender"]["email"] 
            subject  = raw_msg["data"]["subject"]
            date = raw_msg['data']['created_at']        
            content  = get_teks("text/html,text/plain",data["id"])
            atc = raw_msg["data"]["attachments"]
            if atc == []:
                name="none"
                file=b"none"
            else:
                for atch in atc:
                    id = atch["id"]
                    name = atch["file_name"]
                    req = r.get(f'{API}/{data["id"]}/attachments/{id}')
                    file = req.content
            r.delete(f'{API}/{data["id"]}')      
            inbox=inbox_msg(sender=sender,senderName=sender_name,subject=subject,date=date,content=content,file=file,fileName=name)
            db.session.add(inbox)
            db.session.commit()
            
           

    
set_name, domain = get_random(10)

@app.route('/',methods=['Get','POST'])
def home():
    email=set_name+"@"+domain
    inbox_data(email)
    inbox = inbox_msg.query.all()
    return render_template('index.html',email=email,inbox=inbox)
            

@app.route('/delete/<int:no>')
def delete(no):
    inbox = inbox_msg.query.filter_by(no=no).first()
    db.session.delete(inbox)
    db.session.commit()
    return redirect("/")

@app.route('/content/<int:no>')
def content(no):
    inbox=inbox_msg.query.filter_by(no=no).first()
   
    return render_template('msg.html',inbox=inbox)

@app.route('/download/<int:no>')
def download(no):
    inbox=inbox_msg.query.filter_by(no=no).first()
    return send_file(BytesIO(inbox.file),attachment_filename=inbox.fileName,as_attachment=True)
    
@app.route('/sign')
def sign():
   
    return render_template('sign.html')

@app.route('/login')
def login():
   
    return render_template('login.html')

@app.route('/doc')
def doc():
   
    return render_template('doc.html')


# example 
@app.route('/ex')
def ex():
   
    return render_template('ex.html')
 
if __name__ == '__main__':
    app.run(debug=True, port=9080)    
 

    




#!/usr/bin/env python

import IPython


from flask import Flask,render_template,request
app = Flask(__name__)

from flask.ext.socketio import SocketIO,emit
socketio = SocketIO(app)

@app.route("/")
def hello():
  return render_template('upload.html')

@app.route("/upload",methods=['POST'])
def upload_cards():
  #rudimentary.. better: http://flask.pocoo.org/docs/0.10/patterns/fileuploads/#uploading-files
  request.files['proccard'].save('uploads/proc_card.dat')
  request.files['paramcard'].save('uploads/param_card.dat')
  return render_template('running.html')

@app.route("/run")
def runview():
  return render_template('running.html')
  
@socketio.on('runanalysis')
def handle_my_custom_event():
  import subprocess
  print 'ok.. now run the analysis....'
  p = subprocess.Popen(['/Users/lukas/heptools/madgraph-1.5.10/bin/mg5','-f','mg5.cmd'],
                      stdout = subprocess.PIPE,
                      stderr = subprocess.PIPE)
  while True:
    s =  p.stdout.readline()
    if not s: break
    import time
    time.sleep(0.01)
    import re
    strip_ansi =  re.sub(r'\x1b\[([0-9,A-Z]{1,2}(;[0-9]{1,2})?(;[0-9]{3})?)?[m|K]?', '', s)
    emit('respond',strip_ansi)
  print "emit some stuff here"
  return
  
if __name__ == "__main__":
    socketio.run(app)
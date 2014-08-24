#!/usr/bin/env python

import IPython


from flask import Flask,render_template,request,url_for,redirect
app = Flask(__name__)
app.debug = True
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
  return redirect(url_for('runview'))

@app.route("/run")
def runview():
  return render_template('running.html')

p = None

@socketio.on('killer')
def killer():
  print 'killing'
  global p
  if p is not None: 
    p.kill()
    print 'killed'

def printer(p,req):
  with app.test_request_context():
    while p.poll() is None:
      import time
      import re
      s = p.stdout.readline()
      time.sleep(0.005)
      strip_ansi =  re.sub(r'\x1b\[([0-9,A-Z]{1,2}(;[0-9]{1,2})?(;[0-9]{3})?)?[m|K]?', '', s)
      socketio.emit('respond',strip_ansi)
    (stdout,_) = p.communicate()
    socketio.emit('respond',stdout)      
    print "returning printer"
    return

def workflow(req):
  with app.test_request_context():
    request = req
    socketio.emit('update-stage','madgraph')
    import subprocess
    import threading
    p = subprocess.Popen(['/Users/lukas/heptools/madgraph-1.5.10/bin/mg5','-f','mg5.cmd'],
                        stdout = subprocess.PIPE,
                        stderr = subprocess.PIPE,bufsize=0)
                        
    printer(p,request)
    socketio.emit('update-stage','pythia')
    subprocess.call('''gunzip -c ./madgraphrun/Events/output/events.lhe.gz > ./madgraphrun/Events/output/events.lhe''',shell=True)
    p = subprocess.Popen('''PYTHIA8DATA=`pythia8-config --xmldoc` ./pythiarun/pythiarun pythiasteering.cmnd pythiarun/output.hepmc''',
                  shell=True,
                  stdout = subprocess.PIPE,
                  stderr = subprocess.PIPE)
    printer(p,request)
    socketio.emit('update-stage','rivet')
    # p = subprocess.Popen('''PYTHIA8DATA=`pythia8-config --xmldoc` ./pythiarun/pythiarun pythiasteering.cmnd pythiarun/output.hepmc''',
    #               shell=True,
    #               stdout = subprocess.PIPE,
    #               stderr = subprocess.PIPE)
    # t = threading.Thread(target=printer, args=(request,))
    # t.start()
    # p.communicate()
    # t.join()

                        
@socketio.on('runanalysis')
def handle_my_custom_event():
  import subprocess
  print 'ok.. now run the analysis....'
  import threading
  from multiprocessing import Process
  wfthread = threading.Thread(target=workflow,args=(request,))
  wfthread.start()
  print "emit some stuff here"
  return
  
if __name__ == "__main__":
    socketio.run(app)
#!/usr/bin/env python

import IPython
import gevent.subprocess as subprocess

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
  mode = request.form.get('mode',None)
  if len(request.files) == 0:
    import shutil
    shutil.copy('demofiles/proc_card.dat','uploads/proc_card.dat',)
    shutil.copy('demofiles/param_card.dat','uploads/param_card.dat',)
  else:
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


def workflow(req):
  with app.test_request_context():
    request = req
    socketio.emit('update-stage','madgraph')
    
    import cookbook
    import backend
    steps = ['madgraph','evgen']
    
    for step in steps:
      socketio.emit('update-stage',step)
      backend.printandwait(socketio,app,getattr(cookbook,step)(), req)
      print "done with {}".format(step)

                        
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
  
@app.route("/amitags",methods=['GET'])
def amitags():
    dataset = request.args.get('dataset')
    import requests
    from flask import json,jsonify
    if dataset is not None:
      response = requests.get('http://localhost:10003',params = {'dataset':dataset}).content
      jsondata = json.loads(response)
      ordered_data = list(sorted(jsondata.iteritems(),key=lambda x:x[0]))
      return render_template('amiinfo.html',data = ordered_data, dataset = dataset)
    else:
      return 'no dataset provided'  
  
if __name__ == "__main__":
    socketio.run(app,host='0.0.0.0',port=8000)

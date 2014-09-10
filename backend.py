
def printandwait(socketio,app,p,req):
  with app.test_request_context():
    while p.poll() is None:
      import time
      import re
      s = p.stdout.readline()
      time.sleep(0.002)
      strip_ansi =  re.sub(r'\x1b\[([0-9,A-Z]{1,2}(;[0-9]{1,2})?(;[0-9]{3})?)?[m|K]?', '', s)
      socketio.emit('respond',strip_ansi)
    (stdout,stderr) = p.communicate()
    socketio.emit('respond',stdout)      
    return

import os
from app import app, socketio

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    #app.run(host='0.0.0.0', port=port, threaded=4)
    socketio.run(app, host='0.0.0.0', port=port, debug=False)

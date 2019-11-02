from flask import Flask, render_template, request, make_response, g
from redis import Redis
import os
import socket
import random
import json

option_a = os.getenv('OPTION_A', "Cats")
# gjnote: this is to get the form options
option_b = os.getenv('OPTION_B', "Dogs")
option_c = os.getenv('OPTION_C', "Donkeys")
# gjnote: By default, the hostname inside a container will be the short id of that container
hostname = socket.gethostname()

app = Flask(__name__)

def get_redis():
    if not hasattr(g, 'redis'):
        # gjnote: A namespace object that can store data during an application context
        g.redis = Redis(host="redis", db=0, socket_timeout=5)
    return g.redis

# gjnote: Routing that handle both the POST and GET request
@app.route("/", methods=['POST','GET'])
def hello():
    voter_id = request.cookies.get('voter_id')
    if not voter_id:
        voter_id = hex(random.getrandbits(64))[2:-1]

    vote = None

    print("Inside the root endpoint of vote")

    # gjnote: when the request is after the user clicks one option
    if request.method == 'POST':
        redis = get_redis()
        # gjnote: Get vote data from form of the request, and send it to redis
        vote = request.form['vote']
        print("The vote value is", vote)
        # gjnote: output is like this: ('The vote value is', u'a')
        data = json.dumps({'voter_id': voter_id, 'vote': vote})
        # gjnote: output is like this: ('The data value is', '{"vote": "a", "voter_id": "77fbfdf7f8fbfcb6"}')

        print("The data value is", data)
        redis.rpush('votes', data)

    # gjnote: pass option and values to view (index.html). Render it
    resp = make_response(render_template(
        'index.html',
        option_a=option_a,
        option_b=option_b,
        option_c=option_c,
        hostname=hostname,
        vote=vote,
    ))
    resp.set_cookie('voter_id', voter_id)
    return resp


if __name__ == "__main__":
    # The flask web app runs from here
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)

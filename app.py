#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# @file: main.py

import json
import cPickle as pickle
from functools import wraps

from flask import Flask, Response, render_template, request, redirect, url_for


app = Flask(__name__)
app.config.from_pyfile('config.py')
with open('data/ip_blocks_to_pos', 'rb') as f:
    ip_blocks = pickle.load(f)


def json_response(method):
    @wraps(method)
    def decorated(*args, **kwargs):
        return Response(json.dumps(method(*args, **kwargs)),
                        mimetype='application/json')
    return decorated


@app.route('/query/', methods=['GET', 'POST'])
@json_response
def query():
    o_req = request.json
    q = o_req['query']
    ip_list = [i.strip() for i in q.strip().split(',')]
    results = []
    for ip in ip_list:
        arr = map(int, ip.split('.'))
        id_ = reduce(lambda x, y: x*256 + y, arr)
        for k, v in ip_blocks:
            if k[0] <= id_ and k[1] > id_:
                results.append(dict(pos=v, ip=ip, desc=str(v)))
    print 'results:', results
    ret = {
        'error': int(not results),
        'message': 'Address not in US',
        'results': results,
    }
    return ret


@app.route('/vis/state-ip/', methods=['GET', 'POST'])
def visualize_state_ip_stats():
    return redirect(url_for('static', filename='images/state_ip_stats.png'))


@app.route('/', methods=['GET', 'POST'])
def homepage():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()

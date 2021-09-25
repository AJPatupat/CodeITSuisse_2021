import logging
import json

from flask import request, jsonify

from codeitsuisse import app

logger = logging.getLogger(__name__)

import hashlib
from math import log

@app.route('/cipher-cracking', methods=['POST'])
def cipher_cracking():
    input = request.get_json()
    logging.info("Input: {}".format(input))

    output = []
    for test_case in input:
        X = int(test_case['X'])
        fx = (X+1)/X * (0.57721566 + log(X) + 0.5/X) - 1
        FX = '::{:.3f}'.format(fx)
        for K in range(1+10**test_case['D']):
            if hashlib.sha256((str(K)+FX).encode('utf-8')).hexdigest() == test_case['Y']:                    
                break
        output.append(K)

    logging.info("Output: {}".format(output))
    return json.dumps(output)

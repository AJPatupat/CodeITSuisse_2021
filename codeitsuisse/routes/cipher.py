import logging
import json

from flask import request, jsonify

from codeitsuisse import app

logger = logging.getLogger(__name__)

import hashlib
SHA = hashlib.sha256()

@app.route('/cipher-cracking', methods=['POST'])
def cipher_cracking():
    input = request.get_json()
    logging.info("Input: {}".format(input))

    output = []
    for test_case in input:
        if test_case['D'] == 1:
            X = int(test_case['X'])
            fx = sum([(X+1-i)/(i*X) for i in range(1,X+1)])
            FX = '::{.3f}'.format(fx)
            for K in range(1, 10**test_case['D']):
                SHA.update(bytes(str(K)+FX))
                SHA.digest()
                if SHA.hexdigest() == test_case['Y']:
                    break
            output.append(K)
        else:
            output.append(1)

    logging.info("Output: {}".format(output))
    return json.dumps(output)

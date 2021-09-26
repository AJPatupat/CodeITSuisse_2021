import logging
import json

from flask import request, jsonify

from codeitsuisse import app

logger = logging.getLogger(__name__)

import bisect
from math import gcd

@app.route('/stig/perry', methods=['POST'])
def stig_perry():
    input = request.get_json()
    logging.info("Input: {}".format(input))

    output = []
    for test_case in input:
        M = test_case['maxRating']
        questions = [
            (question[0]['from'], question[0]['to'])
            for question in test_case['questions']
        ]
        questions.sort()
        p = 1 + len(questions)
        for question in questions:
            num_from = question[0]
            num_to = question[0]
            pos_from = bisect.bisect_left(questions, (num_from+1, -1))
            pos_to = bisect.bisect_left(questions, (num_to, -1))
            p += pos_to-pos_from
        q = M
        g = gcd(p,q)
        p = p // g
        q = q // g
        output.append({'p':p,'q':q})

    logging.info("Output: {}".format(output))
    return json.dumps(output)

import logging
import json

from flask import request, jsonify

from codeitsuisse import app

logger = logging.getLogger(__name__)

import numpy as np
from scipy.stats import norm


def expected_return_per_view(option_dict, view_dict):
    strike = option_dict['strike']
    premium = option_dict['premium']

    if option_dict['type'] == 'call':
        if strike >= view_dict['max']:
            return -premium
        else:
            mu = view_dict['mean']
            sigma = np.sqrt(view_dict['var'])
            a = view_dict['min']
            b = view_dict['max']
            c = max(a, strike)
            aa = (a-mu)/sigma
            bb = (b-mu)/sigma
            cc = (c-mu)/sigma
            diff_cdf_bb_aa = norm.cdf(bb) - norm.cdf(aa)
            diff_cdf_bb_cc = norm.cdf(bb) - norm.cdf(cc)
            diff_pdf_bb_cc = norm.pdf(bb) - norm.pdf(cc)
            multiplier0 = diff_cdf_bb_cc / diff_cdf_bb_aa
            multiplier1 = diff_pdf_bb_cc / diff_cdf_bb_aa
            return multiplier0 * (mu - strike) - multiplier1 * sigma - premium

    else:
        if strike <= view_dict['min']:
            return -premium
        else:
            mu = view_dict['mean']
            sigma = np.sqrt(view_dict['var'])
            a = view_dict['min']
            b = view_dict['max']
            d = min(b, strike)
            aa = (a-mu)/sigma
            bb = (b-mu)/sigma
            dd = (d-mu)/sigma
            diff_cdf_bb_aa = norm.cdf(bb) - norm.cdf(aa)
            diff_cdf_dd_aa = norm.cdf(dd) - norm.cdf(aa)
            diff_pdf_dd_aa = norm.pdf(dd) - norm.pdf(aa)
            multiplier0 = diff_cdf_dd_aa / diff_cdf_bb_aa
            multiplier1 = diff_pdf_dd_aa / diff_cdf_bb_aa
            return multiplier0 * (strike - mu) + multiplier1 * sigma - premium


@app.route('/optopt', methods=['POST'])
def optopt():
    input = request.get_json()
    #logging.info("Input: {}".format(input))

    option_dicts = input['options']
    view_dicts = input['view']

    strike = np.empty(len(option_dicts))
    premium = np.empty(len(option_dicts))
    is_call = np.empty(len(option_dicts))
    for i in range(len(option_dicts)):
        strike[i] = option_dicts[i]['strike']
        premium[i] = option_dicts[i]['premium']
        is_call[i] = 1 if option_dicts[i]['type'] == 'call' else 0

    avg = np.empty(len(view_dicts))
    var = np.empty(len(view_dicts))
    a = np.empty(len(view_dicts))
    b = np.empty(len(view_dicts))
    w = np.empty(len(view_dicts))
    for i in range(len(view_dicts)):        
        avg[i] = view_dicts[i]['mean']
        var[i] = view_dicts[i]['var']
        a[i] = view_dicts[i]['min']
        b[i] = view_dicts[i]['max']
        w[i] = view_dicts[i]['weight']

    std = np.sqrt(var)
    aa = (a-avg)/std
    bb = (b-avg)/std
    cdf_aa = norm.cdf(aa)
    cdf_bb = norm.cdf(bb)
    pdf_aa = norm.pdf(aa)
    pdf_bb = norm.pdf(bb)

    c = np.maximum(np.expand_dims(strike,1), np.expand_dims(a,0))
    d = np.minimum(np.expand_dims(strike,1), np.expand_dims(b,0))
    cc = (c-avg)/std
    dd = (d-avg)/std
    cdf_cc = norm.cdf(cc)
    cdf_dd = norm.cdf(dd)
    pdf_cc = norm.pdf(cc)
    pdf_dd = norm.pdf(dd)

    expected_returns = np.zeros(len(option_dicts))
    for i in range(len(option_dicts)):
        for j in range(len(view_dicts)):
            expected_return = -premium[i]

            if is_call[i] == 1 and strike[i] < b[j]:
                increment = 0
                increment += (cdf_bb[j]-cdf_cc[i][j])*(avg[j]-strike[i])
                increment += -(pdf_bb[j]-pdf_cc[i][j])*(std[j]) 
                increment /= (cdf_bb[j]-cdf_aa[j])
                expected_return += increment

            if is_call[i] == 0 and strike[i] > a[j]:
                increment = 0
                increment += (cdf_dd[i][j]-cdf_aa[j])*(strike[i]-avg[j])
                increment += -(pdf_dd[i][j]-pdf_aa[j])*(std[j]) 
                increment /= (cdf_bb[j]-cdf_aa[j])
                expected_return += increment

            expected_returns[i] += w[j] * expected_return

    pos = np.argmax(np.abs(expected_returns))
    output = [0] * len(option_dicts)
    if expected_returns[pos] > 0:
        output[pos] = 100
    else:
        output[pos] = -100

    #logging.info("Output: {}".format(output))
    return json.dumps(output)

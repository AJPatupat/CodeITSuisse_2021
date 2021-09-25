import logging
import json

from flask import request, jsonify

from codeitsuisse import app

logger = logging.getLogger(__name__)

import heapq

@app.route('/parasite', methods=['POST'])
def parasite():
    input = request.get_json()
    logging.info("Input: {}".format(input))

    output = []
    for room_input in input:
        room_output = {}
        room_output['room'] = room_input['room']

        grid_O = room_input['grid']

        row_count = len(grid_O)
        col_count = len(grid_O[0])
        max_count = row_count * col_count

        grid_A = [ [0]*col_count for _ in range(row_count) ]
        grid_B = [ [0]*col_count for _ in range(row_count) ]
        grid_X = [ [0]*col_count for _ in range(row_count) ]

        seen_A = [ [False]*col_count for _ in range(row_count) ]
        seen_B = [ [False]*col_count for _ in range(row_count) ]
        seen_X = [ [False]*col_count for _ in range(row_count) ]

        for row in range(row_count):
            for col in range(col_count):
                val = grid_O[row][col]
                if val == 0:
                    grid_A[row][col] = -max_count
                    grid_B[row][col] = -max_count
                    grid_X[row][col] = max_count
                elif val == 1 or val == 2:
                    grid_A[row][col] = max_count
                    grid_B[row][col] = max_count
                    grid_X[row][col] = max_count
                elif val == 3:
                    grid_A[row][col] = 0
                    grid_B[row][col] = 0
                    grid_X[row][col] = 0
                    parasite_row = row
                    parasite_col = col

        pq_A = [(grid_A[parasite_row][parasite_col], parasite_row, parasite_col)]
        while len(pq_A) != 0:
            val, row, col = heapq.heappop(pq_A)
            if not seen_A[row][col]:
                seen_A[row][col] = True
                val += 1
                for i in range(row-1, row+2):
                    if i >= 0 and i < row_count:
                        j = col
                        if grid_A[i][j] > val:
                            grid_A[i][j] = val
                            heapq.heappush(pq_A, (val, i, j))
                for j in range(col-1, col+2):
                    if j >= 0 and j < col_count:
                        i = row
                        if grid_A[i][j] > val:
                            grid_A[i][j] = val
                            heapq.heappush(pq_A, (val, i, j))

        pq_B = [(grid_B[parasite_row][parasite_col], parasite_row, parasite_col)]
        while len(pq_B) != 0:
            val, row, col = heapq.heappop(pq_B)
            if not seen_B[row][col]:
                seen_B[row][col] = True
                val += 1
                for i in range(row-1, row+2):
                    if i >= 0 and i < row_count:
                        for j in range(col-1, col+2):
                            if j >= 0 and j < col_count:
                                if grid_B[i][j] > val:
                                    grid_B[i][j] = val
                                    heapq.heappush(pq_B, (val, i, j))

        pq_X = [(grid_X[parasite_row][parasite_col], parasite_row, parasite_col)]
        while len(pq_X) != 0:
            val, row, col = heapq.heappop(pq_X)
            if not seen_X[row][col]:
                seen_X[row][col] = True
                if grid_O[row][col] == 0 or grid_O[row][col] == 2:
                    val += 1
                for i in range(row-1, row+2):
                    if i >= 0 and i < row_count:
                        j = col
                        if grid_X[i][j] > val:
                            grid_X[i][j] = val
                            heapq.heappush(pq_X, (val, i, j))
                for j in range(col-1, col+2):
                    if j >= 0 and j < col_count:
                        i = row
                        if grid_X[i][j] > val:
                            grid_X[i][j] = val
                            heapq.heappush(pq_X, (val, i, j))

        room_output['p1'] = {}
        for row_col_str in room_input['interestedIndividuals']:
            row_col_list = [int(int_str) for int_str in row_col_str.split(',')]
            row = row_col_list[0]
            col = row_col_list[1]
            if grid_O[row][col] == 1 and grid_A[row][col] < max_count:
                room_output['p1'][row_col_str] = grid_A[row][col]
            else:
                room_output['p1'][row_col_str] = -1

        room_output['p2'] = 0
        for row in range(row_count):
            for col in range(col_count):
                if grid_O[row][col] == 1:
                   if room_output['p2'] < grid_A[row][col]:
                       room_output['p2'] = grid_A[row][col]
        if room_output['p2'] == max_count:
            room_output['p2'] = -1

        room_output['p3'] = 0
        for row in range(row_count):
            for col in range(col_count):
                if grid_O[row][col] == 1:
                   if room_output['p3'] < grid_B[row][col]:
                       room_output['p3'] = grid_B[row][col]
        if room_output['p3'] == max_count:
            room_output['p3'] = -1

        room_output['p4'] = 0
        for row in range(row_count):
            for col in range(col_count):
                if grid_O[row][col] == 1:
                   if room_output['p4'] < grid_X[row][col]:
                       room_output['p4'] = grid_X[row][col]
        if room_output['p4'] == max_count:
            room_output['p4'] = -1

        output.append(room_output)

    logging.info("Output: {}".format(output))
    return json.dumps(output)

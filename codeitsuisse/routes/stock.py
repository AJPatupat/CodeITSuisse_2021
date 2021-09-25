import logging
import json

from flask import request, jsonify

from codeitsuisse import app

logger = logging.getLogger(__name__)

import heapq

@app.route('/stock-hunter', methods=['POST'])
def stock_hunter():
    inputs = request.get_json()
    logging.info("Input: {}".format(inputs))
    outputs = []

    for input in inputs:
        
        x_count = 20 + max(input['entryPoint']['first'], input['targetPoint']['first'])
        y_count = 20 + max(input['entryPoint']['second'], input['targetPoint']['second'])
        x_step = input['horizontalStepper']
        y_step = input['verticalStepper']
        grid_mod = input['gridKey']
        grid_add = input['gridDepth']

        grid = [[0]*x_count for _ in range(y_count)]
        for x in range(1, x_count):
            grid[0][x] = (x*x_step+grid_add)%grid_mod
        for y in range(1, y_count):
            grid[y][0] = (y*y_step+grid_add)%grid_mod
            for x in range(1, x_count):
                grid[y][x] = (grid[y][x-1]*grid[y-1][x]+grid_add)%grid_mod
        for y in range(y_count):
            for x in range(x_count):
                grid[y][x] = grid[y][x] % 3
                if grid[y][x] == 0:
                    grid[y][x] = 3

        x_max = max(input['entryPoint']['first'], input['targetPoint']['first'])
        x_min = min(input['entryPoint']['first'], input['targetPoint']['first'])
        y_max = max(input['entryPoint']['second'], input['targetPoint']['second'])
        y_min = min(input['entryPoint']['second'], input['targetPoint']['second'])
        grid_map = [['L']*(1+x_max-x_min) for _ in range(1+y_max-y_min)]
        for y in range(1+y_max-y_min):
            for x in range(1+x_max-x_min):
                val = grid[y+y_min][x+x_min]
                if val == 1:
                    grid_map[y][x] = 'S'
                elif val == 2:
                    grid_map[y][x] = 'M'

        cost = [[x_count*y_count*10]*x_count for _ in range(y_count)]
        seen = [[False]*x_count for _ in range(y_count)]
        pq = [(0, input['targetPoint']['first'], input['targetPoint']['second'])]
        while len(pq) != 0:
            val, x, y = heapq.heappop(pq)
            if not seen[y][x]:
                seen[y][x] = True
                val += grid[y][x]
                for i in range(x-1, x+2):
                    if i >= 0 and i < x_count:
                        j = y
                        if cost[j][i] > val:
                            cost[j][i] = val
                            heapq.heappush(pq, (val, i, j))
                for j in range(y-1, y+2):
                    if j >= 0 and j < y_count:
                        i = x
                        if cost[j][i] > val:
                            cost[j][i] = val
                            heapq.heappush(pq, (val, i, j))
        min_cost = cost[input['entryPoint']['first']][input['entryPoint']['second']]

        output = {'gridMap':grid_map, 'minimumCost':min_cost}
        outputs.append(output)

    logging.info("Output: {}".format(outputs))
    return json.dumps(outputs)

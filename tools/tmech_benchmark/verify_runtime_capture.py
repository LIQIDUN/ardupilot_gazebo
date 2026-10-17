#!/usr/bin/env python3
"""Cross-check saved `gz model -i` collision poses and boxes at full precision."""
import argparse
import json
import re
from pathlib import Path

import numpy as np

from validate_bundle import close, quaternion_matrix, validate


def direct_blocks(text, field):
    blocks = []
    depth = 0
    collecting = None
    for line in text.splitlines(keepends=True):
        if depth == 0 and re.fullmatch(r'\s*' + field + r'\s*\{\s*', line):
            collecting = []
        if collecting is not None:
            collecting.append(line)
        depth += line.count('{') - line.count('}')
        if depth < 0:
            raise ValueError('Unbalanced runtime model information')
        if depth == 0 and collecting is not None:
            blocks.append(''.join(collecting).split('{', 1)[1].rsplit('}', 1)[0])
            collecting = None
    if depth != 0:
        raise ValueError('Truncated runtime model information')
    return blocks


def single_block(text, field):
    blocks = direct_blocks(text, field)
    if len(blocks) != 1:
        raise ValueError('Expected one runtime field: ' + field)
    return blocks[0]


def vector(text, fields):
    result = []
    for field in fields:
        match = re.search(r'^\s*' + field + r':\s*([-+0-9.eE]+)\s*$', text, re.MULTILINE)
        if match is None:
            raise ValueError('Missing runtime scalar ' + field)
        result.append(float(match.group(1)))
    return np.array(result)


def pose(text):
    document = single_block(text, 'pose')
    position = vector(single_block(document, 'position'), ['x', 'y', 'z'])
    quaternion = vector(single_block(document, 'orientation'), ['x', 'y', 'z', 'w'])
    return position, quaternion_matrix(quaternion)


def size(text):
    geometry = single_block(text, 'geometry')
    return vector(single_block(single_block(geometry, 'box'), 'size'), ['x', 'y', 'z'])


def verify_runtime(bundle, capture):
    validate(bundle)
    records = json.loads((bundle / 'obstacles.json').read_text())['obstacles']
    transform = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]])
    results = []
    for index, record in enumerate(records):
        text = (capture / 'model_{:02d}.txt'.format(index)).read_text()
        match = re.match(r'name: "([^"]+)"', text)
        if match is None or match.group(1) != record['name']:
            raise ValueError('Runtime model identity mismatch')
        model_position, model_rotation = pose(text)
        link = single_block(text, 'link')
        link_position, link_rotation = pose(link)
        collision = single_block(link, 'collision')
        collision_position, collision_rotation = pose(collision)
        close(size(collision), record['size_m'], 'runtime collision size')
        close(model_position, record['gazebo']['origin_m'], 'runtime model origin')
        close(model_rotation, record['gazebo']['rotation'], 'runtime model rotation')
        close(link_position, [0, 0, 0], 'runtime link pose')
        close(link_rotation, np.eye(3), 'runtime link rotation')
        close(collision_position, [0, 0, record['size_m'][2] / 2], 'runtime collision offset')
        close(collision_rotation, np.eye(3), 'runtime collision rotation')
        visuals = [block for block in direct_blocks(link, 'visual') if direct_blocks(block, 'geometry')]
        if len(visuals) != 1:
            raise ValueError('Expected exactly one physical geometry visual')
        visual_position, visual_rotation = pose(visuals[0])
        close(size(visuals[0]), record['size_m'], 'runtime visual size')
        close(visual_position, collision_position, 'runtime visual/collision pose')
        close(visual_rotation, collision_rotation, 'runtime visual/collision rotation')
        center = model_position + model_rotation @ (link_position + link_rotation @ collision_position)
        error = float(np.max(np.abs(transform @ center - record['planner']['center'])))
        close(transform @ center, record['planner']['center'], 'runtime/planner collision center')
        results.append({'name': record['name'], 'collision_count': 1, 'full_precision_origin_m': model_position.tolist(),
                        'collision_offset_m': collision_position.tolist(), 'max_planner_center_error_m': error})
    return {'passed': True, 'scope': 'SAVED_RUNTIME_ENVIRONMENT_COLLISION_GEOMETRY_ONLY',
            'bundle': str(bundle), 'capture': str(capture), 'models': results,
            'max_planner_center_error_m': max(item['max_planner_center_error_m'] for item in results)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--capture', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    arguments = parser.parse_args()
    result = verify_runtime(arguments.bundle, arguments.capture)
    with arguments.output.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'passed': True, 'models': len(result['models']),
                      'max_planner_center_error_m': result['max_planner_center_error_m']}))


if __name__ == '__main__':
    main()

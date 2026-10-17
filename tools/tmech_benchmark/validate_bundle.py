#!/usr/bin/env python3
"""Independent SDF collision/visual/OBB/target consistency check; no safety certificate."""
import argparse
import hashlib
import itertools
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np


def rpy_matrix(angles):
    roll, pitch, yaw = angles
    sr, cr = math.sin(roll), math.cos(roll)
    sp, cp = math.sin(pitch), math.cos(pitch)
    sy, cy = math.sin(yaw), math.cos(yaw)
    return np.array([[cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
                     [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
                     [-sp, cp * sr, cp * cr]])


def pose(element):
    values = np.array([float(value) for value in element.findtext('pose', '0 0 0 0 0 0').split()])
    if values.shape != (6,) or not np.isfinite(values).all():
        raise ValueError('Invalid pose')
    return values[:3], rpy_matrix(values[3:])


def close(actual, expected, label):
    if np.shape(actual) != np.shape(expected) or not np.allclose(actual, expected, atol=2e-12, rtol=0):
        raise ValueError('Mismatch: ' + label)


def quaternion_matrix(quaternion):
    qx, qy, qz, qw = quaternion
    close(np.dot(quaternion, quaternion), 1.0, 'quaternion norm')
    return np.array([[1 - 2 * (qy * qy + qz * qz), 2 * (qx * qy - qz * qw), 2 * (qx * qz + qy * qw)],
                     [2 * (qx * qy + qz * qw), 1 - 2 * (qx * qx + qz * qz), 2 * (qy * qz - qx * qw)],
                     [2 * (qx * qz - qy * qw), 2 * (qy * qz + qx * qw), 1 - 2 * (qx * qx + qy * qy)]])


def validate(directory):
    manifest = json.loads((directory / 'manifest.json').read_text())
    expected_files = {'benchmark.world', 'parameters.json', 'obstacles.json', 'targets.json'}
    if set(manifest['files_sha256']) != expected_files:
        raise ValueError('Incomplete bundle manifest')
    for name, checksum in manifest['files_sha256'].items():
        if hashlib.sha256((directory / name).read_bytes()).hexdigest() != checksum:
            raise ValueError('Hash mismatch: ' + name)
    document = json.loads((directory / 'obstacles.json').read_text())
    parameters = json.loads((directory / 'parameters.json').read_text())
    transform = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]])
    close(document['transform_planner_from_gazebo'], transform, 'frame transform')
    records = {item['name']: item for item in document['obstacles']}
    if len(records) != len(document['obstacles']):
        raise ValueError('Duplicate obstacle names')
    root = ET.parse(directory / 'benchmark.world').getroot()
    if root.findall('.//include') or root.findall('.//plugin'):
        raise ValueError('Environment-only bundle must have no includes or plugins')
    models = root.findall('./world/model')
    expected_count = 3 if parameters['scene'] == 'solar' else 6
    if len(models) != expected_count or {model.get('name') for model in models} != set(records):
        raise ValueError('SDF/manifest model set mismatch')
    signs = np.array(list(itertools.product((-1, 1), repeat=3)))
    parsed = []
    maximum_error = 0.0
    for model in models:
        record = records[model.get('name')]
        if model.findtext('static') not in ('true', '1'):
            raise ValueError('All benchmark solids must be static')
        links = model.findall('link')
        if len(links) != 1:
            raise ValueError('One link per obstacle required')
        link = links[0]
        collision, visual = link.findall('collision'), link.findall('visual')
        if len(collision) != 1 or len(visual) != 1:
            raise ValueError('Exactly one physical collision and matching visual required')
        origin, rotation = pose(model)
        link_position, link_rotation = pose(link)
        collision_position, collision_rotation = pose(collision[0])
        visual_position, visual_rotation = pose(visual[0])
        size = np.array([float(value) for value in collision[0].findtext('geometry/box/size', '').split()])
        visual_size = [float(value) for value in visual[0].findtext('geometry/box/size', '').split()]
        if size.shape != (3,) or not np.isfinite(size).all() or np.any(size <= 0):
            raise ValueError('Collision must be a positive finite box')
        close(size, visual_size, 'collision/visual dimensions')
        close(collision_position, visual_position, 'collision/visual translation')
        close(collision_rotation, visual_rotation, 'collision/visual rotation')
        close(link_position, [0, 0, 0], 'link origin')
        close(link_rotation, np.eye(3), 'link rotation')
        close(collision_rotation, np.eye(3), 'box local rotation')
        close(collision_position, [0, 0, size[2] / 2], 'bottom origin convention')
        close([float(value) for value in record['name'].split('_')[2:5]], size, 'name dimensions')
        center = origin + rotation @ collision_position
        vertices = (signs * size / 2) @ rotation.T + center
        planner_vertices = vertices @ transform.T
        close(record['size_m'], size, 'record size')
        close(record['gazebo']['origin_m'], origin, 'record origin')
        close(record['gazebo']['center_m'], center, 'record center')
        close(record['gazebo']['rotation'], rotation, 'record rotation')
        close(quaternion_matrix(record['gazebo']['quat_xyzw']), rotation, 'Gazebo quaternion')
        close(record['gazebo']['vertices_m'], vertices, 'Gazebo vertices')
        close(record['planner']['center'], transform @ center, 'planner center')
        close(record['planner']['size'], size, 'planner size')
        close(record['planner']['rotation'], transform @ rotation, 'planner rotation')
        close(quaternion_matrix(record['planner']['quat']), transform @ rotation, 'planner quaternion')
        close(record['planner']['vertices_m'], planner_vertices, 'planner vertices')
        maximum_error = max(maximum_error, float(np.max(np.abs(record['planner']['vertices_m'] - planner_vertices))))
        if record['role'] == 'ground':
            close(np.max(vertices[:, 2]), 0, 'ground top')
        elif np.min(vertices[:, 2]) <= 0 or np.max(np.abs(vertices[:, :2])) >= 20:
            raise ValueError('Solid penetrates ground or exceeds its footprint')
        parsed.append((record['name'], center, rotation, size))
    scene_rotation = rpy_matrix([0, -math.radians(parameters['beta_deg']), 0])
    lower = next(item for item in document['obstacles'] if item['role'] == 'lower')
    upper = next(item for item in document['obstacles'] if item['role'] == 'upper')
    normal = scene_rotation[:, 2]
    gap = np.dot(np.array(upper['gazebo']['center_m']) - lower['gazebo']['center_m'], normal)
    gap -= (upper['size_m'][2] + lower['size_m'][2]) / 2
    close(gap, parameters['clearance'], 'normal inner-surface clearance')
    if parameters['scene'] == 'shelf':
        sides = [next(item for item in document['obstacles'] if item['role'] == role) for role in ('left', 'right')]
        width = np.dot(np.array(sides[1]['gazebo']['center_m']) - sides[0]['gazebo']['center_m'], scene_rotation[:, 1])
        width -= (sides[0]['size_m'][1] + sides[1]['size_m'][1]) / 2
        close(width, parameters['width'], 'lateral inner-surface clearance')
    targets = json.loads((directory / 'targets.json').read_text())['targets']
    expected_targets = len(parameters['depths']) * len(parameters['lateral']) * len(parameters['orientation_deg'])
    if len(targets) != expected_targets or len(set(item['id'] for item in targets)) != expected_targets:
        raise ValueError('Target count/identity mismatch')
    for target in targets:
        position = np.array(target['gazebo']['position_m'])
        close(target['planner']['position_m'], transform @ position, 'target position')
        tool_rotation = quaternion_matrix(target['gazebo']['quat_xyzw'])
        close(quaternion_matrix(target['planner']['quat_xyzw']), transform @ tool_rotation, 'target orientation')
        local = scene_rotation.T @ (position - parameters['center'])
        close(local, [-parameters['length'] / 2 + target['depth_m'], target['lateral_m'],
                      -parameters['clearance'] / 2 + parameters['tool_offset']], 'target local coordinates')
        expected_tool = rpy_matrix([0, math.radians(target['orientation_delta_deg']), 0]) @ np.diag([1, -1, -1])
        close(tool_rotation, scene_rotation @ expected_tool, 'tool axis contract')
        for name, center, rotation, size in parsed:
            if np.all(np.abs(rotation.T @ (position - center)) <= size / 2):
                raise ValueError('Target in obstacle ' + name)
    return {'bundle': str(directory), 'status': 'GEOMETRY_CONSISTENT_ONLY', 'obstacles': len(parsed),
            'targets': len(targets), 'normal_clearance_m': float(gap), 'max_vertex_error_m': maximum_error,
            'robot_loaded': False, 'phase1': 'NOT_RUN', 'phase2': 'NOT_RUN', 'execution': 'NOT_RUN'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle', type=Path)
    parser.add_argument('--output', type=Path)
    arguments = parser.parse_args()
    result = validate(arguments.bundle)
    if arguments.output:
        with arguments.output.open('x') as stream:
            json.dump(result, stream, indent=2)
            stream.write('\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()

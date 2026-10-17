#!/usr/bin/env python3
"""Generate isolated, environment-only P54 worlds and lossless OBB/task bundles."""
import argparse
import hashlib
import itertools
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path


TRANSFORM = [[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]]


def matrix_product(left, right):
    return [[sum(first * second for first, second in zip(row, column))
             for column in zip(*right)] for row in left]


def rotate(rotation, vector):
    return [sum(first * second for first, second in zip(row, vector)) for row in rotation]


def translated(origin, vector):
    return [first + second for first, second in zip(origin, vector)]


def quaternion_product(left, right):
    lx, ly, lz, lw = left
    rx, ry, rz, rw = right
    return [lw * rx + lx * rw + ly * rz - lz * ry,
            lw * ry - lx * rz + ly * rw + lz * rx,
            lw * rz + lx * ry - ly * rx + lz * rw,
            lw * rw - lx * rx - ly * ry - lz * rz]


def pitch_rotation(angle):
    cosine, sine = math.cos(angle), math.sin(angle)
    return [[cosine, 0.0, sine], [0.0, 1.0, 0.0], [-sine, 0.0, cosine]]


def pitch_quaternion(angle):
    return [0.0, math.sin(angle / 2), 0.0, math.cos(angle / 2)]


def numbers(values):
    return ' '.join(format(value, '.17g') for value in values)


def add(parent, tag, text=None, **attributes):
    element = ET.SubElement(parent, tag, attributes)
    if text is not None:
        element.text = str(text)
    return element


def corners(center, rotation, size):
    return [translated(center, rotate(rotation, [sign * extent / 2 for sign, extent in zip(signs, size)]))
            for signs in itertools.product((-1, 1), repeat=3)]


def box_record(role, size, center, angle):
    rotation = pitch_rotation(angle)
    origin = translated(center, rotate(rotation, [0, 0, -size[2] / 2]))
    name = 'obs_box_' + '_'.join(format(value, '.17g') for value in size) + '_' + role
    planner_rotation = matrix_product(TRANSFORM, rotation)
    planner_center = rotate(TRANSFORM, center)
    return {
        'name': name, 'role': role, 'size_m': size,
        'gazebo': {'origin_m': origin, 'rpy_rad': [0.0, angle, 0.0], 'center_m': center,
                   'rotation': rotation, 'quat_xyzw': pitch_quaternion(angle),
                   'vertices_m': corners(center, rotation, size)},
        'planner': {'center': planner_center, 'size': size, 'rotation': planner_rotation,
                    'quat': quaternion_product([0, 0, math.sqrt(0.5), math.sqrt(0.5)], pitch_quaternion(angle)),
                    'vertices_m': corners(planner_center, planner_rotation, size)},
    }


def make_world(scene, records):
    sdf = ET.Element('sdf', {'version': '1.6'})
    world = add(sdf, 'world', name='tmech_' + scene)
    add(world, 'gravity', '0 0 -9.81')
    physics = add(world, 'physics', name='p54_ode', type='ode')
    add(physics, 'max_step_size', '0.001')
    add(physics, 'real_time_update_rate', '1000')
    light = add(world, 'light', name='p54_sun', type='directional')
    add(light, 'pose', '0 0 10 0 0 0')
    add(light, 'diffuse', '0.8 0.8 0.8 1')
    add(light, 'specular', '0.2 0.2 0.2 1')
    add(light, 'direction', '-0.5 0.2 -1')
    for record in records:
        model = add(world, 'model', name=record['name'])
        add(model, 'static', 'true')
        add(model, 'pose', numbers(record['gazebo']['origin_m'] + record['gazebo']['rpy_rad']))
        link = add(model, 'link', name='solid')
        for kind in ('collision', 'visual'):
            element = add(link, kind, name=kind)
            add(element, 'pose', numbers([0, 0, record['size_m'][2] / 2, 0, 0, 0]))
            add(add(add(element, 'geometry'), 'box'), 'size', numbers(record['size_m']))
            if kind == 'collision':
                surface = add(element, 'surface')
                friction = add(add(surface, 'friction'), 'ode')
                add(friction, 'mu', '0.8')
                add(friction, 'mu2', '0.8')
                contact = add(add(surface, 'contact'), 'ode')
                for tag, value in [('kp', '1000000'), ('kd', '1'), ('max_vel', '0.1'), ('min_depth', '0.001')]:
                    add(contact, tag, value)
            else:
                color = '0.2 0.45 0.65 1' if record['role'] != 'ground' else '0.5 0.5 0.5 1'
                material = add(element, 'material')
                add(material, 'ambient', color)
                add(material, 'diffuse', color)
    return ET.tostring(sdf, encoding='utf-8', xml_declaration=True) + b'\n'


def generate(parameters):
    numeric = [parameters[key] for key in ('beta_deg', 'clearance', 'width', 'length', 'thickness', 'tool_offset')]
    numeric += parameters['center'] + parameters['depths'] + parameters['lateral'] + parameters['orientation_deg']
    if not all(math.isfinite(value) for value in numeric):
        raise ValueError('All parameters must be finite')
    if not all(parameters[key] > 0 for key in ('clearance', 'width', 'length', 'thickness', 'tool_offset')):
        raise ValueError('Dimensions and tool offset must be positive')
    if abs(parameters['beta_deg']) >= 90:
        raise ValueError('This benchmark requires abs(beta) < 90 degrees')
    if parameters['tool_offset'] >= parameters['clearance']:
        raise ValueError('Tool offset must be inside the normal clearance')
    if any(not 0 < depth < parameters['length'] for depth in parameters['depths']):
        raise ValueError('Depths must be strictly inside (0, length)')
    if any(abs(value) >= parameters['width'] / 2 for value in parameters['lateral']):
        raise ValueError('Lateral targets must be strictly inside the aperture width')
    for key in ('depths', 'lateral', 'orientation_deg'):
        if not parameters[key] or len(set(parameters[key])) != len(parameters[key]):
            raise ValueError('Target axes must be nonempty and contain no duplicates')
    angle = -math.radians(parameters['beta_deg'])
    rotation = pitch_rotation(angle)
    length, width, gap, thickness = [parameters[key] for key in ('length', 'width', 'clearance', 'thickness')]
    center = parameters['center']
    local_center = lambda point: translated(center, rotate(rotation, point))
    records = [box_record('ground', [40.0, 40.0, 0.2], [0.0, 0.0, -0.1], 0.0)]
    for role, sign in [('lower', -1), ('upper', 1)]:
        records.append(box_record(role, [length, width, thickness], local_center([0, 0, sign * (gap + thickness) / 2]), angle))
    if parameters['scene'] == 'shelf':
        for role, sign in [('left', -1), ('right', 1)]:
            records.append(box_record(role, [length, thickness, gap + 2 * thickness],
                                      local_center([0, sign * (width + thickness) / 2, 0]), angle))
        records.append(box_record('back', [thickness, width + 2 * thickness, gap + 2 * thickness],
                                  local_center([(length + thickness) / 2, 0, 0]), angle))
    for record in records[1:]:
        for vertex in record['gazebo']['vertices_m']:
            if vertex[2] <= 0:
                raise ValueError('A non-ground solid intersects the ground; raise the scene center')
            if abs(vertex[0]) >= 20 or abs(vertex[1]) >= 20:
                raise ValueError('Scene exceeds the finite ground footprint')
    targets = []
    for index, (depth, lateral, delta) in enumerate(itertools.product(
            parameters['depths'], parameters['lateral'], parameters['orientation_deg'])):
        point = local_center([-length / 2 + depth, lateral, -gap / 2 + parameters['tool_offset']])
        if point[2] <= 0:
            raise ValueError('Target is below ground')
        for record in records:
            inverse = list(zip(*record['gazebo']['rotation']))
            relative = [value - base for value, base in zip(point, record['gazebo']['center_m'])]
            local = rotate(inverse, relative)
            if all(abs(value) <= size / 2 for value, size in zip(local, record['size_m'])):
                raise ValueError('Target lies inside a collision solid')
        tool_quaternion = quaternion_product(pitch_quaternion(angle + math.radians(delta)), [1.0, 0.0, 0.0, 0.0])
        targets.append({'id': 'target_{:03d}'.format(index), 'depth_m': depth, 'lateral_m': lateral,
                        'orientation_delta_deg': delta,
                        'gazebo': {'position_m': point, 'quat_xyzw': tool_quaternion},
                        'planner': {'position_m': rotate(TRANSFORM, point),
                                    'quat_xyzw': quaternion_product([0, 0, math.sqrt(0.5), math.sqrt(0.5)], tool_quaternion)},
                        'position_tolerance_m': 0.005, 'orientation_tolerance_rad': math.radians(1),
                        'type': 'PRECONTACT_NOT_EXECUTED', 'planner_3r_tool_mapping': 'UNVERIFIED'})
    return records, targets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scene', choices=['solar', 'shelf'], required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--beta-deg', type=float, default=20.0)
    parser.add_argument('--clearance', type=float, default=0.8)
    parser.add_argument('--width', type=float, default=1.2)
    parser.add_argument('--length', type=float, default=2.4)
    parser.add_argument('--thickness', type=float, default=0.08)
    parser.add_argument('--center', type=float, nargs=3, default=[3.0, 0.0, 2.2])
    parser.add_argument('--depths', type=float, nargs='+', default=[0.4, 1.2, 2.0])
    parser.add_argument('--lateral', type=float, nargs='+', default=[-0.2, 0.0, 0.2])
    parser.add_argument('--orientation-deg', type=float, nargs='+', default=[-10.0, 0.0, 10.0])
    parser.add_argument('--tool-offset', type=float, default=0.08)
    arguments = parser.parse_args()
    parameters = vars(arguments).copy()
    output = parameters.pop('output')
    records, targets = generate(parameters)
    output.mkdir(parents=True, exist_ok=False)
    files = {'benchmark.world': make_world(arguments.scene, records)}
    documents = {
        'parameters.json': parameters,
        'obstacles.json': {'schema': 'p54_obb_v1', 'transform_planner_from_gazebo': TRANSFORM,
                           'collision_contract': 'BOTTOM_ORIGIN_CENTER_OFFSET_LZ_OVER_2', 'obstacles': records},
        'targets.json': {'schema': 'p54_targets_v1', 'tool_frame': 'x=tangent_u,y=-v,z=-normal_at_zero_delta',
                         'targets': targets},
    }
    for filename, document in documents.items():
        files[filename] = (json.dumps(document, indent=2, allow_nan=False) + '\n').encode()
    for filename, content in files.items():
        with (output / filename).open('xb') as stream:
            stream.write(content)
    manifest = {'schema': 'p54_bundle_v1', 'generator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'files_sha256': {name: hashlib.sha256(content).hexdigest() for name, content in files.items()},
                'safety_status': 'ENVIRONMENT_GEOMETRY_ONLY_NO_ROBOT_NO_EXECUTION',
                'methods_evaluated': [], 'target_count': len(targets)}
    with (output / 'manifest.json').open('x') as stream:
        json.dump(manifest, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'output': str(output), 'obstacles': len(records), 'targets': len(targets)}))


if __name__ == '__main__':
    main()

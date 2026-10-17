#!/usr/bin/env python3
"""Bounded, private-master Gazebo load check of environment-only P54 bundles."""
import argparse
import datetime
import hashlib
import json
import math
import os
import re
import signal
import socket
import subprocess
import threading
import time
import xml.etree.ElementTree as ET
from pathlib import Path

from validate_bundle import validate
from verify_runtime_capture import verify_runtime


def bounded_log(pipe, path, counters):
    limit = 512 * 1024
    with path.open('xb') as stream:
        while True:
            block = pipe.read(4096)
            if not block:
                break
            remaining = max(0, limit - counters['saved_bytes'])
            stream.write(block[:remaining])
            counters['saved_bytes'] += min(len(block), remaining)
            counters['discarded_bytes'] += max(0, len(block) - remaining)


def command(arguments, environment, deadline):
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError('World load-check deadline exceeded')
    result = subprocess.run(arguments, env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            timeout=min(4.0, remaining), text=True)
    if len(result.stdout) + len(result.stderr) > 512 * 1024:
        raise ValueError('Unexpectedly large Gazebo query output')
    if result.returncode:
        raise RuntimeError('Gazebo query failed: ' + ' '.join(arguments) + '\n' + result.stderr)
    if '[Err]' in result.stderr or 'Error [' in result.stderr:
        raise RuntimeError('Gazebo reported an error: ' + result.stderr)
    return result.stdout


def check(bundle, directory, seconds):
    geometry = validate(bundle)
    world = ET.parse(bundle / 'benchmark.world').getroot().find('world').get('name')
    obstacles = json.loads((bundle / 'obstacles.json').read_text())['obstacles']
    directory.mkdir(parents=True, exist_ok=False)
    home = directory / 'home'
    home.mkdir()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(('127.0.0.1', 0))
        port = probe.getsockname()[1]
    environment = os.environ.copy()
    for name in ['DISPLAY', 'WAYLAND_DISPLAY', 'ROS_MASTER_URI', 'ROS_NAMESPACE']:
        environment.pop(name, None)
    environment.update({'HOME': str(home.resolve()), 'GAZEBO_MASTER_URI': 'http://127.0.0.1:' + str(port),
                        'GAZEBO_IP': '127.0.0.1',
                        'GAZEBO_MODEL_DATABASE_URI': '', 'GAZEBO_MODEL_PATH': '', 'GAZEBO_PLUGIN_PATH': '',
                        'GAZEBO_LOG_PATH': str((directory / 'gazebo_logs').resolve())})
    result = {'bundle': str(bundle), 'world': world, 'private_master_uri': environment['GAZEBO_MASTER_URI'],
              'budget_seconds': seconds, 'geometry': geometry, 'models': [], 'robot_loaded': False,
              'ros_started': False, 'sitl_started': False, 'execution': 'NOT_RUN', 'passed': False,
              'start_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'tool_source_sha256': {name: hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest()
                                      for name in ['check_load.py', 'validate_bundle.py', 'verify_runtime_capture.py']}}
    counters = {'saved_bytes': 0, 'discarded_bytes': 0}
    start = time.monotonic()
    deadline = start + seconds
    server = None
    writer = None
    try:
        schema = command(['gz', 'sdf', '-k', str(bundle / 'benchmark.world')], environment, deadline)
        (directory / 'sdf_check.txt').write_text(schema)
        if schema.strip() != 'Check complete':
            raise ValueError('SDF validator did not confirm validity')
        server = subprocess.Popen(['gzserver', '--verbose', '--pause', str(bundle / 'benchmark.world')],
                                  env=environment, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, start_new_session=True)
        result['server_pid'] = server.pid
        result['owned_process_group'] = server.pid
        writer = threading.Thread(target=bounded_log, args=(server.stdout, directory / 'gzserver.log', counters), daemon=True)
        writer.start()
        ready = False
        last_error = None
        while time.monotonic() < deadline - 5:
            if server.poll() is not None:
                raise RuntimeError('gzserver exited during startup: ' + str(server.returncode))
            try:
                topics = command(['gz', 'topic', '-l'], environment, deadline)
                if '/gazebo/' + world + '/world_stats' in topics:
                    (directory / 'topics.txt').write_text(topics)
                    ready = True
                    break
            except (RuntimeError, subprocess.TimeoutExpired) as error:
                last_error = str(error)
            time.sleep(0.2)
        if not ready:
            raise TimeoutError('No world_stats topic before deadline: ' + str(last_error))
        number = r'([-+0-9.eE]+)'
        box_pattern = r'box\s*\{\s*size\s*\{\s*x:\s*' + number + r'\s*y:\s*' + number + r'\s*z:\s*' + number
        for index, record in enumerate(obstacles):
            information = command(['gz', 'model', '-w', world, '-m', record['name'], '-i'], environment, deadline)
            (directory / ('model_{:02d}.txt'.format(index))).write_text(information)
            sizes = [[float(value) for value in match] for match in re.findall(box_pattern, information)]
            if not sizes or not all(all(abs(actual - expected) < 1e-10 for actual, expected in zip(size, record['size_m'])) for size in sizes):
                raise ValueError('Runtime box dimensions missing/inconsistent: ' + record['name'])
            collision_count = len(re.findall(r'\bcollision\s*\{', information))
            if collision_count != 1:
                raise ValueError('Expected exactly one loaded collision for ' + record['name'])
            actual_pose = command(['gz', 'model', '-w', world, '-m', record['name'], '-p'], environment, deadline)
            values = [float(value) for value in actual_pose.split()]
            expected_pose = record['gazebo']['origin_m'] + record['gazebo']['rpy_rad']
            if len(values) != 6 or not all(math.isclose(actual, expected, abs_tol=2e-5) for actual, expected in zip(values, expected_pose)):
                raise ValueError('Runtime pose mismatch: ' + record['name'])
            result['models'].append({'name': record['name'], 'loaded_collision_count': collision_count,
                                     'box_sizes_m': sizes, 'pose_rpy': values})
        if server.poll() is not None:
            raise RuntimeError('gzserver did not remain alive through queries')
        result['runtime_geometry'] = verify_runtime(bundle, directory)
        result['passed'] = True
    except Exception as error:
        result['error'] = type(error).__name__ + ': ' + str(error)
    finally:
        if server is not None:
            try:
                os.killpg(server.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(server.pid, signal.SIGKILL)
                server.wait(timeout=3)
            if writer is not None:
                writer.join(timeout=3)
            result['server_returncode_after_scoped_cleanup'] = server.returncode
        result['wall_seconds'] = time.monotonic() - start
        result['log_bytes'] = counters
        with (directory / 'result.json').open('x') as stream:
            json.dump(result, stream, indent=2)
            stream.write('\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, nargs='+', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--seconds', type=int, default=40)
    arguments = parser.parse_args()
    if not 10 <= arguments.seconds <= 60:
        parser.error('Each world budget must be within [10,60] seconds')
    arguments.output.mkdir(parents=True, exist_ok=False)
    results = [check(bundle.resolve(), arguments.output / str(index), arguments.seconds)
               for index, bundle in enumerate(arguments.bundle)]
    with (arguments.output / 'summary.json').open('x') as stream:
        json.dump(results, stream, indent=2)
        stream.write('\n')
    print(json.dumps([{'world': item['world'], 'passed': item['passed'], 'error': item.get('error')} for item in results]))
    if not all(item['passed'] for item in results):
        raise SystemExit(1)


if __name__ == '__main__':
    main()

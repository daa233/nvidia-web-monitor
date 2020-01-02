import os
import yaml
import subprocess
import datetime
from collections import namedtuple
from multiprocessing import Pool

from flask import Flask
from flask import render_template

app = Flask(__name__)


CONFIG_FILE = 'config.yaml'


@app.route('/')
def show():
    log('Configuring...')
    display_query_gpu_options, query_gpu_cmd_list, valid_gpu_attr_list, host_list = \
        get_config(CONFIG_FILE)
    log('Start querying...')
    gpu_info_list = multiprocess_query_cmds(query_gpu_cmd_list)
    log('Info got! Start parsing...')
    if len(gpu_info_list) == 0:
        log('No GPU found')
        return render_template('404.html') 
    all_server_item_list = []
    for host, gpu_info in zip(host_list, gpu_info_list):
        if not gpu_info:
            host['comment'] = '(ssh error)'
        elif 'NVIDIA-SMI has failed' in gpu_info[0]:
            host['comment'] = '(nvidia-smi has failed)'
        else:
            host['comment'] = ' '
        gpu_item_list = parse_gpu_info(gpu_info, valid_gpu_attr_list)
        all_server_item_list.append({'host': host, 'gpu': gpu_item_list})
    log('Parsing finished! Rendering...')
    return render_template('main.html',
                           all_server_item_list=all_server_item_list,
                           gpu_attrs=valid_gpu_attr_list,
                           header_items=display_query_gpu_options)


def get_config(config_file):
    with open(config_file, 'r') as stream:
        config = yaml.load(stream)
    
    query_gpu_options = config['QUERY_GPU_OPTIONS']
    query_gpu_cmd = config['QUERY_GPU_CMD'] + '=' + ','.join(query_gpu_options) + ' --format=csv' 

    display_query_gpu_options = config['DISPLAY_QUERY_GPU_OPTIONS']
    valid_gpu_attr_list = [i.replace('.', '_') for i in query_gpu_options]
    
    assert len(display_query_gpu_options) == len(query_gpu_options) == len(valid_gpu_attr_list)
    
    query_gpu_cmd_list = []
    host_list = []
    if config['REMOTE_HOST']:
        host_list += config['HOST']
        for host in host_list:
            cmd = ' '.join(['ssh', '-oBatchMode=yes', host['username']+'@'+host['ip'], query_gpu_cmd])
            query_gpu_cmd_list.append(cmd)
    if config['LOCAL_HOST']:
        query_gpu_cmd_list.insert(0, query_gpu_cmd)
        host_list.insert(0, {'ip': 'localhost'})
    
    return display_query_gpu_options, query_gpu_cmd_list, valid_gpu_attr_list, host_list


def query_info(cmd):
    # info_proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    fd = os.popen(cmd)
    info_proc = fd.readlines()
    fd.close()
    return info_proc


def multiprocess_query_cmds(cmd_list):
    info_list = []

    if len(cmd_list) == 0:
        return info_list

    # info_proc_list = [query_info(cmd) for cmd in cmd_list]
    with Pool(processes=10) as pool:
        info_list = pool.map(query_info, cmd_list, chunksize=1)
    # info_list = [info_proc.stdout.decode('utf-8').split('\n') for info_proc in info_proc_list]
    for info in info_list:
        if '' in info:
            info.remove('')
    return info_list


def parse_gpu_info(info, valid_gpu_attr_list):
    gpu_item_list = []
    for info_str in info[1:]:
        # str.split returns a list
        value_list = [i.strip() for i in info_str.split(', ')]
        if value_list == ['']:
            # nvidia-smi has failed
            value_list = ['-'] * len(valid_gpu_attr_list)
        assert len(value_list) == len(valid_gpu_attr_list)
        GPU = namedtuple('GPU', valid_gpu_attr_list)
        gpu_item = GPU(*value_list)
        gpu_item_list.append(gpu_item)
    return gpu_item_list


def log(msg):
    print(datetime.datetime.now(), '\t'+msg)


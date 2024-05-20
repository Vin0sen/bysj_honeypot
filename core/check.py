# author: cslin
# date  : 2024-04-18

import os
import importlib
import elasticsearch
import subprocess
from shutil import which
import logging
import json
from config import api_configuration


def load_requirements():
    """Load and return all required modules from requirements.txt."""
    requirements_path = os.path.join(os.getcwd(), 'requirements.txt')
    with open(requirements_path, 'r') as file:
        return file.read().strip().split('\n')


def check_python_packages(required_modules):
    """Check if all required Python packages are installed."""
    for module in required_modules:
        try:
            module_name = module.split(':')[1] if ':' in module else module.split('==')[0]
            # print(module_name)
            importlib.import_module(module_name)
        except ImportError as e:
            logging.error(f"Module {module} not installed. Please run: pip3 install {module}")
            return False
    return True


def check_elasticsearch(api_config):
    """Check if Elasticsearch can be accessed."""
    try:
        connection = elasticsearch.Elasticsearch(
            api_config["api_database"],
            http_auth=api_config["api_database"]
        )
        connection.indices.get_alias("*")
    except Exception as e:
        logging.error("Elasticsearch connection failed: " + str(e))
        return False
    return True


def check_external_commands(commands):
    """Check availability of external system commands."""
    missing_commands = {cmd: which(cmd) for cmd in commands if not which(cmd)}
    if missing_commands:
        logging.error("Missing tools: " + json.dumps(missing_commands, indent=4))
        return False
    return True


def check_for_requirements(start_api_server):
    # Load and check required Python packages
    required_modules = load_requirements()
    if not check_python_packages(required_modules):
        return False

    # Load configuration and messages (assuming these functions exist)
    api_config = api_configuration()

    # Elasticsearch check
    if not check_elasticsearch(api_config):
        return False

    # Additional checks based on the mode
    if not start_api_server:
        # Check Docker and system commands
        if not subprocess.check_output(["docker", "--help"], stderr=subprocess.PIPE):
            return False

        commands = ['tshark', 'ps', 'grep', 'kill']
        if not check_external_commands(commands):
            return False

    logging.info("All checks passed.")
    return True


"""
# The code below is in compatible.py before.
def check_for_requirements(start_api_server):
# check if requirements exist
# Returns: True if exist otherwise False

# TODO : Fix the cyclic dependency later
from config import api_configuration
from core.messages import load_messages
messages = load_messages().message_contents
# check external required modules
api_config = api_configuration()
external_modules = open(os.path.join(os.getcwd(), 'requirements.txt'), 'r').read().split('\n')
for module_name in external_modules:
    try:
        __import__(
            module_name.split('==')[0] if 'library_name=' not in module_name
            else module_name.split('library_name=')[1].split()[0]
        )
    except Exception:
        exit_failure(
            "pip3 install -r requirements.txt ---> " + module_name + " not installed!"
        )
# check elasticsearch
try:
    connection = elasticsearch.Elasticsearch(
        api_config["api_database"],
        http_auth=api_config["api_database"]
    )
    connection.indices.get_alias("*")
except Exception:
    exit_failure(messages["elasticsearch_not_found"])
# check if its honeypot server not api server
if not start_api_server:
    # check docker
    try:
        subprocess.check_output(["docker", "--help"],
                                stderr=subprocess.PIPE)
    except Exception:
        exit_failure(messages["cannot_communicate_with_docker"])
    # check for commandline requirements
    commands = {
        'tshark': which('tshark'),
        'ps': which('ps'),
        'grep': which('grep'),
        'kill': which('kill')
    }
    for command in commands:
        if commands[command] is None:
            exit_failure(
                messages["install_tools"] + "{0}".format(json.dumps(commands, indent=4))
            )
return True
"""
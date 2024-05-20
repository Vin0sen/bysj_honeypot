#!/usr/bin/env python
# -*- coding: utf-8 -*-

import docker
import os, json
from core.alert import info
from core.get_modules import (virtual_machine_name_to_container_name,
                              virtual_machine_names_to_container_names)
from core.compatible import (copy_dir_tree, is_verbose_mode, make_tmp_thread_dir, mkdir)
from core.messages import load_messages

messages = load_messages().message_contents

def get_image_name_of_selected_modules(configuration):
    """
    get list of image name using user final configuration
    Returns:
        list of virtual machine image name
    """
    return virtual_machine_names_to_container_names(configuration)


class DockerProcess():
    def __init__(self):
        self.client = docker.from_env()          

    def get_honeypot_images(self, pattern="ohp"):
        # for image in images:
        #     for tag in image.tags:
        #         if tag.startswith("ohp"):
        #             print(tag)
        try:
            all_images = self.client.images.list()
            return [image for image in all_images if any(tag.startswith(pattern) for tag in image.tags)]
        except docker.errors.APIError as e:
            print(f"Error retrieving Docker images: {e}")
            return []
        
    def get_honeypot_containers(self, pattern="ohp"):
        try:
            all_running_containers = self.client.containers.list()  # docker ps, all=False(default)
            return [container for container in all_running_containers if container.name.startswith(pattern)]
        except docker.errors.APIError as e:
            print(f"Error retrieving Docker containers: {e}")
            return []

    def count_docker_images(self, pattern="ohp"):
        # total honeypot images
        return len(self.get_honeypot_images()) 

    def count_docker_containers(self, pattern="ohp"):
        # total running honeypot containers 
        return len(self.get_honeypot_containers())

    def stop_all_containers(self):
        containers = self.get_honeypot_containers()
        for container in containers:
            container.stop()
            print(f"stopping {container.name}")

    def create_ohp_networks(self):
        """
        Create Docker networks for OWASP Honeypot with specific configurations.
        Returns:
            bool: True if networks were created or already exist, False if an error occurred.
        """
        networks = self.client.networks.list()  
        existing_networks = [network.name for network in networks]
        
        try:
            # Create ohp_internet network if it does not exist
            if "ohp_internet" not in existing_networks:
                info("creating ohp_internet network")
                self.client.networks.create(
                    name="ohp_internet",
                    driver="bridge",
                    options={
                        "com.docker.network.bridge.enable_icc": "true",
                        "com.docker.network.bridge.enable_ip_masquerade": "true",
                        "com.docker.network.bridge.host_binding_ipv4": "0.0.0.0",
                        "com.docker.network.driver.mtu": "1500"
                    }
                )
                network_json = json.loads(os.popen("docker network inspect ohp_internet").read())[
            0]["IPAM"]["Config"][0]
                info(f"ohp_internet network created subnet:{network_json['Subnet']} gateway:{network_json['Gateway']}")

            # Create ohp_no_internet network if it does not exist
            if "ohp_no_internet" not in existing_networks:
                info("creating ohp_no_internet network")
                self.client.networks.create(
                    name="ohp_no_internet",
                    driver="bridge",
                    internal=True,
                    attachable=True,
                    options={
                        "com.docker.network.bridge.enable_icc": "true",
                        "com.docker.network.bridge.enable_ip_masquerade": "true",
                        "com.docker.network.bridge.host_binding_ipv4": "0.0.0.0",
                        "com.docker.network.driver.mtu": "1500"
                    }
                )
                network_json = json.loads(os.popen("docker network inspect ohp_no_internet").read())[
                    0]["IPAM"]["Config"][0]
                info(f"ohp_no_internet network created subnet:{network_json['Subnet']} gateway:{network_json['Gateway']}")
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    def docker_rm_container(self):
        pass
    def docker_rm_image(self):
        pass
    

def running_containers():
    """
    list of running containers
    Returns:
        an array with list of running containers name
    """
    return [container.rsplit()[-1] for container in
            os.popen("docker ps").read().rsplit("\n")[1:-1]]

def all_existing_containers():
    """
    list of all existing containers
    Returns:
        an array with list of all existing containers name
    """
    return [container.rsplit()[-1] for container in
            os.popen("docker ps -a").read().rsplit("\n")[1:-1]]


def all_existing_images():
    """
    list of all existing images
    example: ['ohp_sshserver_weak_password', 'ohp_httpserver_basic_auth_weak_password']
    """
    return [
        container.rsplit()[0] for container in
        os.popen("docker images").read().rsplit("\n")[1:-1]
    ]

def remove_old_containers(configuration):
    # remove old containers based on images

    containers_list = all_existing_containers()
    for container in virtual_machine_names_to_container_names(configuration):
        if container in containers_list:
            info(
                "removing container {0}".format(
                    os.popen(
                        "docker rm {0}".format(container)
                    ).read().rsplit()[0]
                )
            )
    return True


def remove_old_images(configuration):
    # remove old images based on user configuration
    existing_images = set(all_existing_images())
    images_to_remove = set(get_image_name_of_selected_modules(configuration))
    images_to_remove = existing_images.intersection(images_to_remove)

    for image in images_to_remove:
        info(messages["removing_image"].format(image))
        os.popen("docker rmi {0}".format(image)).read()
    return True

def start_containers(configuration):
    """
    start containers based on configuration and dockerfile

    Args:
        configuration: JSON container configuration

    Returns:
        configuration containing IP Addresses
    """
    for selected_module in configuration:
        # get the container name to start (organizing)
        # using pattern name will help us to remove/modify the images and modules
        container_name = virtual_machine_name_to_container_name(
            configuration[selected_module]["virtual_machine_name"],
            selected_module
        )
        configuration[selected_module]['container_name'] = container_name
        real_machine_port = configuration[selected_module]["real_machine_port_number"]
        virtual_machine_port = configuration[selected_module]["virtual_machine_port_number"]
        # connect to owasp honeypot networks!
        # run the container with internet access
        os.popen(
            "docker run {0} --net {4} --name={1} -d -t -p {2}:{3} {1}".format(
                " ".join(
                    configuration[selected_module]["extra_docker_options"]
                ),
                container_name,
                real_machine_port,
                virtual_machine_port,
                'ohp_internet' if configuration[selected_module]["virtual_machine_internet_access"]
                else 'ohp_no_internet'
            )
        ).read()
        try:
            virtual_machine_ip_address = os.popen(
                "docker inspect -f '{{{{range.NetworkSettings.Networks}}}}"
                "{{{{.IPAddress}}}}{{{{end}}}}' {0}".format(
                    container_name
                )
            ).read().rsplit()[0].replace("\'", "")  # single quotes needs to be removed in windows
        except Exception:
            virtual_machine_ip_address = "CANNOT_FIND_IP_ADDRESS"
        # add virtual machine IP Address to configuration
        configuration[selected_module]["ip_address"] = virtual_machine_ip_address
        # print started container information
        info(
            "container {0} started, forwarding 0.0.0.0:{1} to {2}:{3}".format(
                container_name,
                real_machine_port,
                virtual_machine_ip_address,
                virtual_machine_port
            )
        )
    return configuration


def create_new_images(configuration):
    # start new images based on configuration and dockerfile
    from core.load import tmp_directories

    for selected_module in configuration:
        image_name = virtual_machine_name_to_container_name(
            configuration[selected_module]["virtual_machine_name"],
            selected_module
        )
        if image_name in all_existing_images():
            continue
        # go to tmp folder to create Dockerfile and files dir
        tmp_dir_name = make_tmp_thread_dir()
        os.chdir(tmp_dir_name)  # tmp/thread_saGK78HhJ3fk6BN/files
        mkdir("files")

        # create Dockerfile
        dockerfile = open("Dockerfile", "w")
        dockerfile.write(configuration[selected_module]["dockerfile"])
        dockerfile.close()

        # copy files
        copy_dir_tree(configuration[selected_module]["files"], "files")

        info(messages["creating_image"].format(image_name))

        # in case if verbose mode is enabled, we will be use os.system
        # instead of os.popen to show the outputs in case
        # of anyone want to be aware what's happening or what's the error,
        # it's a good feature for developers as well to create new modules
        if is_verbose_mode():
            os.system(f"docker build . -t {image_name}")
        else:
            os.popen(f"docker build . -t {image_name}").read()

        # created
        info(messages["image_created"].format(image_name))

        # go back to home directory
        os.chdir("../..")

        # submit tmp dir name
        tmp_directories.append(tmp_dir_name)
    return True


if __name__ == '__main__':
    dp = DockerProcess()
    # print(dp.count_docker_containers(),
    # dp.count_docker_images())
    while True:
        if input()=="0":
            print(dp.count_docker_containers(), dp.count_docker_images())
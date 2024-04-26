#!/usr/bin/env python3

import subprocess
import sys
import os
import re
import requests
import json
import zipfile
from io import BytesIO

def check_and_prompt_package_installation():
    try:
        import requests
    except ImportError:
        print("The required Python package 'requests' is not installed.")
        print("Please install it using your system's package manager. For example:")
        print("sudo apt install python3-requests")
        sys.exit(1)

ENV_TO_CHAIN_ID = {
    "local": None,
    "devnet": "arctic-1",
    "testnet": "atlantic-2"
}

def print_ascii_and_intro():
    print("""
                     ..:=++****++=:.
                  .:+*##############*+:.
                .=*#####+:....:+#######+.
              .-*#####=.  ....  .+###*:. ...
            ..+#####=.. .=####=.  .... .-*#=.
            .+#####+. .=########+:...:=*####=.
            =########*#######################-
           .#################=:...=###########.
           ...  ..-*######+..      .:*########:
            ..=-.   -###-    -####.   :+######:
           :#####+:       .=########:   .+####:
           .########+:.:=#############=-######.
            =################################-
            .+#####*-.. ..-########+.. ..-*#=.
            ..+##*-. ..... .-*###-. ...... ..
              .--. .:*###*:.  ...  .+###*-.
                 .:+#######*-:..::*#####=.
                  .-+###############*+:.
                     ..-+********+-.

Welcome to the Sei node installer!
For more information please visit docs.sei.io
Please make sure you have the following installed locally:
\t- golang 1.21 (with PATH and GOPATH set properly)
\t- make
\t- gcc
\t- docker
This tool will build from scratch seid and wipe away existing state.
Please backup any important existing data before proceeding.
""")

def install_latest_release():
    try:
        response = requests.get("https://api.github.com/repos/sei-protocol/sei-chain/releases/latest")
        response.raise_for_status()
        latest_version = response.json()["tag_name"]
        zip_url = f"https://github.com/sei-protocol/sei-chain/archive/refs/tags/{latest_version}.zip"
        download_and_unzip(zip_url)
    except requests.exceptions.RequestException as e:
        print(f"Failed to download or parse release data: {e}")
        sys.exit(1)

def download_and_unzip(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with zipfile.ZipFile(BytesIO(response.content)) as z:
            z.extractall(".")
            os.chdir(z.namelist()[0])
        run_command("make install")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading the zip file: {e}")
        sys.exit(1)
    except zipfile.BadZipFile:
        print("Downloaded file is not a zip file.")
        sys.exit(1)
def get_rpc_server(chain_id):
    chains_json_url = "https://raw.githubusercontent.com/sei-protocol/chain-registry/main/chains.json"
    response = requests.get(chains_json_url)
    chains = response.json()
    rpcs = []
    for chain in chains:
        if chains[chain]['chainId'] == chain_id:
            rpcs = chains[chain]['rpc']
            break
    for rpc in rpcs:
        try:
            response = requests.get(rpc['url'])
            if response.status_code == 200:
                return rpc['url']
        except Exception:
            pass
    return None

def take_manual_inputs():
    print(
        """Please choose an environment:
        1. local
        2. devnet (arctic-1)
        3. testnet (atlantic-2)"""
    )
    choice = input("Enter choice: ")
    while choice not in ['1', '2', '3']:
        print("Invalid input. Please enter '1', '2' or '3'.")
        choice = input("Enter choice: ")
    env = ""
    if choice == "1":
        env = "local"
    elif choice == "2":
        env = "devnet"
    elif choice == "3":
        env = "testnet"

    print("Please choose the database backend to use for state commit:")
    print("1. sei-db")
    print("2. legacy (default)")
    db_choice = input("Enter choice (default is 2): ").strip() or "2"
    return env, db_choice

def get_state_sync_params(rpc_url):
    trust_height_delta = 40000
    response = requests.get(f"{rpc_url}/status")
    latest_height = int(response.json()['sync_info']['latest_block_height'])
    sync_block_height = latest_height - trust_height_delta if latest_height > trust_height_delta else latest_height
    response = requests.get(f"{rpc_url}/block?height={sync_block_height}")
    sync_block_hash = response.json()['block_id']['hash']
    return sync_block_height, sync_block_hash

def get_persistent_peers(rpc_url):
    with open(os.path.expanduser('~/.sei/config/node_key.json'), 'r') as f:
        self_id = json.load(f)['id']
        response = requests.get(f"{rpc_url}/net_info")
        peers = [peer['url'].replace('mconn://', '') for peer in response.json()['peers'] if peer['node_id'] != self_id]
        persistent_peers = ','.join(peers)
        return persistent_peers

def get_genesis_file(chain_id):
    genesis_url = f"https://raw.githubusercontent.com/sei-protocol/testnet/main/{chain_id}/genesis.json"
    response = requests.get(genesis_url)
    return response

def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command '{command}' failed with error code {e.returncode}. Error output: {e.output}")
        handle_specific_errors(e)

def handle_specific_errors(error):
    if error.returncode == 1:  # Example specific error code
        print("Handling specific error scenario...")
        # Implement retry logic, if appropriate
        # Or log more details, or even ignore under certain conditions
    else:
        print("Unhandled error, stopping execution.")
        sys.exit(1)

def main():
    print_ascii_and_intro()
    env, db_choice = take_manual_inputs()
    moniker = "demo"
    print(f"Setting up a node in {env}")
    chain_id = ENV_TO_CHAIN_ID[env]
    install_latest_release()
    if env == "local":
        run_command("chmod +x scripts/initialize_local_chain.sh")
        run_command("scripts/initialize_local_chain.sh")

    rpc_url = get_rpc_server(chain_id)
    run_command("rm -rf $HOME/.sei")
    run_command(f"seid init --chain-id {chain_id} {moniker}")
    sync_block_height, sync_block_hash = get_state_sync_params(rpc_url)
    persistent_peers = get_persistent_peers(rpc_url)
    genesis_file = get_genesis_file(chain_id)

    # Config file handling
    config_path = os.path.expanduser('~/.sei/config/config.toml')
    app_config_path = os.path.expanduser('~/.sei/config/app.toml')
    genesis_path = os.path.join(os.path.dirname(config_path), 'genesis.json')
    with open(genesis_path, 'wb') as f:
        f.write(genesis_file.content)

    with open(config_path, 'r') as file:
        config_data = file.read()
    with open(app_config_path, 'r') as file:
        app_config_data = file.read()

    # Config.toml edits
    config_data = config_data.replace('rpc-servers = ""', f'rpc-servers = "{rpc_url},{rpc_url}"')
    config_data = config_data.replace('trust-height = 0', f'trust-height = {sync_block_height}')
    config_data = config_data.replace('trust-hash = ""', f'trust-hash = "{sync_block_hash}"')
    config_data = config_data.replace('persistent-peers = ""', f'persistent-peers = "{persistent_peers}"')
    config_data = config_data.replace('enable = false', 'enable = true')
    config_data = config_data.replace('db-sync-enable = true', 'db-sync-enable = false')
    config_data = config_data.replace('use-p2p = false', 'use-p2p = true')
    with open(config_path, 'w') as file:
        file.write(config_data)

    # App.toml edits for 'sc-enable' and 'enabled' under specific conditions
    if db_choice == "1":
        app_config_data = re.sub(
            r"(sc-enable = ).*",
            r"\1true",
            app_config_data
        )
    app_config_data = re.sub(
        r"(# other sinks such as Prometheus.\nenabled = ).*",
        r"\1false",
        app_config_data
    )
    with open(app_config_path, 'w') as file:
        file.write(app_config_data)

    print("Starting seid...")
    run_command("seid start")

if __name__ == "__main__":
    main()

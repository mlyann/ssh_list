"""
Parse the .ssh/config file, connect to a server.

Author:
Minglai Yang
"""
import subprocess
import re
import os

def select_a_server(servers):
  if servers == []:
    print("No servers found. Showing all servers.")
    servers = read_ssh_config()
    print(f"{len(servers)} servers reloaded.")

  servers = sorted(servers, key=lambda x: x[0])

  print("\n  Select a server to connect to:")
  for i, server in enumerate(servers):
    if i == 0:
      print(f"   [1] {server[0]}")
    else:
      print(f"    {i+1}. {server[0]}")
  print("    0. Exit")
  print("    A. Show server info")
  selected_server = input("\n> ")

  if selected_server in ["A", "a"]:
    print("\n  Select a server to connect to:")
    for i, server in enumerate(servers):
      if i == 0:
        print(f"   [1] {server[0]}: {server[1]}")
      else:
        print(f"    {i+1}. {server[0]}: {server[1]}")
    print("    0. Exit")
    selected_server = input("\n> ")

  if selected_server != "0":
    if selected_server == "":
      selected_server = 1
    try:
      selected_server = servers[int(selected_server) - 1]
      connect_to_server(selected_server)
    except:
      select_a_server(fuzzyfinder(selected_server, servers))

def fuzzyfinder(user_input, servers):
  # modified from https://blog.amjith.com/fuzzyfinder-in-10-lines-of-python
  user_input = user_input.split(" ")
  if len(user_input) > 1:
    suggestions = servers
    for word in user_input:
      suggestions = fuzzyfinder(word, suggestions)
    return suggestions

  else:
    suggestions = []
    pattern = '.*?'.join(user_input[0])   # Converts 'djm' to 'd.*?j.*?m'
    regex = re.compile(pattern)  # Compiles a regex.
    for server in servers:
      match = regex.search(server[0].lower())   # Checks if the current server matches the regex.
      if match:
        suggestions.append((len(match.group()), match.start(), server))
    return [x for _, _, x in sorted(suggestions)]

def store_new_server():
  print("\nWhat will we call this server? (Use the format: Client-ServerName)")
  host = input("Host: ").replace(" ", "")
  print("\nEnter the user and hostname together.")
  user_hostname = input("\nUser@HostName: ").strip().split("@")

  # if user_hostname.count("@") != 1:
  if len(user_hostname) != 2:
    print("Invalid input. Should have one @ symbol.")
  else:
    info_to_add = (f"\nHost {host}\n"
      f"    User {user_hostname[0]}\n"
      f"    HostName {user_hostname[1]}\n")
    print("The following entry will be added to the .ssh/config file:\n",
        info_to_add
      )

  print("Is this ok? (yes/no)")
  confirmation = input("> ")
  if(confirmation in ["Y", "y", "YES", "Yes", "yes"]):
    path = os.path.abspath(".ssh/config")
    try:
      with open(path, "a") as file:
        file.write(info_to_add)
      print("Added the new entry in your .ssh/config file.")
    except:
      print("Something went wrong. Does the file .ssh/config exist?")
  else:
    print("Aborting.")


def connect_to_server(server):
  print(f"Connecting to server: {server[0]}...")
  subprocess.run(f"ssh {server[1]}", shell=True)

def read_ssh_config():
  servers = list()
  path = os.path.abspath(".ssh/config")
  with open(path, "r") as file:
    lines = file.readlines()
  host = ""
  user = ""
  hostname = ""
  for line in lines:
    if line == "\n":
      server = [host, f"{user}@{hostname}"]
      servers.append(server)
      host = ""
      user = ""
      hostname = ""
    else:
      title, data = line.strip().split(" ", 1)
      if title == "Host":
        host = data
      if title == "User":
        user = data
      if title == "HostName":
        hostname = data
  server = [host, f"{user}@{hostname}"]
  servers.append(server)
  return servers

if __name__ == "__main__":
  all_servers = read_ssh_config()
  print("\n ", len(all_servers), "servers loaded from .ssh/config")
  print("  Main Menu"
        "\n    1. Show all clients"
        "\n    2. Show all servers"
        "\n    3. Add New Server"
        "\n    0. Exit"
        f"\n  or type in a search (dash to separate client-server name)"
        )
  selection = input("> ")

  if selection == "1":
    clients = dict()
    for server in all_servers:
      client, server_name = server[0].split("-", 1)
      if client in clients:
        clients[client].append(server)
      else:
        clients[client] = [server]
    print("\n  Client (no. of servers)")
    client_list = list()
    for i, client in enumerate(clients):
      client_list.append(client)
      print(f"    {i + 1}. {client} ({len(clients[client])})")
    selected_client = input("> ")

    try:
      select_a_server(clients[client_list[int(selected_client) - 1]])
    except:
      select_a_server(fuzzyfinder(selected_client, all_servers))

  elif selection == "2":
    select_a_server(all_servers)

  elif selection == "3":
    store_new_server()

  elif selection != "0":
    filtered_servers = fuzzyfinder(selection, all_servers)
    select_a_server(filtered_servers)

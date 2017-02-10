#!/usr/bin/env python
"""
This program convert Zabbix Export .xml file into Ansible hosts strings

"""
from collections import OrderedDict


# This function expects .xml file from Zabbix Export command. It searches through file and append to list only lines
# that have <name> or <ip> fields.
def parse_file(raw_file):
    new_file = []
    for line in raw_file:
        if (line.strip().find("<name>") == 0 and line.strip().find("-") != -1) or (line.strip().find("<ip>") == 0):
            new_file.append(line.strip())
    return new_file


# This function expects list from parse_file function. It deletes duplicate <name> field, which are not hostnames
# but SNMP location strings
def delete_duplicates(raw_list):
    i = 0
    cleaned_list = []
    while i < len(raw_list):
        if raw_list[i].find("<name") == 0 and raw_list[i + 1].find("<ip>") == 0:
            cleaned_list.append(raw_list[i])
            cleaned_list.append(raw_list[i + 1])
            i += 2
        else:
            i += 1
    return cleaned_list


# This function expects list without duplicates from delete_duplicates function. It erases all <name> and <ip> fields
def clean_list(dirty_list):
    tmp_list = []
    cleaned_list = []
    for item in dirty_list:
        tmp_list.append(item.split(">")[1])
    for item in tmp_list:
        cleaned_list.append(item.split("<")[0])
    return cleaned_list


# This function expects list from clean_list function.
# It creates dictionary with keys = hostname and values = ip addresses
def generate_ordered_dictionary(raw_file):
    parsed_file = parse_file(raw_file)
    cleaned_list = clean_list(delete_duplicates(parsed_file))
    keys = cleaned_list[::2]
    values = cleaned_list[1::2]
    ordered_dictionary = OrderedDict(zip(keys, values))
    return ordered_dictionary


with open("zbx_export_hosts.xml", "r") as input_file:
    my_dict = generate_ordered_dictionary(input_file)
with open("hosts_tmp.txt", "w") as output_file:
    for key in my_dict.keys():
        output_file.write(key + " ")
        output_file.write("ansible_host=" + my_dict[key] + "\n")

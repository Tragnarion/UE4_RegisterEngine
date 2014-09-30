#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
UE4 engine registration helper

Copyright Tragnarion Studios - by Moritz Wundke
"""
import os
import sys
import getopt
import argparse
import shutil
import fileinput
import traceback
import ctypes

# Python 2.7 and 3 ready
try: import _winreg as winreg
except ImportError: import winreg

__version__ = '0.1'
__author__ = 'Moritz Wundke'

# uuid used when none specified
DEFAUL_UUID = '{7F209AE1-0867-4B03-811D-243C9BAF2E74}'
KEY_TYPE = winreg.HKEY_CURRENT_USER
KEY_NAME = 'SOFTWARE\\Epic Games\\Unreal Engine\\Builds'

def show_message_box(title, message):
    """
    Show a windows message box
    """
    MessageBox = ctypes.windll.user32.MessageBoxA
    MessageBox(None, message, title, 0)

def print_error(msg):
    print("ERROR: %s" % msg)

def valid_engine_path(path):
    """
    Check if the engine path is valid
    """
    path = os.path.normcase(path)

    # Check that path is actually there
    if not os.path.exists(path):
        return False

    # Check that is has an engine folder
    if not os.path.exists(os.path.join(path,'engine')):
        return False

    # Check some specific engine folders
    if not os.path.exists(os.path.join(path,'engine','Binaries')):
        return False
    if not os.path.exists(os.path.join(path,'engine','Build')):
        return False
    if not os.path.exists(os.path.join(path,'engine','Config')):
        return False
    if not os.path.exists(os.path.join(path,'engine','Content')):
        return False

    return True

def open_key():
    """
    Open the key we will use
    """
    return winreg.CreateKeyEx(KEY_TYPE, KEY_NAME, 0, winreg.KEY_ALL_ACCESS)

def get_key_data(key, name):
    """
    Get a value of a given value_name
    """
    try:
        value, type = winreg.QueryValueEx(key, name)
        return value
    except WindowsError:
        return None

def set_key_data(key, name, data):
    """
    Set a value of a given value_name
    """
    winreg.SetValueEx(key, name, 0, winreg.REG_SZ, data)


def print_key_data(key):
    """
    Print all key data for a given key
    """
    try:
        i = 0
        while 1:
            name, value, type = winreg.EnumValue(key, i)
            print(name, value)
            i += 1
    except WindowsError:
        pass

def remove_previous_path(key, path):
    """
    Rempove any previous name value that was pointing to the given path
    """
    try:
        i = 0
        while 1:
            name, value, type = winreg.EnumValue(key, i)
            value_path = os.path.normcase(value)
            if value_path == path:
                winreg.DeleteValue(key, name)
            i += 1
    except WindowsError:
        pass

def register_engine(uuid, path, force):
    """
    Register an engine path using an uuid
    """
    if not valid_engine_path(path):
        raise RuntimeError("Engine path is not valid")

    key = open_key()

    if force:
        remove_previous_path(key, path)
    elif get_key_data(key, uuid):
        raise RuntimeError("Engine has already been registered")

    set_key_data(key, uuid, path)

    show_message_box('Done', 'Engine has been registered')

def cleanup_engines():
    """
    Cleanup any registered engine that is pointing to an invalid path
    """
    key = open_key()

    try:
        i = 0
        while 1:
            name, value, type = winreg.EnumValue(key, i)
            value_path = os.path.normcase(value)
            if not valid_engine_path(value_path):
                winreg.DeleteValue(key, name)
            i += 1
    except WindowsError:
        pass

    show_message_box('Done', 'Engine registry cleaned up!')

def main():
    parser = argparse.ArgumentParser(description='UE4 engine registration helper (%s). Tragnarion Studios - by %s' % (__version__, __author__))

    parser.add_argument('-v', '--version', action='version', version=__version__)
    parser.add_argument('-c', help='Cleanup engine registries that are not valid anymore', action="store_true")
    parser.add_argument('-f', help='Overwrite registration if path already registered', action="store_true", default=True)
    parser.add_argument('-u','--uuid', help='UUID used for registration, if not specified \'%s\' will be used or the content of uuid.txt if present.' % DEFAUL_UUID)
    parser.add_argument('-p','--path', help='Engine path, if not specified PWD will be used instead')
    args = parser.parse_args()

    try:
        if args.c:
            cleanup_engines()
        else:
            if not args.uuid:
                try:
                    with open('uuid.txt') as f:
                        args.uuid = f.readline()
                except:
                    args.uuid = DEFAUL_UUID

            if not args.path:
                args.path = os.getcwd()

            register_engine(args.uuid, os.path.normcase(args.path), args.f)
    except Exception as e:
        traceback.print_exc()
        show_message_box('Error', str(e))

if __name__ == "__main__":
    main()

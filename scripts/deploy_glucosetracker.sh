#!/bin/bash

ansible-playbook -i www.glucosetracker.net, ../ansible/production.yml --tags="deploy" --ask-vault-pass

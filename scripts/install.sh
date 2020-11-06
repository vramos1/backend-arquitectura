#!/bin/bash
pwd=$( aws ecr get-login-password --region us-east-1 )
docker container stop $(docker container ls -aq)
docker login -u arquitectura -p $pwd https://601498516328.dkr.ecr.us-east-1.amazonaws.com/arquitectura
docker pull 601498516328.dkr.ecr.us-east-1.amazonaws.com/arquitectura:latest
pip3 install boto3
python3 /home/ec2-user/chat/env_variables.py
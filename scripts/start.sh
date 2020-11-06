#!/bin/bash
pwd=$( aws ecr get-login-password --region us-east-1 )
docker login -u AWS -p $pwd https://601498516328.dkr.ecr.us-east-1.amazonaws.com/arquitectura
/usr/local/bin/docker-compose -f /home/ec2-user/chat/docker-compose.production.yml up -d
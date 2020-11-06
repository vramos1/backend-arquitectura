#!/bin/bash
pwd=$( aws ecr get-login-password )
docker container stop $(docker container ls -aq)
docker login -u AWS -p $pwd https://601498516328.dkr.ecr.us-east-1.amazonaws.com/arquitectura
docker pull 601498516328.dkr.ecr.us-east-1.amazonaws.com/arquitectura


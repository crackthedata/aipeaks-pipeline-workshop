#  This is an example for use during our workhsop, a.k.a. this is NOT optimized

# pull the latest Ubuntu image
FROM ubuntu:latest

# install some Ubuntu dependencies and security updates:
# software-properties-common = so we can install Python 3.12
# python3-pip = so we can install Python packages from Pypi
# vim = a text editor so we can edit our files
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y software-properties-common python3-pip vim

# So our terminal doesn't wait for user inputs during build
ENV DEBIAN_FRONTEND=noninteractive

# We only want the newest, coolest version of Python 
RUN add-apt-repository ppa:deadsnakes/ppa

# Let's install Python because we are cool
RUN apt-get install python3.12 -y

# Set our working directory
WORKDIR /data
COPY . /data

RUN pip install -r requirements.txt

# Set a username, requirement for Metaflow
ENV USERNAME='aipeaks'

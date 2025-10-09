# CS6410 Fall 2025 Gossip Project

This repository contains an implementation of the gossip project for CS6410.


## Setup Instructions

This repo only uses python standard library packages, so there are no dependencies aside from a modern version (>=3.10) of Python 3. 
For this reason, `build.sh` does nothing.


## Running the Program

To run the program, type the following

`chmod +x ./run.sh`

`./run.sh <HOST> <PORT>` 

where `<HOST>` is your IP address and `<PORT>` is your desired port.

To update your local digit, type `0-9`.

To connect to a new node, type `+XXX.XX.XX.XX:YYYY`, where `XXX.XX.XX.XX` is the ip address of the node you want to connect to and `YYYY` is the portname.

To enter evil mode, type `-`. This will cause the local node to report its timestamp as `1` and its TCP/IP address as a bunch of zeros. 




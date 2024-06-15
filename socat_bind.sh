#!/bin/bash


socat TCP-LISTEN:1011,fork,bind=X.X.X.X TCP:192.168.100.1:80,bind=192.168.0.2,so-bindtodevice=enp3s0f1

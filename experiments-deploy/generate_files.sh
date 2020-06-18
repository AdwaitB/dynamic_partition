#!/bin/bash
mkdir -p /root/deploy/files
#declare -a arr=(16 64 128 256 2048 8192 16384 32768)
#for e in `seq 1 4096`
declare -a arr=(32 64 256 512 1024 2048 16384 32768)
for e in `seq 1 1024`
do
    echo  -n 1 >> /root/deploy/files/1
done

for i in "${arr[@]}"
do
   for (( e=0; e<$i; e++))
   do
	cat /root/deploy/files/1 >> /root/deploy/files/$i
   done
done

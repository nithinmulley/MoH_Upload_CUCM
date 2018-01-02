# MoH_Upload_CUCM
Upload MoH Files on CUCM Servers in a cluster in parallel with Selenium

#Why?
The way CUCM handles MoH [Music on Hold] is elegant. But that leaves us with
uploading the same file on every server in the cluster using the web GUI.
I have not come across any other way to upload MoH files on the cluster 
without using the web GUI. If there are anything less than 3 servers in the 
cluster and one or two files to update, that's not frustrating. But anything 
beyond that can be quite tedious and waste of time when you are supposed to 
work on issues which require your attention. 
This script allows you to upload MoH files on all the Servers[MoH] in the 
cluster parallely. With automatic login on all the servers, there is no 
intervention required once the script is run. I work with multiple clusters 
and where I work I need to upload new MoH files on a regular basis for 
different offices using the same cluster. And this script saves a lot of 
time for me. Until there is a new way of doing it, this is my way of doing it.

#Setup?
Before starting to use this script, ensure you have all the dependencies 
installed.

Chrome Web Driver: Latest (Tested on v2.34)
Python Version: 3.4 and above
Additional Packages required:
	- selenium (Tested on v3.4.3)
	- PyYAML (Tested on v3.12)
Use the 'template.yaml' file to save the settings related to your cluster. You 
can create multiple yaml files to store settings of multiple clusters if you 
have. Supplied 'template.yaml' has comments for all the settings required.

#Run?
Supply the yaml file as an argument to the script.

	$python MoH_Upload_CUCM.py template.yaml


You'll see multiple chrome windows opened up. Once for each server in your 
cluster. They'll be closed once the uploading (and deleting if selected) is 
completed on all servers. From where I connect, the average delay is 25ms 
for all the servers in the cluster and it takes about 80 secs for a 3 MB file
to upload on all servers. Mileage can vary based on the average delay and 
BandWidth between your PC and the servers.

NOTE: This script is CPU intensive as it opens up multiple chrome windows in 
parallel threads. Make sure your PC is not very busy with other tasks. I work 
with mutiple clusters on a daily basis. One cluster is a Mega Cluster with
11 servers in it. My PC [with Intel Core i5 and 8GB RAM] handles it 
effortlessly.


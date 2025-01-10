# ssync
A syncronization system to deploy core packages and manage configurations across multiple systems. Provides `backup` and `deployment` modes to either either backup configuration and package list updates to relevant seconary locations, or grab the configurations and package lists from that location to the current machine, updating relevant config options. 

The location to backup to and deploy from should be available across all machines, for instance, a private git repo or shared network storage.



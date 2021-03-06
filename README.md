## Optopus CLI
This uses the optopus API to get information about nodes as well as execute commands against the search results.

### Basic configuration
To get going, you can set the environment variable <code>OPTOPUS_ENDPOINT</code> or the flag <code>--optopus-endpoint</code> to the location of your optopus installation.

### Example queries
Search queries are passed to optopus which in turn just uses elasticsearch. Pretty much any elasticsearch query string will work. The <code>--show-facts</code> flag can be used to display facts about the resulting nodes.

    $ optopus-cli search location:nyc02 and facts.productname:PowerEdge --show-facts productname ipaddress
    dev-db01.nyc02.foo.net
        productname: PowerEdge R510
          ipaddress: 10.0.88.25

    ops-master02.nyc02.foo.net
        productname: PowerEdge C1100
          ipaddress: 10.0.80.4

    ..snip..

### Run commands against the resulting hosts
Running commands just uses Fabric. You can set the login user by setting the environment variable <code>FAB_USER</code>, or passing in the <code>--fab-user</code> flag. If you want to run comands in parallel, use the <code>--parallel</code> flag.

    $ optopus-cli search location:tx01 and facts.productname:PowerEdge --run uptime

Or with sudo

    $ optopus-cli search location:ma01 and facts.productname:PowerEdge --sudo tail /var/log/messages

#### Additional functionality
You can use the <code>--put</code> flag to scp files to remote hosts and the <code>--get</code> flag to retrieve files from remote hosts.

### Getting child nodes
This feature will return all children that are related to the supplied node.


    $ optopus-cli get-children some-switch
    some-host1
    some-host2
    ...snip...

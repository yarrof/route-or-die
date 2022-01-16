# Route or Die!

## Story

You wake up alone lying on the floor in a dusty old building.
You turn your head and see **an ancient network map** ([`.png`](media/admin/network.png), [`.pdf`](media/admin/network.pdf), [`.svg`](media/admin/network.svg), [`.drawio`](media/admin/network.drawio))
beside you with a note on top saying

***ROUTE OR DIE!***

Shaken with fear you get up and look around.
All over the place you see enormous, ancient computers huge as refrigerators equipped with
vibrating CRTs showing fuzzy, blinking, green terminal prompts having white mechanic keyboards
turned yellow with age in front of them ... and the cables ... likes snakes they wrap around
your ankle as if trying to crawl up on your neck to suffocate you.

After overcoming your desperation you flip the note and find the following instructions ...

## What are you going to learn?

- How does routing logic work
- How to read a routing table using the `route` or the `ip route` commands
- How to view a host's assigned IP or IPs using `ip addr`
- How `ping` works
- How `traceroute` works
- What is a *hop*
- What is a *gateway*
- What are directly connected networks
- What is static routing
- What is dynamic routing (compared to static routing)

## Tasks

1. Grab and start a VM image pre-loaded with Mininet.
    - [Downloaded and started VM image containing Mininet from here](https://github.com/CodecoolBase/short-admin-vms/releases/latest/download/ubuntu-18.04-mininet.ova)
    - A shared folder is created between host and guest, the starter code is accessible from within the guest

2. Run `./mn.py` as `root` and note down your random network seed identifier.
    - Run `./mn.py` without any arguments and noted the down seed number from its output, e.g. 3070 in the following case

```
# ./mn.py
*** Using seed: 3070
mininet>
```
    - The same generated seed is used in every other tasks

3. Connect the `n1` and `n3` networks by configuring routing tables on the required nodes.
    - All hosts in `n1` can ping all hosts in `n3`
    - All hosts in `n3` can ping all hosts in `n1`
    - `task1.ini` contains the required routing commands
    - Running `./mn.py --task 1 --test --seed <your-seed>` outputs `Results: 0% dropped`

4. Connect the `n2` and `n3` networks by configuring routing tables on the required nodes.
    - All hosts in `n2` can ping all hosts in `n3`
    - All hosts in `n3` can ping all hosts in `n2`
    - `task2.ini` contains the required routing commands
    - Running `./mn.py --task 2 --test --seed <your-seed>` outputs `Results: 0% dropped`

5. Connect the `n2` and `n5` networks by configuring routing tables on the required nodes.
    - All hosts in `n2` can ping all hosts in `n5`
    - All hosts in `n5` can ping all hosts in `n2`
    - `task3.ini` contains the required routing commands
    - Running `./mn.py --task 3 --test --seed <your-seed>` outputs `Results: 0% dropped`

6. Connect the `n3` and `n5` networks by configuring routing tables on the required nodes.
    - All hosts in `n3` can ping all hosts in `n5`
    - All hosts in `n5` can ping all hosts in `n3`
    - `task4.ini` contains the required routing commands
    - Running `./mn.py --task 4 --test --seed <your-seed>` outputs `Results: 0% dropped`

7. Connect the `n1`, `n2` and `n4` networks by configuring routing tables on the required nodes.
    - All hosts in `n1` can ping all hosts in `n2` and `n4`
    - All hosts in `n2` can ping all hosts in `n1` and `n4`
    - All hosts in `n4` can ping all hosts in `n1` and `n2`
    - `task5.ini` contains the required routing commands
    - Running `./mn.py --task 5 --test --seed <your-seed>` outputs `Results: 0% dropped`

8. Connect every network with each other by configuring routing tables on the required nodes.
    - Every host can ping every other host in any network
    - `task6.ini` contains the required routing commands
    - Running `./mn.py --task 6 --test --seed <your-seed>` outputs `Results: 0% dropped`

## General requirements

- Test `.txt` files are not modified, e.g. `test1.txt`, `test2.txt`, etc.
- `mn.py` is not modified
- Each task `.ini` file e.g. `task1.ini`, `task2.ini`, etc. should contain a comment with the seed used, e.g

```
# seed=1234
r1 ip add route ...
```

## Hints

- If you get errors when running `./mn.py` (saying that is already running or similar) execute this `sudo fuser --kill 6653/tcp` and try again
- Map out the network!
  1. Find the address of each host
  1. Find the network address and mask for each group of hosts
  1. Find the _all_ addresses and interface names of each router
  1. Find the network address and mask for each connected routers
  1. Draw the darn thing!
- To allow host _A_ to ping host _B_ routes must from _A_ to _B_ **_and_** from _B_ to _A_ as well!
- In the task `.ini` files you can use comments and empty lines, e.g.

  ```text
  # seed=1234
  # This commands allows ...
  r1 ip route add ...

  # This other one ...
  r2 ip route add ...
  ```
- **When you are reading background materials:**
  - [Adding Routes with the `ip` Command](https://www.linuxtechi.com/add-delete-static-route-linux-ip-command/)
    - Use `route -n` to view routing tables for now, but you can try at other commands as well, the main to thing to remember is that there are a lot of tools for the same purpose
    - When adding routes use the `ip route add` command instead of `route add`
    - When adding routes you can always almost omit specifying the network interface section, e.g. `dev dev enp0s3` part
    - You can skip the part on how to permanently add a static route to a system
  - [How `traceroute` Work](https://networklessons.com/cisco/ccna-routing-switching-icnd1-100-105/traceroute)
    - Read only the general description of how the command works, up to the first section, _1. Traceroute Command_

## Background materials

- <i class="far fa-exclamation"></i> [`ping` Command in Linux](https://linuxize.com/post/linux-ping-command)
- <i class="far fa-exclamation"></i> [Adding Routes with the `ip` Command](https://www.linuxtechi.com/add-delete-static-route-linux-ip-command/)
- [How `traceroute` Work](https://networklessons.com/cisco/ccna-routing-switching-icnd1-100-105/traceroute)

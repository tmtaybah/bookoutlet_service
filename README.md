# Introduction
Put simply, this project just cross-checks Bookoutlet.com against a user's Goodreads want-to read list (or possibly any other list they provide) created using Flask and Goodreads' API.
The motivation is a personal one, I'm always looking for a good deal on books but once I get on Bookoutlet I can't seem to use their site to find any books I actually want and just end up randomly scrolling through the "related books" section until something I want pops up.

---

# Installation
1. Git clone the project

2. install the project dependencies found in requirements.txt  

```
pip3 install -r requirements.txt
```
3. run the server

```
python3 run.py
```

---

### #TODO:
+ fix oauth (not very reliable atm)
+ add notifier
+ fix db scheme
+ containerize server using docker

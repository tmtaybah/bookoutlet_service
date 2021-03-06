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

### TO-DO:
- [x] fix oauth (not very reliable atm)
- [ ] add notifier/ email w SendGrid maybe
- [x] fix db scheme
- [ ] containerize server using docker
- [ ] explain why oauth1 is used instead of standard oauth2
- [ ] flash message when logout 
- [x] ask user for profile link during registration + able to update on account page  
- [x] double check user id when authorizing 
- [ ] add section on how to deauthorize app 
- [x] add db migration 
- [ ] integrate/ scale w Celery 
- [ ] explore using vue.js on frontend 
- [ ] add more comprehensive testing 
- [ ] add links to matches 


# Course Grade Directory

It's a basic TCP server which allows for students enrolled in a course to fetch their latest test score results.

## Setup

The client and server scripts are written in [python3](https://www.python.org/downloads/).

### Install Dependencies
1. Install [pip](https://pip.pypa.io) and [venv](https://docs.python.org/3/library/venv.html)

2. Clone this repository
```sh
 $ git clone https://github.com/DeeprajPandey/networks.git
 $ cd networks/A4P3
```

3. Create a venv and activate it
```sh
 $ python3 -m venv .
 $ source ./bin/activate
```
If you're on Windows, you may have to specify the full path to your python installation directory
```sh
 $ c:\python36\python.exe -m venv c:\path\to\curr\dir
 $ .\env\Scripts\activate
```

4. Install the dependencies required by the server
```sh
 $ pip install -r requirements.txt
```

### Run

Start the server (it runs on your local machine by default).
If you want clients on your network to have access to it, run `ifconfig` to get your IP address and change `IP` in `Main()` in **server.py** and in **client.py** to that (do this only if you understand what you are doing) and run the script.
```sh
 $ python3 server.py
```

In another terminal session, run the client and start communicating (send `HELP` on first run to get the server spec).
```sh
 $ python3 client.py
```

### To Do
- [ ] Add 2FA via OTP sent over email when registering new users
- [ ] Store a salted hash instead of plaintext passwords
- [ ] Extend 2FA to support time based authenticators (e.g. Google Authenticator)
- [ ] Add multi-threading for handling clients

### License
CC BY-NC 4.0 International

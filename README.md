# NVIDIA Web Monitor

*NVIDIA Web Monitor is a simple tool based on Flask for serving and monitoring nvidia-smi in the browser.*

It can be used for monitoring GPUs on localhost or remote host servers at the same time. Consider your research lab has several GPU servers (independent, not a cluster) that are available to everyone in the lab. To reach a better resource utilization, you want a web page that shows all the GPU status at the same time and here is what you want.

## Prerequisites

1. On the serving host (maybe localhost)

    Python 3.6 with:
    - Flask
    - PyYAML
    - Pipenv (optional)

    The code was tested on Ubuntu 14.04, with Python 3.6, Flask 1.0.2 and PyYAML 3.13.

    Quick install with [Pipenv](https://pipenv.readthedocs.io/en/latest/):

    ```shell
    $ pip install pipenv
    $ pipenv install  # this will create a virtual environment for this project
    $ pipenv shell    # enter the virtual environment
    ```

2. On the remote hosts to be monitored

    - OpenSSH Server (`sudo apt install openssh-server`)
    - NVIDIA driver (to use `nvidia-smi`)

3. SSH passwordless

    - Create authentication SSH-Kegen keys on the serving host:

        ```shell
        $ ssh-keygen  # just press Enter for default settings
        Generating public/private rsa key pair.
        Enter file in which to save the key (/home/user/.ssh/id_rsa):
        Created directory '/home/user/.ssh'.
        Enter passphrase (empty for no passphrase):
        Enter same passphrase again:
        Your identification has been saved in /home/user/.ssh/id_rsa.
        Your public key has been saved in /home/user/.ssh/id_rsa.pub.
        The key fingerprint is:
        SHA256:47VkvSjlFhKRgz/6RYdXM2EULtk9TQ65PDWJjYC5Jys user@local
        The key's randomart image is:
        +---[RSA 2048]----+
        |       ...o...X+o|
        |      . o+   B=Oo|
        |       .....ooo*=|
        |        o+ooo.+ .|
        |       .SoXo.  . |
        |      .E X.+ .   |
        |       .+.= .    |
        |        .o       |
        |                 |
        +----[SHA256]-----+
        ```

    - Copy the key to the remote server:

        ```shell
        $ ssh-copy-id user@remote -p port
        /usr/bin/ssh-copy-id: INFO: Source of key(s) to be installed: "/home/user/.ssh/id_rsa.pub"
        /usr/bin/ssh-copy-id: INFO: attempting to log in with the new key(s), to filter out any that are already installed
        /usr/bin/ssh-copy-id: INFO: 1 key(s) remain to be installed -- if you are prompted now it is to install the new keys
        user@remote's password:

        Number of key(s) added: 1

        Now try logging into the machine, with:   "ssh 'user@remote' -p port"
        and check to make sure that only the key(s) you wanted were added.
        ```

## Run and serve

1. Configure the querying command options and host addresses in [`config.yaml`](config.yaml)
2. Run the Flask application

    ```shell
    $ FLASK_APP=main flask run
     * Serving Flask app "main"
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
    ```

    Now head over to http://127.0.0.1:5000/ to see something like the following:

    [![demo](assets/demo.jpg)](https://raw.githubusercontent.com/DAA233/nvidia-web-monitor/32dc6e112841a5688e33a0050294dea06bf70c6c/assets/demo.jpg)

    If you have the debugger disabled or trust the users on your network, you can make the server publicly available simply by adding `--host=0.0.0.0` to the command line:

    ```shell
    $ FLASK_APP=main flask run --host=0.0.0.0
     * Serving Flask app "main"
     * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
    ```

    This tells your operating system to listen on all public IPs. To get more information, read the [Flask documentation](http://flask.pocoo.org/docs/1.0/quickstart/#a-minimal-application).

## References

1. [Flask’s documentation](http://flask.pocoo.org/docs/1.0/)
2. [SSH 基本用法](https://zhuanlan.zhihu.com/p/21999778)

# convertit

## Description

`convertit` is a server that will allow you to convert **Html** and **Libre Office** documents to **Pdf**.

Supported formats:
* *odt*
* *ott*
* *oth*
* *odm*
* *otm*
* *odg*
* *otg*
* *odp*
* *otp*
* *ods*
* *ots*
* *odc*
* *odf*
* *odi*
* *docx*
* *doc*
* *html*

## How it works

### How to run the server on localhost

The simplest way is to use *Docker*. You will only need to build the **Dockerfile** and start a container. If you are at the root of the project:

```
docker build -t server .
docker run -itd -p "127.0.0.1:8000:8000" server
```

### How to make a request to the server

This server has only one route (the root). To convert a valid document:

```
>>> from requests import post
>>> files = {'file': ('name.ext', open(path, 'rb'), 'mimetype')}
>>> response = post('http://127.0.0.1:8000/', files=files)
```

# Good practices when you want to participate

## Set up a virtual environment

If virtualenv is not installed, run the following command in your terminal:

```
pip3 install virtualenv
```

Then create a virtual environment by running:

```
virtualenv ./venv
```

Activate it by running:

```
source ./venv/bin/activate
```

## Tool for style guide enforcement

*It is advisable to use a tool for style guide enforcement.*

### Flake8

If your virtual environment is not active, run:

```
source ./venv/bin/activate
```

Install flake8 by running:

```
pip install flake8
```

If you use vscode, you can configure it to use flake8:

```
ctrl + maj + p > Python: select linter
```

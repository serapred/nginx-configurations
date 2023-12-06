# nginx-modular

modular configuration files for nginx web-server.
demo to showcase the rate_limit[https://www.nginx.com/blog/rate-limiting-nginx/] functionality.

## Introduction

NGINX rate limiting uses the leaky bucket algorithm,
which is widely used in telecommunications and packet‑switched computer networks
to deal with burstiness when bandwidth is limited.
The analogy is with a bucket where water is poured in at the top and leaks from the bottom;
if the rate at which water is poured in exceeds the rate at which it leaks, the bucket overflows.
In terms of request processing, the water represents requests from clients,
and the bucket represents a queue where requests wait to be processed
according to a first‑in‑first‑out (FIFO) scheduling algorithm.
The leaking water represents requests exiting the buffer for processing by the server,
and the overflow represents requests that are discarded and never serviced.

## Directory structure

this project has the following structure:

```sh
├── disable.sh
├── docker-compose.yml
├── nginx
│   ├── certs
│   │   ├── ssl_certificate.crt
│   │   └── ssl_certificate.key
│   ├── conf.d
│   │   ├── events.conf
│   │   ├── http
│   │   │   ├── headers.conf
│   │   │   ├── limits.conf
│   │   │   ├── main.conf
│   │   │   └── ssl.conf
│   │   └── main.conf
│   ├── mime.types
│   ├── nginx.conf
│   ├── proxy_params
│   ├── servers
│   │   ├── default.conf
│   │   └── proxy._conf
│   └── upstreams
│       └── example._conf
├── README.md
└── test.py

```

## Nginx Configuration

The nginx.conf modularizes other files via include mechanism.
files with the extention '\_conf' will be ignored.

```
[nginx.conf]

include conf/main.conf;     # main context directives

events { 
  include conf/events.conf; # events directive
}

http {
  include conf.d/http/main.conf;       # global http(s) directives
  include conf.d/http/upstream/*.conf; # upstream
  include conf.d/http/servers/*.conf;  # virtual servers
}


```


## Limit-Rate Configuration

the limit-rate mechanism is defined in `conf.d/http/limits.conf`:

```
[limits.conf]

# limit_req_zone key zone=name:size rate=rate;
# processing rate of requests coming from a single IP address.
# The limitation is done using the “leaky bucket” method.
limit_req_zone  $binary_remote_addr zone=limitreqbyaddr:64m rate=1r/s;
limit_req_zone  $server_name zone=limitreqbyserver:64m rate=1r/s;

# limit_req_log_level info | notice | warn | error;
limit_req_log_level error;

# limit_conn_zone key zone=name:size;
# limits the number of connections from a single IP address.
limit_conn_zone $binary_remote_addr zone=limitconnbyaddr:32m;
limit_conn_zone $server_name zone=limitconnbyserver:32m;

# limit_conn_log_level info | notice | warn | error;
limit_conn_log_level error;

# limit_req zone=name [burst=number] [nodelay | delay=number];
# If the requests rate exceeds the rate configured for a zone,
# their processing is delayed such that requests are processed at a defined rate.
# Excessive requests are delayed until their number exceeds the maximum burst size
# in which case the request is terminated with an error
limit_req zone=limitreqbyaddr;
limit_req zone=limitreqbyserver;

# limit_conn zone number;
limit_conn limitconnbyaddr 5;
limit_conn limitconnbyserver 5;

# limit_*_status status;
# error status code
limit_req_status 429;
limit_conn_status 429;

```

To configure the limit rate use the limit_req_zone directive to define shared memory space for the requests
and the rate itself. In this example the rate is set to 1 response per second with no burst allowed (and consequently no-delay).
Finally, to actually enable the limit-rate use the limit_req directive passing the relative zone and burst behaviour as parameters.
It is possible to define multimple limit_req with different req_zones (here showcased by address and server name).


## Testing

to test that everything is working launch the server with:
```sh
docker-compose up -d --build
```
and test the limit rate with:
```sh
# 1 request per second (OK)
python test.py -n 10 -r 1

# 2 requests per second (1 OK/1 ERROR)
python test.py -n 10 -r 2

# 4 requests per second (1 OK/3 ERRORS)
python test.py -n 10 -r 4

# and so on for induction
# R requests per second (1 OK/R-1 ERRORS)
# python test.py -n 10 -r R
```

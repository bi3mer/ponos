# Ponos

Ponos is a tool for building a [Markov Decision Process (MDP)](https://en.wikipedia.org/wiki/Markov_decision_process) that assembles video game levels for dynamic difficult adjustment. It is the work behind my dissertation, and it combines the work of three papers into one:

- [Paper](https://bi3mer.github.io/pdf/2021_gram_elites.pdf), [Repo](https://github.com/bi3mer/GramElites)
- [Paper](https://arxiv.org/pdf/2203.05057), [Repo](https://github.com/bi3mer/LinkingLevelSegments)
- [Paper](https://arxiv.org/pdf/2304.13922), [Repo](https://github.com/bi3mer/mdp-level-assembly)

## Usage

Ponos works by interacting with a socket server or a REST server. For the command below to work, the server must be running. Examples of kinds of servers can be seen in the [examples repo](https://github.com/bi3mer/ponos-example). Fair warning, sockets are, unsurprisingly, a lot faster, so I recommend using them.

### Socket Server

```bash
pypy3 ponos/ponos.py --model-name mario
```

### REST Server
```bash
pypy3 ponos/ponos.py --model-name mario --use-rest-server --port 5000
```

### Help
```bash
> python ponos/ponos.py --help
usage: ponos.py [-h] [--host HOST] [--port PORT] [--use-rest-server] --model-name MODEL_NAME

Ponos

options:
  -h, --help            show this help message and exit
  --host HOST           URL for host, defaults to 127.0.0.1
  --port PORT           URL for host, defaults to 8000
  --use-rest-server     Set to true if the server uses REST instead of a socket. Default is to use a socket.
  --model-name MODEL_NAME
                        Name of file for resulting pickle file (don't include extension).
```

## Cite

TBD
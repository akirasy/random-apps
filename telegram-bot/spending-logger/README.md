### Build docker container

1. Edit `config.py` accordingly.
2. Build docker container using command as below:

```
docker build -t ptb-spending-logger .
```

### Use and run docker container in host machine

1. Create `directory` in host machine.

```
mkdir -p $(HOME)/docker-share/spending-logger
```

2. Run docker command as below:

```
docker run \
--detach \
--restart unless-stopped \
-v $(HOME)/docker-share/spending-logger:/usr/src/app/volume-host/ \
ptb-spending-logger
```

3. Initialize database in `Telegram`.

```
/init_database
```

4. Database `database.db` is in sqlite format and is available at `$(HOME)/docker-share/spending-logger` in host directory.

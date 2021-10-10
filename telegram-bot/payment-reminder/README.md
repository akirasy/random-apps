### Build docker container

1. Edit `config.py` accordingly.
2. Build docker container using command as below:

```
docker build -t ptb-payment-reminder .
```

### Use and run docker container in host machine

1. Create `directory` in host machine.

```
mkdir -p $(HOME)/docker-share/payment-reminder
```

2. Run docker command as below:

```
docker run \
--detach \
--restart unless-stopped \
-v $(HOME)/docker-share/payment-reminder:/usr/src/app/volume-host/ \
ptb-payment-reminder
```

3. Initialize database in `Telegram`.

```
/init_database
```

4. Database `database.db` is in sqlite format and is available at `$(HOME)/docker-share/payment-reminder` in host directory.

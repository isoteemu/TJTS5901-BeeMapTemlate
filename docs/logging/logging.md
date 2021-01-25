## Logging theory

Logging artifacts that fall into an uncanny valley are most valuable – things that seem normal, but there is something odd about them.

Common layers of logging are: [^Securing_DevOps]

- **Collection Layer**:
  Takes logs from applications and systems and networks and such. Even from github/gitlab.

- **Streaming Layer**:
  Message broker, queues and delivers logs to different analyzers.

- **Analysis layer**:
  Different things for different tasks. Some for storing logs, some for statistics, and some for anomalies.

- **Storage layer**:
  Recent logs into a database, and older logs into archive.

- **Access layer**:
  Dashboard for human consumption.

## Logging setup

### Basic logging in python

Getting basic logging requires importing `logging` module, and defining both logger instance, and stream handler. [^logging]
```
    # Import inbuild logging library
    import logging

    # Setup logging object for current context:
    logger = logging.getLogger(__name__)
    # Define basic config, which sets the handler to console by default
    logger.basicConfig(level=logging.DEBUG)
```



[^Securing_DevOps]: Securing DevOps, Julien Vehent, 2018
[^logging]: https://docs.python.org/dev/howto/logging.html
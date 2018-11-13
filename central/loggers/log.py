import logging
import logging.config as log_conf


log_config = {
    'version': 1.0,
    'formatters': {
        'detail': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
        'simple': {
            'format': '%(name)s - %(levelname)s - %(message)s',
        },

    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'detail'
        },
        'logstash': {
            'level': 'WARNING',
            'class': 'logstash.TCPLogstashHandler',
            'host': 'localhost',
            'port': 5959,
            'version': 1,
            'message_type': 'logstash',
            'fqdn': False,
            'tags': []
        }
    },
    'loggers': {
        'crawler': {
            'handlers': ['console', 'logstash'],
            'level': 'DEBUG',
        },
        'parser': {
            'handlers': ['console', 'logstash'],
            'level': 'INFO',
        },
        'other': {
            'handlers': ['console', 'logstash'],
            'level': 'INFO',
        },
        'storage': {
            'handlers': ['console', 'logstash'],
            'level': 'INFO',
        }
    }
}

log_conf.dictConfig(log_config)

crawler = logging.getLogger('crawler')
parser = logging.getLogger('parser')
other = logging.getLogger('other')
storage = logging.getLogger('storage')



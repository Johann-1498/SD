service_properties = {
    'Product': {
        'properties': {
            'sku': {
                'type': 'str',
                'default': None,
                'required': True,
                'description': 'Product SKU',
            },
            'name': {
                'type': 'str',
                'default': None,
                'required': True,
                'description': 'Product name',
            },
            'price': {
                'type': 'float',
                'default': 0.0,
                'required': True,
                'description': 'Unit price',
            },
            'dbcon': {
                'type': 'classref',
                'default': None,
                'required': False,
                'description': 'Database connection reference',
            },
            'mq': {
                'type': 'classref',
                'default': None,
                'required': False,
                'description': 'Async messaging reference',
            },
        },
        'methods': ['insert'],
    },
    'Stock': {
        'properties': {
            'warehouse': {
                'type': 'str',
                'default': None,
                'required': True,
                'description': 'Warehouse code',
            },
            'quantity': {
                'type': 'int',
                'default': 0,
                'required': True,
                'description': 'Stock units',
            },
        },
        'methods': ['insert'],
    },
    'Notification': {
        'properties': {
            'channel': {
                'type': 'str',
                'default': 'email',
                'required': True,
                'description': 'Notification channel',
            },
            'message': {
                'type': 'str',
                'default': None,
                'required': True,
                'description': 'Notification payload',
            },
        },
        'methods': ['send'],
    },
}

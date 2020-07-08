vagrant_image = "ubuntu-custom"

#g5k_loc = "rennes"
#g5k_cluster = "paravance"

#g5k_loc = "nancy"
#g5k_cluster = "grisou"
#g5k_cluster = "gros"
g5k_loc = "nantes"
# g5k_cluster = "econome"
g5k_cluster = "ecotype"

# g5k_loc = "lyon"
# g5k_cluster = "sagittaire"
# g5k_image = "https://api.grid5000.fr/4.0/sites/{}/public/alexvankempen/mydebian.env".format(g5k_loc)
g5k_image = "https://api.grid5000.fr/sid/sites/rennes/public/alexvankempen/mydebian.env"

INFRA_two = {
    "master": {},
    "node1": {"node2": "50ms"},
    "node2": {"node1": "50ms"}
}

INFRA_triangle = {
    "master": {},
    "node1": {
        "node2": "50ms",
        "node3": "50ms"
    },
    "node2": {
        "node3": "50ms"
    },
    "node3": {}
}

INFRA_complete_20 = {'master': {},
                     'node1': {'node2': '50ms', 'node3': '50ms', 'node4': '50ms', 'node5': '50ms', 'node6': '50ms',
                               'node7': '50ms', 'node8': '50ms', 'node9': '50ms', 'node10': '50ms', 'node11': '50ms',
                               'node12': '50ms', 'node13': '50ms', 'node14': '50ms', 'node15': '50ms', 'node16': '50ms',
                               'node17': '50ms', 'node18': '50ms', 'node19': '50ms', 'node20': '50ms'},
                     'node2': {'node1': '50ms', 'node3': '50ms', 'node4': '50ms', 'node5': '50ms', 'node6': '50ms',
                               'node7': '50ms', 'node8': '50ms', 'node9': '50ms', 'node10': '50ms', 'node11': '50ms',
                               'node12': '50ms', 'node13': '50ms', 'node14': '50ms', 'node15': '50ms', 'node16': '50ms',
                               'node17': '50ms', 'node18': '50ms', 'node19': '50ms', 'node20': '50ms'},
                     'node3': {'node1': '50ms', 'node2': '50ms', 'node4': '50ms', 'node5': '50ms', 'node6': '50ms',
                               'node7': '50ms', 'node8': '50ms', 'node9': '50ms', 'node10': '50ms', 'node11': '50ms',
                               'node12': '50ms', 'node13': '50ms', 'node14': '50ms', 'node15': '50ms', 'node16': '50ms',
                               'node17': '50ms', 'node18': '50ms', 'node19': '50ms', 'node20': '50ms'},
                     'node4': {'node1': '50ms', 'node2': '50ms', 'node3': '50ms', 'node5': '50ms', 'node6': '50ms',
                               'node7': '50ms', 'node8': '50ms', 'node9': '50ms', 'node10': '50ms', 'node11': '50ms',
                               'node12': '50ms', 'node13': '50ms', 'node14': '50ms', 'node15': '50ms', 'node16': '50ms',
                               'node17': '50ms', 'node18': '50ms', 'node19': '50ms', 'node20': '50ms'},
                     'node5': {'node1': '50ms', 'node2': '50ms', 'node3': '50ms', 'node4': '50ms', 'node6': '50ms',
                               'node7': '50ms', 'node8': '50ms', 'node9': '50ms', 'node10': '50ms', 'node11': '50ms',
                               'node12': '50ms', 'node13': '50ms', 'node14': '50ms', 'node15': '50ms', 'node16': '50ms',
                               'node17': '50ms', 'node18': '50ms', 'node19': '50ms', 'node20': '50ms'},
                     'node6': {'node1': '50ms', 'node2': '50ms', 'node3': '50ms', 'node4': '50ms', 'node5': '50ms',
                               'node7': '50ms', 'node8': '50ms', 'node9': '50ms', 'node10': '50ms', 'node11': '50ms',
                               'node12': '50ms', 'node13': '50ms', 'node14': '50ms', 'node15': '50ms', 'node16': '50ms',
                               'node17': '50ms', 'node18': '50ms', 'node19': '50ms', 'node20': '50ms'},
                     'node7': {'node1': '50ms', 'node2': '50ms', 'node3': '50ms', 'node4': '50ms', 'node5': '50ms',
                               'node6': '50ms', 'node8': '50ms', 'node9': '50ms', 'node10': '50ms', 'node11': '50ms',
                               'node12': '50ms', 'node13': '50ms', 'node14': '50ms', 'node15': '50ms', 'node16': '50ms',
                               'node17': '50ms', 'node18': '50ms', 'node19': '50ms', 'node20': '50ms'},
                     'node8': {'node1': '50ms', 'node2': '50ms', 'node3': '50ms', 'node4': '50ms', 'node5': '50ms',
                               'node6': '50ms', 'node7': '50ms', 'node9': '50ms', 'node10': '50ms', 'node11': '50ms',
                               'node12': '50ms', 'node13': '50ms', 'node14': '50ms', 'node15': '50ms', 'node16': '50ms',
                               'node17': '50ms', 'node18': '50ms', 'node19': '50ms', 'node20': '50ms'},
                     'node9': {'node1': '50ms', 'node2': '50ms', 'node3': '50ms', 'node4': '50ms', 'node5': '50ms',
                               'node6': '50ms', 'node7': '50ms', 'node8': '50ms', 'node10': '50ms', 'node11': '50ms',
                               'node12': '50ms', 'node13': '50ms', 'node14': '50ms', 'node15': '50ms', 'node16': '50ms',
                               'node17': '50ms', 'node18': '50ms', 'node19': '50ms', 'node20': '50ms'},
                     'node10': {'node1': '50ms', 'node2': '50ms', 'node3': '50ms', 'node4': '50ms', 'node5': '50ms',
                                'node6': '50ms', 'node7': '50ms', 'node8': '50ms', 'node9': '50ms', 'node11': '50ms',
                                'node12': '50ms', 'node13': '50ms', 'node14': '50ms', 'node15': '50ms',
                                'node16': '50ms', 'node17': '50ms', 'node18': '50ms', 'node19': '50ms',
                                'node20': '50ms'},
                     'node11': {'node1': '50ms', 'node2': '50ms', 'node3': '50ms', 'node4': '50ms', 'node5': '50ms',
                                'node6': '50ms', 'node7': '50ms', 'node8': '50ms', 'node9': '50ms', 'node10': '50ms',
                                'node12': '50ms', 'node13': '50ms', 'node14': '50ms', 'node15': '50ms',
                                'node16': '50ms', 'node17': '50ms', 'node18': '50ms', 'node19': '50ms',
                                'node20': '50ms'},
                     'node12': {'node1': '50ms', 'node2': '50ms', 'node3': '50ms', 'node4': '50ms', 'node5': '50ms',
                                'node6': '50ms', 'node7': '50ms', 'node8': '50ms', 'node9': '50ms', 'node10': '50ms',
                                'node11': '50ms', 'node13': '50ms', 'node14': '50ms', 'node15': '50ms',
                                'node16': '50ms', 'node17': '50ms', 'node18': '50ms', 'node19': '50ms',
                                'node20': '50ms'},
                     'node13': {'node1': '50ms', 'node2': '50ms', 'node3': '50ms', 'node4': '50ms', 'node5': '50ms',
                                'node6': '50ms', 'node7': '50ms', 'node8': '50ms', 'node9': '50ms', 'node10': '50ms',
                                'node11': '50ms', 'node12': '50ms', 'node14': '50ms', 'node15': '50ms',
                                'node16': '50ms', 'node17': '50ms', 'node18': '50ms', 'node19': '50ms',
                                'node20': '50ms'},
                     'node14': {'node1': '50ms', 'node2': '50ms', 'node3': '50ms', 'node4': '50ms', 'node5': '50ms',
                                'node6': '50ms', 'node7': '50ms', 'node8': '50ms', 'node9': '50ms', 'node10': '50ms',
                                'node11': '50ms', 'node12': '50ms', 'node13': '50ms', 'node15': '50ms',
                                'node16': '50ms', 'node17': '50ms', 'node18': '50ms', 'node19': '50ms',
                                'node20': '50ms'},
                     'node15': {'node1': '50ms', 'node2': '50ms', 'node3': '50ms', 'node4': '50ms', 'node5': '50ms',
                                'node6': '50ms', 'node7': '50ms', 'node8': '50ms', 'node9': '50ms', 'node10': '50ms',
                                'node11': '50ms', 'node12': '50ms', 'node13': '50ms', 'node14': '50ms',
                                'node16': '50ms', 'node17': '50ms', 'node18': '50ms', 'node19': '50ms',
                                'node20': '50ms'},
                     'node16': {'node1': '50ms', 'node2': '50ms', 'node3': '50ms', 'node4': '50ms', 'node5': '50ms',
                                'node6': '50ms', 'node7': '50ms', 'node8': '50ms', 'node9': '50ms', 'node10': '50ms',
                                'node11': '50ms', 'node12': '50ms', 'node13': '50ms', 'node14': '50ms',
                                'node15': '50ms', 'node17': '50ms', 'node18': '50ms', 'node19': '50ms',
                                'node20': '50ms'},
                     'node17': {'node1': '50ms', 'node2': '50ms', 'node3': '50ms', 'node4': '50ms', 'node5': '50ms',
                                'node6': '50ms', 'node7': '50ms', 'node8': '50ms', 'node9': '50ms', 'node10': '50ms',
                                'node11': '50ms', 'node12': '50ms', 'node13': '50ms', 'node14': '50ms',
                                'node15': '50ms', 'node16': '50ms', 'node18': '50ms', 'node19': '50ms',
                                'node20': '50ms'},
                     'node18': {'node1': '50ms', 'node2': '50ms', 'node3': '50ms', 'node4': '50ms', 'node5': '50ms',
                                'node6': '50ms', 'node7': '50ms', 'node8': '50ms', 'node9': '50ms', 'node10': '50ms',
                                'node11': '50ms', 'node12': '50ms', 'node13': '50ms', 'node14': '50ms',
                                'node15': '50ms', 'node16': '50ms', 'node17': '50ms', 'node19': '50ms',
                                'node20': '50ms'},
                     'node19': {'node1': '50ms', 'node2': '50ms', 'node3': '50ms', 'node4': '50ms', 'node5': '50ms',
                                'node6': '50ms', 'node7': '50ms', 'node8': '50ms', 'node9': '50ms', 'node10': '50ms',
                                'node11': '50ms', 'node12': '50ms', 'node13': '50ms', 'node14': '50ms',
                                'node15': '50ms', 'node16': '50ms', 'node17': '50ms', 'node18': '50ms',
                                'node20': '50ms'},
                     'node20': {'node1': '50ms', 'node2': '50ms', 'node3': '50ms', 'node4': '50ms', 'node5': '50ms',
                                'node6': '50ms', 'node7': '50ms', 'node8': '50ms', 'node9': '50ms', 'node10': '50ms',
                                'node11': '50ms', 'node12': '50ms', 'node13': '50ms', 'node14': '50ms',
                                'node15': '50ms', 'node16': '50ms', 'node17': '50ms', 'node18': '50ms',
                                'node19': '50ms'}}

INFRA_complete_10 = {
    "master": {},
    "node1": {
        "node2": "50ms",
        "node3": "50ms",
        "node4": "50ms",
        "node5": "50ms",
        "node6": "50ms",
        "node7": "50ms",
        "node8": "50ms",
        "node9": "50ms",
        "node10": "50ms"
    },
    "node2": {
        "node1": "50ms",
        "node3": "50ms",
        "node4": "50ms",
        "node5": "50ms",
        "node6": "50ms",
        "node7": "50ms",
        "node8": "50ms",
        "node9": "50ms",
        "node10": "50ms"
    },
    "node3": {
        "node1": "50ms",
        "node2": "50ms",
        "node4": "50ms",
        "node5": "50ms",
        "node6": "50ms",
        "node7": "50ms",
        "node8": "50ms",
        "node9": "50ms",
        "node10": "50ms"
    },
    "node4": {
        "node1": "50ms",
        "node2": "50ms",
        "node3": "50ms",
        "node5": "50ms",
        "node6": "50ms",
        "node7": "50ms",
        "node8": "50ms",
        "node9": "50ms",
        "node10": "50ms"
    },
    "node5": {
        "node1": "50ms",
        "node2": "50ms",
        "node3": "50ms",
        "node4": "50ms",
        "node6": "50ms",
        "node7": "50ms",
        "node8": "50ms",
        "node9": "50ms",
        "node10": "50ms"
    },
    "node6": {
        "node1": "50ms",
        "node2": "50ms",
        "node3": "50ms",
        "node4": "50ms",
        "node5": "50ms",
        "node7": "50ms",
        "node8": "50ms",
        "node9": "50ms",
        "node10": "50ms"
    },
    "node7": {
        "node1": "50ms",
        "node2": "50ms",
        "node3": "50ms",
        "node4": "50ms",
        "node5": "50ms",
        "node6": "50ms",
        "node8": "50ms",
        "node9": "50ms",
        "node10": "50ms"
    },
    "node8": {
        "node1": "50ms",
        "node2": "50ms",
        "node3": "50ms",
        "node4": "50ms",
        "node5": "50ms",
        "node6": "50ms",
        "node7": "50ms",
        "node9": "50ms",
        "node10": "50ms"
    },
    "node9": {
        "node1": "50ms",
        "node2": "50ms",
        "node3": "50ms",
        "node4": "50ms",
        "node5": "50ms",
        "node6": "50ms",
        "node7": "50ms",
        "node8": "50ms",
        "node10": "50ms"
    },
    "node10": {
        "node1": "50ms",
        "node2": "50ms",
        "node3": "50ms",
        "node4": "50ms",
        "node5": "50ms",
        "node6": "50ms",
        "node7": "50ms",
        "node8": "50ms",
        "node9": "50ms",
    }
}

INFRA_test = {
    "master": {},
    "node1": {
        "node2": "30ms",
        "node4": "10ms"
    },
    "node2": {
        "node4": "10ms",
        "node5": "20ms"
    },
    "node3": {
        "node4": "20ms"
    },
    "node4": {
        "node5": "30ms"
    },
    "node5": {}
}

INFRA_0 = {
    "master": {},
    "node1": {
        "node2": "40ms",
        "node8": "80ms"
    },
    "node2": {
        "node3": "80ms",
        "node8": "110ms"
    },
    "node3": {
        "node4": "70ms",
        "node6": "40ms",
        "node9": "20ms"
    },
    "node4": {
        "node5": "90ms",
        "node6": "140ms"
    },
    "node5": {
        "node6": "100ms"
    },
    "node6": {
        "node7": "20ms"
    },
    "node7": {
        "node8": "10ms",
        "node9": "60ms"
    },
    "node8": {
        "node9": "70ms"
    },
    "node9": {}
}
'''
 {1, 2, 3, 4, 5, 6, 7, 8, 9}
1{-, 4, 0, 0, 0, 0, 0, 8, 0},
2{4, -, 8, 0, 0, 0, 0, 11, 0},
3{0, 8, -, 7, 0, 4, 0, 0, 2},
4{0, 0, 7, -, 9, 14, 0, 0, 0},
5{0, 0, 0, 9, -, 10, 0, 0, 0},
6{0, 0, 4, 14, 10, -, 2, 0, 0},
7{0, 0, 0, 0, 0, 2, -, 1, 6},
8{8, 11, 0, 0, 0, 0, 1, -, 7},
9{0, 0, 2, 0, 0, 0, 6, 7, -}
'''

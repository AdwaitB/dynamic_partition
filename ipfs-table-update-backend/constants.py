from enum import Enum

NODE_CUSTOM_PORT = '12000'

DEFAULT_IP = "0.0.0.0"
DEFAULT_NODE_NAME = "NODE"
DEFAULT_VERSION = -1
DEFAULT_ALIAS = "ALIAS"

DEFAULT_ENTRY = (DEFAULT_IP, DEFAULT_VERSION)

LOCALHOST = "127.0.0.1"

IP = 'ip'
TYPE = 'type'
SUBTYPE = 'subtype'

TS = 'timestamp'
FH = 'file_hash'
FSIP = 'file_src_ip'

HTTP_TIMEOUT = 3600  # (seconds)
SEED = 111
N_JOBS = 20000
MAX_CACHE_SIZE = 60
N_THREADS = 100
do_async = False


class ControlType(Enum):
	FILE_REQUEST = 0
	FILE_ADD = 1
	FILE_DELETE = 2


class RequestType(Enum):
	DHT = 0  # DHT request
	INSERT = 1  # Add a new object to the node
	ADD = 2  # ADD message
	REMOVE = 3  # Remove an object from the node
	DELETE = 4  # DEL message
	CONTROL = 5  # Used for control messages
	DOWNLOAD = 6  # Download file
	JOB = 7  # Search and download file


class RequestSubtype(Enum):
	INIT = 0  # Initialization
	FILE = 1  # File generation (Rename from copied)
	WRITE_TRACE = 2  # Things to do after the experiments are over
	FINALIZE = 3 # Wait for all the data update processes to complete


class RequestAdd(Enum):
	# Remote entry
	add_id = 1
	entry_ip = 2
	entry_clock = 3


class Entries(Enum):
	INSERT_ENTRIES = 0
	ADD_ENTRIES = 1
	REMOVE_ENTRIES = 2
	DELETE_ENTRIES = 3
	CONTROL_ENTRIES = 4


class RequestDel(Enum):
	remove_src_ip = 2
	remove_src_clock = 3
	sender_ip = 4
	sender_entry_ip = 5
	sender_entry_clock = 6


#FILE_SIZES = (1, 16, 64, 128, 256, 2048, 8192, 16384, 32768)
FILE_SIZES = (1, 32, 64, 256, 512, 1024, 2048, 16384, 32768)

CONFIG_FOLDER = "/root/deploy/backend/"
FILE_FOLDER = "/root/deploy/files/"
TRACES_FOLDER = "/root/deploy/traces/"
FILE_CACHE = "/root/deploy/files-cache/"

# Values in ms, time between jobs = a + rand(0, b)
JOB_GENERATION_A = 50
JOB_GENERATION_B = 50

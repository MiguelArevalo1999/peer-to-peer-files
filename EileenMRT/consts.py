MAX_INT = 2147483647  # largest positve integer

PACK_FMT="iiiii"    # pack format for connId, checksum, type, fragNum, winAdv, final_flag

# Packet type
#       RCON - request connection
#       ACON - acknowledge connection
#       DATA - send data
#       ADAT - acknowledge data
#       RCLS - request close connection
#       ACLS - acknowledge close
#       RSND - resend last packet
RCON = 1
ACON = 2
DATA = 3
ADAT = 4
RCLS = 5
ACLS = 6
RSND = 7


BUFSIZE = 4096      # 4KB
CHUNK_SIZE = 3072   # 3KB

WINDOW_SIZE = 10

# if a packet doesn't get an acknowledgement in this time frame 
# resend this packet
# in milli-seconds
RETRY_TIMEOUT = 10000

DUMP_SIZE_THRESHOLD = 10240 # 10KB
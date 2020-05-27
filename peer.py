"""
A file that defines the peer client we will use.
"""


class Peer:

    def __init__(self, identifier):
        self.identify = identifier  # Will be constructed with an identifier.
        self.upstream = None
        self.downstream = None
        self.filesAvailable = list()
        self.myFiles = list()

    # Used for setting Linked list upstream neighbor.
    def setUpstream(self, upstream_neighbor):
        self.upstream = upstream_neighbor

    # Setting Linked List downstream neighbor
    def setDownstream(self, downstream_neighbor):
        self.downstream = downstream_neighbor

    # Set the Internal Files this Peer can share.
    def set_my_files(self, my_files):
        self.myFiles = my_files

    # Adds a file to the Internal Sendable files (likely used when downloading a file from elsewhere)
    def append_my_files(self, file):
        self.myFiles.append(file)

    # When adding a new node, this is used to set the possible files we can download.
    def set_available_files(self, available_files):
        self.filesAvailable = available_files

    # If we want to add one.
    def append_one_available_files(self, new_file):
        self.filesAvailable.append(new_file)

    # If we want to add a group of them.
    def append_group_available_files(self, group_files):
        for file in group_files:
            self.append_one_available_files(file)

    # If we want to remove a file (For example, when a node disconnects)
    def remove_one_available_file(self, file):
        self.filesAvailable.remove(file)

    # If we want to remove a group of files (when a node disconnects)
    def remove_group_available_files(self, group_files):
        for file in group_files:
            self.remove_one_available_file(file)

    # Getter for the upstream. If used over and over would return the whole upstream linked list.
    def getUpstream(self):
        return self.upstream

    # Getter for downstream. If used in loop would return all downstream peers.
    def getDownstream(self):
        return self.downstream

# Testing some of the class.
Anjer = Peer("0001")

# Initializing the first node.
Anjer.append_my_files("first.txt")
Anjer.append_one_available_files("first.txt")
Anjer.append_my_files("second.txt")
Anjer.append_one_available_files("second.txt")

# Second node in network.
Shane = Peer("0002")

# Linked List functionality.
Anjer.setDownstream(Shane)
Shane.setUpstream(Anjer)

# Gets the upstream files Anjer has global access to and adds them to the internal files in Shane.
Shane.append_group_available_files(Shane.getUpstream().myFiles)

# Makes sure that the functions are working.
print("Test 1: Transferring Anjer's global files to my personal files: ", Shane.filesAvailable)

if Shane.filesAvailable == Anjer.filesAvailable:
    print("PASSED")



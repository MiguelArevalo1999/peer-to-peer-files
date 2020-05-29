from Node import Node

node = Node()
node.node_open('127.0.0.1', 8082)
node.node_connect('127.0.0.1', 8080)
node.node_broadcast('test_directory')
print(node.neighbors)

import threading, time
from queue import Queue
from mq_producer import Producer
from mq_consumer import Consumer

def main():
    queue = Queue()
    producer = Producer('Pro', queue)
    consumer = Consumer('Con', queue)
    producer.start()
    consumer.start()
    producer.join()
    consumer.join()
    print('All threads terminate!')

if __name__ == '__main__':
    main()
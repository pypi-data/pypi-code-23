class Sender:
    def __init__(self,rabbit_instance,queue_name,exchange_name=None):
        self.rabbit = rabbit_instance
        if self.rabbit.check_connection() == False:
            print(' [*] Connection is closed. Reopening connection...')
            self.rabbit.connect()

        self.exchange_name = exchange_name #direct default
        self.queue_name = queue_name
        self.channel = self.rabbit.channel()
        if exchange_name is not None:
            self.rabbit.exchange(self.channel,exchange_name,"direct")
        #da eliminare
        list_exchange = ["controller","news","parser_error","reccomender","rss","rss_error","teacher","watcher"]
        for ex in list_exchange:
            self.rabbit.exchange(self.channel, ex, "direct")

        self.queue = self.rabbit.queue(self.channel,queue_name)

    def bind(self,exchange_name,binding_key):
        self.exchange_name = exchange_name
        self.rabbit.queue_bind(self.channel,exchange_name,self.queue,binding_key)

    def publish(self,routing_key,body,delivery_mode=2):
        self.rabbit.publish(self.channel,self.exchange_name,routing_key,body,delivery_mode=delivery_mode)

    def exchange(self,exchange_name,exchange_type):
        self.rabbit.exchange(self.channel,exchange_name,exchange_type)


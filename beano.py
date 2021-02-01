from collections import defaultdict
from mongo_manager import MONGO_CONNECTION_STRING
import pymongo
from pymongo.mongo_client import MongoClient
from datetime import datetime
class Beano:

    hunger      = 0
    thirst      = 0
    energy      = 0
    affection   = 0
    age         = 0
    pat_cooldown = 60
    MONGO_CONNECTION_STRING = 'mongodb+srv://wlogga:j8w6AhB5LjAeQGU@cluster0.sxzam.mongodb.net/test'
    
    def __init__(self):
        pass
    
    def get_update_json(self):
        update_json = {
                        "hunger":0,
                        "thirst":0,
                        "energy":0,
                        "affection":0,
                        "date_created":0,
                        "name":"Beano"
        }

        return update_json

    def get_user_json(self):
        json = {
                    "user_id":0,
                    "last_pat_timestamp":0,
                    "beano_coin_count" : 0,
                    "inventory" : []
                }

    def create_new_user(self,user_id):
        json = {
                    "user_id":user_id,
                    "last_pat_timestamp":datetime.min,
                    "beano_coin_count" : 0,
                    "inventory" : []
                }
        mongo = MongoClient(MONGO_CONNECTION_STRING)
        response = mongo.beanbot.users.insert_one(json)
        print(response)

    def pat_beano(self,user_id):
        print("Patting Beano")
        current_timestamp = datetime.now()
        response = ("idle","There was some issue. Beano is confused.")
        mongo = MongoClient(MONGO_CONNECTION_STRING)

        user_stats = mongo.beanbot.users.find_one({'user_id':user_id})

        
        if user_stats is None:
            print("{} not in mongo. Adding to mongo.".format(user_id))
            self.create_new_user(user_id)
            user_stats = mongo.beanbot.users.find_one({'user_id':user_id})

        print("User Stats : ",user_stats)

        last_pat_ts = user_stats['last_pat_timestamp']
        pat_cd = (current_timestamp - last_pat_ts).total_seconds() / 60

        print(pat_cd," VS ",self.pat_cooldown)

        if pat_cd < self.pat_cooldown:
            response = ("idle","You cannot pat Beano for another {} minutes.".format(self.pat_cooldown - pat_cd))
        else: 
            mongo.beanbot.users.update_one({'user_id':user_id},{"$set":{"last_pat_timestamp":current_timestamp}},upsert=True)
            response = ("happy","You pat Beano!")
        
        mongo.close()

        return response

    def get_user_coins(self,user_id):

        print("Pulling Coin Amount for ",user_id)
        mongo = MongoClient(MONGO_CONNECTION_STRING)
        stats = defaultdict(int,mongo.beanbot.users.find_one({"user_id":user_id}))
        mongo.close()
        return stats['beano_coin_count']

    def give_user_coins(self,user_id,coin_amount):

        print("Giving {} coins to {}".format(coin_amount,user_id))
        mongo = MongoClient(MONGO_CONNECTION_STRING)
        mongo.beanbot.users.update_one({'user_id':user_id},{"$inc":{"beano_coin_count":1}},upsert=True)
        mongo.close()
        return None

    def get_beano_stats(self):

        print("Pulling Stats from Mongo")
        mongo = MongoClient(MONGO_CONNECTION_STRING)
        stats = defaultdict(int,mongo.beanbot.beano_data.find_one())
        mongo.close()
        print(stats)
        return stats

    def update_beano_stats(self,update_json):
        
        print("Pulling Stats from Mongo")
        mongo = MongoClient(MONGO_CONNECTION_STRING)
        stats = mongo.beanbot.beano_data.insert(update_json)
        mongo.close()
        print(stats)
        return stats

    def get_store_inventory(self):
        mongo = MongoClient(MONGO_CONNECTION_STRING)
        response = mongo.beanbot.store_items.find({"active":True}).sort("item_id")
        mongo.close()
        return response
    
    def get_item_info(self,item_id):
            mongo = MongoClient(MONGO_CONNECTION_STRING)
            print("Pulling info for Item ID", item_id)
            response = mongo.beanbot.store_items.find_one({"active":True,"item_id":int(item_id)})
            mongo.close()
            return response

    def buy_item_from_store(self,user_id,item_id):
        
        item_info = self.get_item_info(item_id)

        if item_info is None:
            return f"There is no item found for item id {item_id}"

        print("Item info ",item_info)
        user_coins = self.get_user_coins(user_id)
        print("User Coins", user_coins)
        item_cost = item_info['cost']


        if user_coins >= item_cost:
            mongo = MongoClient(MONGO_CONNECTION_STRING)
            mongo.beanbot.users.update_one({'user_id':user_id},{"$inc":{"beano_coin_count":-item_cost}},upsert=True)
            self.give_item_to_player(item_info,user_id)
            mongo.close()
            return f"You purchased a {item_info['name']}. You have {user_coins - item_cost } BC remaining!"
        else:
            return f"You do not have enough coins to purchase this time.  It costs {item_cost} and you have {user_coins}."
        

    def use_item(self,user_id,item_id):
        print(user_id, item_id)

        return "This command is not complete yet.  Beano apologizes and will try harder tomorrow."

    def give_item_to_player(self,item,user_id):
        mongo = MongoClient(MONGO_CONNECTION_STRING)
        mongo.beanbot.users.update_one({'user_id':user_id},{"$push":{"inventory":{"id":item['item_id'],"name":item['name'],"effect":item['effect'],"description":item['description']}}},upsert=True)
        mongo.close()
        print("Gave {} to {}".format(item['item_id'],user_id))

    def get_player_stats(self,user_id):
        mongo = MongoClient(MONGO_CONNECTION_STRING)
        stats = mongo.beanbot.users.find_one({"user_id":user_id})
        mongo.close()

        return stats
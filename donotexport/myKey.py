import random

class MyKey():
    def __init__(self):
        self.keys = ['M3AVG22OXELHTROF',
                     '9J06ND1RN37ROG4Y',
                     '2UE755N80C9RRTX6',
                     '57QKMOA04YF34V8W',
                     'HEQ1BXG9I3RKCQYU',
                     'LAZ7CKRMKI755YX2'
                     ]

    def returnKey(self):
        return random.choice(self.keys)

import simpy
import random

class Laundary():
    def __init__(self,env):
        print("Laundary initiated")
        self.env=env
        self.action=env.process(self.start())
    
    def start(self):
        while True:
            print("started washing at %d" % env.now)
            washing_duration = 2
            try:
                yield self.env.timeout(washing_duration)
            except simpy.Interrupt:
                print("Interrupted at washing")

            print("started drying at %d" % env.now)
            dry_duration = 2
            try:
                yield self.env.timeout(dry_duration)
                print("Time to clean the washer. Loading..............")
                yield self.env.process(self.clean())
            except simpy.Interrupt:
                print("Interrupted at dry and clean")

    def clean(self):
        yield self.env.timeout(2)


def manual(env, Laundary):
    yield env.timeout(3)
    Laundary.action.interrupt()

env= simpy.Environment()
laundary = Laundary(env)
env.process(manual(env,laundary))
env.run(until=20)
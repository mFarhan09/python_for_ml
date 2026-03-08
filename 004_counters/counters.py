#counter simply  keeps a counter to string or char or whatever
#counter = dictionary that automatically counts
from collections import Counter
from dataclasses import dataclass

#for this particular example we  are keeping a counter on banana , which stores how many times a would appear, and how many times b and n would  appear.
text = "banana"
c  = Counter(text)
print(c)



#exmple two
print("")
text2 = "how are you how was your day and what are you doing now"
words = text2.split()
c2 = Counter(words)
print(c2)



#example 3
nums = [1,1,1,1,1,2,2,3,4,4,4,4]
c3 = Counter(nums)
print(c3.most_common(2))



@dataclass
class Stats:
    errors: Counter = Counter()
    #this looks fine but is dangrous , because every object is going to share same counter

a = Stats()
b = Stats()
a.errors["timeout"] += 1
print(b.errors)
#compiler is not even allow it to run , knowing how dangrous of a bug this is 



#solution: python gives us default_factory  from dataclass module
#it calls c= counter() every time a new object is created 

from dataclasses import dataclass, field
from collections import Counter

@dataclass
class Stats:
    errors: Counter = field(default_factory=Counter)

a = Stats()
b = Stats()

a.errors["timeout"] += 1

print(a.errors)
print(b.errors)

# equivalent to 
# class Stats:
#     def __init__(self):
#         self.errors = Counter()

#field() tells a dataclass how to create or configure a variable inside the class.
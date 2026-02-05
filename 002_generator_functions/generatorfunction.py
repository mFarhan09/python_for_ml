
"""
A generator is a special kind of iterator that yields values one at a time, instead of returning them all at once.
This is memory efficient for large datasets because it does not store everything in memory.
Generators are defined like a normal function but use the yield keyword instead of return
"""
from typing import Generator


def simpleGenerator():
    print ("start")
    yield 1
    print ("middle")
    yield 2
    print ("end")
    yield 3



gen = simpleGenerator()

print(next(gen))
print(next(gen))
print(next(gen))

#or you can also do
for i in simpleGenerator(): # generates the same output
    print(i)

#lazy evaluation : compute values only when needed.
#generate numbers from 1 to 5 
def number():
    for i in range(1,5):
        yield i


print("")
for n in number():
    print(n)


print("")
gen = number()
for i in range(1,5):
    print(next(gen))



#infinite number generator

def infiniteGenerator():
    n =1 
    while True:
        yield n
        n +=1


count = 1
print("")
for i in infiniteGenerator():
    print(i)
    count +=1
    if count > 5 :
        break



gen = infiniteGenerator()
print("")
print(next(gen))
print(next(gen))
print(next(gen))



# enumerate inside  a generator
print("")


def squares(nums):
    for i, x in enumerate(nums):
        yield i , x*x


for index , num in enumerate([1,3,4]):
    print(index,num)



#generator expressions
print("")

genExp = (x*x for x in range(5))

print(next(genExp)) #zero
print(next(genExp)) #1
print(next(genExp)) #4 

#a normal generator function takes normal arguments like any other function 
# presence of yield makes it a generator ,the typing.generator is just there for us to understand what this generator is doing ,that is why its called type hints , and it gets ignore at runtime, code works the same if we remove it



def typinggenerator(n) -> Generator[int,int,str]:
     x = yield n
     yield  x 
     return "Done"

print("")
gen = typinggenerator(2)
print(next(gen))
print(gen.send(15))

try:
    next(gen)
except StopIteration as e:
    print(e.value)


#now try without type hint

def increment(n,limit):  
    while n < limit:
        n +=1
        yield n+1
    

print("")
for i in increment(5,15):
    print(i)
    


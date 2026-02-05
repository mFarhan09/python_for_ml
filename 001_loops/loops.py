
#basic loop 

books = [" book 1" , " book 2 ", " book 3" , " book 4"]
for book in books:
    print(book)



#adding counter 
print("")
count = 1 
for book in books:
    print(count,book)
    count +=1



#using enuerate function to count
print("")
for count , book in enumerate(books):
    print(count,book)



#now lets make count start from 1
print("")
for count, book in enumerate(books, start = 1):
    print(count,book)
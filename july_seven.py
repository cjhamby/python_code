# july 7 challenge
#
# code by chris hamby
#
# implement functions car(pair) and cdr(pair)
# 
# car(pair) returns the first element in the pair
# cdr(pair) returns the last element in the pair
#
# example usage: car(cons(1,2)) -> 1
#

# given code -------------
def cons(a,b):
    def pair(f):
        return f(a,b)
    return pair
# end of given code-------

# -----------------------------------------------------------------
# solution
# -----------------------------------------------------------------
def first_item(x, y):
    return x

def last_item(x, y):
    return y

def car(f):
    return f(first_item)

def cdr(f):
    return f(last_item)

# the output should be "5" then "6"
print(car(cons(5,6)))
print(cdr(cons(5,6)))


# -----------------------------------------------------------------
# explanation
# -----------------------------------------------------------------
# the given code has an example of a closure function... what that mean?
# the function CONS returns the PAIR function
# the only way to understand is with an example
#

var = cons(1, 2)

# var is now a version of the function "pair(f)" with a,b values equivalent to:
#
# def pair(f):
#     return f(1, 2)

var2 = var(min)

# var2 calls the var function, in the following way:
#
# var2 = var(min) = min(1,2)
#
# yes it is weird to use function names (MIN) as arguments
# my brain hurts a little
def get_even_numbers(lst):
    even = []
    for item in lst :
        if item%2 ==0:
            even.append(item)
    return sum(even)

print(get_even_numbers([1,2,3,4]))
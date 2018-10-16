from cs50 import get_int
import sys


while True:
    height = get_int("Enter height: ")
    if height < 0 or height > 23:
        continue
    break

h = height - 1

for x in range(height):
    for j in range(h):
        print(" ", end='')
    for k in range(x):
        print("#", end='')
    h = h - 1
    print("##")

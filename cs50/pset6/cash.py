from cs50 import get_float
import sys

while True:
    c = get_float("Enter change: ")
    if c > 0:
        break

change = c * 100
coins = 0

while change >= 25:
    change -= 25
    coins += 1

while change < 25 and change >= 10:
    change -= 10
    coins += 1

while change < 10 and change >= 5:
    change -= 5
    coins += 1

while change < 5 and change >= 1:
    change -= 1
    coins += 1

print(coins)

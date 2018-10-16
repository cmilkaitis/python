from cs50 import get_string
import sys

if len(sys.argv) != 2:
    print("Please enter an argument")
    sys.exit(1)

k = int(sys.argv[1])

plainText = get_string("plaintext: ")
print("ciphertext: ", end='')

for letter in plainText:
    c = ord(letter)
    if c >= 65 and c <= 122:
        if letter == letter.upper():
            c -= 65
            c = ((c + k) % 26) + 65
            print(chr(c), end='')
        else:
            c -= 97
            c = ((c + k) % 26) + 97
            print(chr(c), end='')
    else:
        print(letter, end='')

print()
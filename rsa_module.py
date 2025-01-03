import random
import math

def is_prime(number):
    if number <= 1:
        return False
    for i in range(2, int(math.sqrt(number)) + 1):
        if number % i == 0:
            return False
    return True

def generate_prime(min_value, max_value):
    while True:
        prime = random.randint(min_value, max_value)
        if is_prime(prime):
            return prime

def mod_inverse(e, phi):
    def egcd(a, b):
        if a == 0:
            return b, 0, 1
        g, x, y = egcd(b % a, a)
        return g, y - (b // a) * x, x

    g, x, _ = egcd(e, phi)
    if g != 1:
        raise ValueError("Mod_inverse does not exist!")
    return x % phi

def generate_keys():
    p = generate_prime(1000, 50000)
    q = generate_prime(1000, 50000)
    while p == q:
        q = generate_prime(1000, 50000)

    n = p * q
    phi_n = (p - 1) * (q - 1)

    e = random.randint(3, phi_n - 1)
    while math.gcd(e, phi_n) != 1:
        e = random.randint(3, phi_n - 1)

    d = mod_inverse(e, phi_n)
    return e, d, n

def encrypt(message, public_key, n):
    if isinstance(message, bytes):
        message = message.decode()
    return [pow(ord(ch), public_key, n) for ch in message]

def decrypt(ciphertext, private_key, n):
    decrypted_chars = []
    for ch in ciphertext:
        decrypted_value = pow(ch, private_key, n)
        if 0 <= decrypted_value <= 0x10FFFF:
            decrypted_chars.append(chr(decrypted_value))
        else:
            return "Invalid message."
    return ''.join(decrypted_chars)

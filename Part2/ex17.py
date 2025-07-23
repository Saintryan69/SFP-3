import random

# 3. Lists of adjectives and animals (each with 6 items)
adjectives = ["Tall", "Young", "Rich", "Handsome", "Fine", "Nonchalant"]
animals = ["Anteater", "Panther", "Otter", "Tiger", "Wolf", "Doggy"]

# 1. Ask user for their name
name = input("What is your name? ")

# 5. Randomly select one adjective and one animal for the codename
codename = random.choice(adjectives) + " " + random.choice(animals)

# 6. Randomly select a lucky number between 1 and 99
lucky_number = random.randint(1, 99)

# 7. Print the final message
print(f"{name}, your codename is: {codename}")
print(f"Your lucky number is: {lucky_number}")
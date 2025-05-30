bad_words = []
with open('words.txt', 'r') as file:
    for line in file:
        bad_words.append(line.strip())


sites = ["cnbc", "bbc", "reuters", "coindesk", "cointelegraph", "cryptoslate"]
number = int(input("Choose a site \n 1. cnbc \n 2. bbc \n 3. reuters \n 4. coindesk \n 5. cointelegraph \n 6. cryptoslate \n 7. traditional \n 8. crypto \n 9. all \n: "))

while number > 9:
    number = int(input("Choose a site \n 1. cnbc \n 2. bbc \n 3. reuters \n 4. coindesk \n 5. cointelegraph \n 6. cryptoslate \n 7. traditional \n 8. crypto \n 9. all \n: "))


if number < 7:
    with open(f'/Users/s/Desktop/Study/Toyproject/Newsquids/Backend/crawler/files/{sites[number-1]}/links.txt', 'r') as f:
        x = f.read()
    x = eval(x)
    d_keys = list(x.keys())
    print(len(d_keys))
elif number == 7:
    key_number = 0
    for n in range(3):
        with open(f'/Users/s/Desktop/Study/Toyproject/Newsquids/Backend/crawler/files/{sites[n]}/links.txt', 'r') as f:
            x = f.read()
        x = eval(x)
        d_keys = list(x.keys())
        key_number += len(d_keys)
    print(key_number)
elif number == 8:
    key_number = 0
    for n in range(3,6):
        with open(f'/Users/s/Desktop/Study/Toyproject/Newsquids/Backend/crawler/files/{sites[n]}/links.txt', 'r') as f:
            x = f.read()
        x = eval(x)
        d_keys = list(x.keys())
        key_number += len(d_keys)
    print(key_number)
elif number == 9:
    key_number = 0
    for n in range(6):
        with open(f'/Users/s/Desktop/Study/Toyproject/Newsquids/Backend/crawler/files/{sites[n]}/links.txt', 'r') as f:
            x = f.read()
        x = eval(x)
        d_keys = list(x.keys())
        key_number += len(d_keys)
    print(key_number)
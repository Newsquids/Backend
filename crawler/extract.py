sites = ["cnbc", "bbc", "reuters", "coindesk", "cointelegraph", "cryptoslate"]
number = int(input("Choose a site \n 1. cnbc \n 2. bbc \n 3. reuters \n 4. coindesk \n 5. cointelegraph \n 6. cryptoslate \n : "))
while number > 6:
    number = int(input("Choose a site \n 1. cnbc \n 2. bbc \n 3. reuters \n 4. coindesk \n 5. cointelegraph \n 6. cryptoslate \n : "))
with open(f'/Users/s/Desktop/Study/Toyproject/Newsquids/Backend/crawler/files/{sites[number-1]}/links.txt', 'r') as f:
    x = f.read()

data = eval(x)
data_keys = list(data.keys())
tem_key = data_keys[5]
# print(data[tem_key][0])
# print(data[tem_key][1])
# print(data[tem_key][2])
ml = 0
for key in data_keys:
    tem = data[key][0]
    if tem != None:
        if ml < len(tem):
            ml = len(tem)
        if len(tem) < 10:
            print(tem)
            print(key)

print(ml)
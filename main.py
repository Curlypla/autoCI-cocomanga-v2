from curl_cffi import requests
import os, re, json

headers = {
    'origin': 'https://www.colamanga.com',
    'referer': 'https://www.colamanga.com/manga-hy703661/1/330.html',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
}

mangareadjs = requests.get('https://www.colamanga.com/js/manga.read.js', headers=headers).text
customjs = requests.get('https://www.colamanga.com/js/custom.js', headers=headers).text

with open("mangaread.js", "w", encoding="utf-8") as f:
    f.write(mangareadjs)

with open("custom.js", "w", encoding="utf-8") as f:
    f.write(customjs)

# run obfuscator-io-deobfuscator <input> -o [output]
os.system("obfuscator-io-deobfuscator mangaread.js -o mangaread-deob.js")
os.system("obfuscator-io-deobfuscator custom.js -o custom-deob.js")

decryption_dico = {}

with open("mangaread-deob.js", "r", encoding="utf-8") as f:
    mangaread = f.read()

with open("custom-deob.js", "r", encoding="utf-8") as f:
    custom = f.read()

keys_list = re.findall(r'\"(.*?)\"', custom)
bad_chars = ["?", "<", "_", ":", ".", "：", "getCroppedCanvas"]
keys_list = [x for x in keys_list if len(x) == 16 and not any(c in x for c in bad_chars)]
keys_list = list(dict.fromkeys(keys_list))
print(keys_list)

decryption_dico["C_DATA"] = [keys_list[0], keys_list[1]]
decryption_dico["enc_code2"] = [keys_list[2], keys_list[3]]
decryption_dico["enc_code1"] = [keys_list[4], keys_list[5]]

# decryption_dico["C_DATA"] = [keys_list[-1], keys_list[5]]
# decryption_dico["enc_code2"] = [keys_list[1], keys_list[0]]
# decryption_dico["enc_code1"] = [keys_list[2], keys_list[3]]

pattern = r'if \(G == "(\d+)"\) {\s*I = "([^"]+)";'
matches = re.findall(pattern, mangaread)
result = dict(matches)

decryption_dico["IG_dict"] = result

json.dump(decryption_dico, open("keys.json", "w", encoding="utf-8"))

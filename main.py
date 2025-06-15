from curl_cffi import requests
import os, re, json

headers = {
    'origin': 'https://www.colamanga.com',
    'referer': 'https://www.colamanga.com/manga-hy703661/1/330.html',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
}

mangareadjs = requests.get('https://www.colamanga.com/js/manga.read.js', headers=headers).text
customjs = requests.get('https://www.colamanga.com/js/custom.js', headers=headers).text
urldata = "https://raw.githubusercontent.com/Curlypla/autoCI-cocomanga-v2/refs/heads/main/keys.json"
data = requests.get(urldata).json()

with open("mangaread.js", "w", encoding="utf-8") as f:
    f.write(mangareadjs)

with open("custom.js", "w", encoding="utf-8") as f:
    f.write(customjs)

# # run obfuscator-io-deobfuscator <input> -o [output]
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

def get_content_beetween_two_strings(content, start, end):
    return content.split(start)[1].split(end)[0]

str1 = "'' && "
str2 = "};"

# Now more dynamic, do not depends on variable name
content = get_content_beetween_two_strings(mangaread, str1, str2)
pattern = r'0x[0-9a-fA-F]+(?=\))'
matches1 = re.findall(pattern, content)
matches1.pop(0)
pattern = r'\"([^"]+)\"'
matches2 = re.findall(pattern, content)

result = {int(value, 16): key for key, value in zip(matches2, matches1)}

decryption_dico["IG_dict"] = result
igdico = decryption_dico["IG_dict"]

js_cr_init = """
window.__cr = {
  timeout: 10000,
  imageisLoading: 0,
  imgKeyIsLoading: true,
  isfromMangaRead: null,
  isloading: 0,
  preloader: [undefined, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}],
  si_lazyload: 3,
  st_showerr: [undefined, 4, 7, 45, 46, 51, 54, 55, 56, 57, 68],
  thispage: 1,
  userReadMode: 3,
  
  PrefixInteger: function(_0x1f6eb5, _0x3fdd9b) {
  },
  
  bindEvent: function() {
  },
  
  charcode: function(_0x267850) {
  },
  
  cookie: function(_0x2b70d0, _0xb1a60d, _0x3cc32a) {
  },
  
  frameImagebind: function(_0x30c3d2, _0x4d7657) {
  },
  
  getLine: function() {
  },
  
  getPage: function() {
  },
  
  getPicUrl: function(_0x488dde) {
  },
  
  goPage: function(_0x49d8e5) {
  },
  
  imgDrag: function(_0x37f797, _0x2eba3b) {
  },
  
  imgOnError: function(_0x355957, _0x5f0bdf) {
  },
  
  imgOnLoad: function(_0x41b05c) {
  },
  
  imgOnTouch: function() {
  },
  
  init: function() {
  },
  
  initpager: function(_0xc524d) {
  },
  
  isLimit: function() {
  },
  
  isSupportWebp: function() {
  },
  
  lazyLoad: function() {
  },
  
  preLoadImg: function(_0x24e91c) {
  },
  
  reloadPic: function(_0x19ff5b, _0x35bb3e) {
  },
  
  saveLine: function(_0x5e7fb9) {
  },
  
  setLine: function(_0x52396f) {
  },
  
  setRecord: function() {
  },
  
  showPic: function(_0x275bd9) {
  },
  
  switchWebp: function(_0x168390, _0x423a95) {
  }
};
""";

fullcodejs = open("full.js", "r").read()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://colamanga.com/") 
    page.evaluate(js_cr_init)
    page.evaluate(f"var actualKey = 'random';")
    page.evaluate(fullcodejs)
    
    for index, encryptedKey in igdico.items():
        page.evaluate(f"var actualKey = '{encryptedKey}';")
        page.evaluate("window.deeee()")
        actualKey = page.evaluate("window.actualKey")
        print(f"Key {index}: {actualKey}")
        decryption_dico["IG_dict"][index] = actualKey
    browser.close()

decryption_dico["IG_dict"] = igdico


json.dump(decryption_dico, open("keys.json", "w", encoding="utf-8"))

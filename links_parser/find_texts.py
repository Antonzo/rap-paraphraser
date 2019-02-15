import requests 
import re
def gentxturls():
    filepages = open('textpages.txt')
    filetexts = open('filetexts.txt', 'w')
    filetexts.close()
    filetexts = open('filetexts.txt', 'a')
    pattern = re.compile(r"href='(.+)'\><span>Читать")
    for line in filepages:
        adress = line[:len(line)-1]
        response = requests.get(adress)
        htmlcode = response.content.decode('utf-8', errors = 'ignore')
        result = pattern.findall(htmlcode)
        for textadress in result:
            filetexts.write(textadress+'\n')   
    filetexts.close()
    filepages.close()
    print('end of work')
gentxturls()
def genarr():
    a = ['https://xn----jtbpreked6g.xn--p1ai/category/teksty-pesen/']
    for i in range(2,1021):
        a.append('https://xn----jtbpreked6g.xn--p1ai/category/teksty-pesen/page/' + str(i) + '/')
    return a

def genpages():
    try:
        file = open('textpages.txt', 'w')
        for url in genarr():
            file.write(url + '\n')
        file.close()
        return 0
    except Exception:
        return 1
    print('end of work')
        
        
    
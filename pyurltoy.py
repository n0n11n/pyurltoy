from pyquery import PyQuery as d
import requests, re

headers = {

        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0',
        'Accept': '*/*',
        'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        #'Referer': 'http://www.wikipedia.com',
    }

s = requests.Session()

palias = {'href' : 'a[href]@href' ,
         'imga' : 'img[src]@src' }

alias = {'undo' : ['back'] ,
         'ls' : ['list'] ,
         'end' : ['exit','quit'] ,
         'remove' : ['del','rem'] ,
         'keep' : ['filter'],
         'uniq' : ['nodupes','uni','uniqe','unique'] ,
         'repl' : ['rep','replace'] ,
         'requery' : ['regex','reg'] ,
         'query' : ['pq','css','jq'] }


def fread(fn):
  with open(fn) as fh:
      txt = fh.read()
  return txt

def fwrite(fn,txt,m='w+'):
  with open(fn,m) as fh:
      fh.write(txt.encode('utf-8'))
  return (txt, fn)

def query(inp,*pattern):
    #inp = 'https://en.wikipedia.org/wiki/Austrian_cuisine'
    
    pattern = ' '.join(pattern)
    print (inp,pattern)    
    
    if inp.find('http') == 0:
        url = inp
        r = s.get(url, headers=headers)
        document = d(r.content).make_links_absolute(url)
    else:
        document = d(inp)
        
    if pattern in palias:
        pattern = palias[pattern]
    
    if pattern.find('@') > -1 :
        jq,attr = pattern.split('@')    
        ele = document(jq)
        #ele.text()? @text?
        return [u.attrib[attr] for u in ele]
    else:
        jq = pattern
        return [d(e).outer_html() for e in document(jq)]
        
def requery(inp,*pattern):
    pattern = ' '.join(pattern)
    print (inp,pattern)    
    
    if inp.find('http') == 0:
        url = inp
        r = s.get(url, headers=headers)
        document = r.content
    else:
        document = inp
    return re.findall(pattern,document)
        
def calias(inp):
    ret =  [m[0] for m in alias.iteritems() if inp in m[1]]
    if len(ret) == 1:
        return ret[0]
    else:
        return inp
        

class worker(object):
    def __init__(self):
        self.stack = []
            
    def __call__(self,*args):
        inp = calias(args[0])
        
        if not inp in ['undo','ls','add','save']:
            self.history = self.stack
        if inp in dir(self):
            #add alias dict
            return getattr(self,inp)(*args[1:])
        elif inp.find('http') == 0:
            self.stack += [inp]
            return True
        else:
            print 'wrong input', inp
            print 'ok input:' , dir(self)
            return True
    
    def end(self):
        print 'CU'
        return False
        
    def undo(self):
        hist = self.stack
        self.stack = self.history
        self.history = hist
        return True
    
    def add(self):
        hist = self.stack
        self.stack = self.history + self.stack
        self.history = hist
        return True
    
    def save(self,*args):
        fname = ' '.join(args)
        fwrite(fname,"\n".join(self.stack))
        return True

    def load(self,*args):
        fname = ' '.join(args)
        txt = fread(fname)
        self.stack = txt.split("\n")
        return True
    
    def query(self,*args):
        out = []
        for u in self.stack:
            out += query( u,*args )
        self.stack = out
        return True

    def requery(self,*args):
        out = []
        for u in self.stack:
            out += requery( u,*args )
        self.stack = out
        return True
        
    def keep(self,*filt):
        out = []
        for f in filt:
            out += [u for u in self.stack if f in u]
        self.stack = out
        return True
        
    def rekeep(self,*filt):
        out = []
        for f in filt:
            out += [u for u in self.stack if re.search(f,u)]
        self.stack = out
        return True
        
    def remove(self,filt):
        self.stack = [u for u in self.stack if not filt in u]
        return True
        
    def ls(self,end=None,start=None):
        if end:
            end = int(end)
        if start:
            start = int(start)
            
        print self.stack[start:end]
        return True
        
    def trim(self,start=None,end=None):
        if end:
            end = int(end)
        if start:
            start = int(start)
            
        self.stack = self.stack[start:end]
        return True
        
    def uniq(self):
        self.stack = list(set(self.stack))
        return True
        
    def repl(self,old,new):
        self.stack = [re.sub(old,new,u) for u in self.stack]
        return True
        
    def fusk(self,inp):
        patterns = [[inp]]
        ranges = re.findall(r'\[\d+\-\d+\]', inp)
        j = -1
        
        for r in ranges:
            j += 1
            s = r.split('-')
            start = s[0][1:]
            stop = s[1][:-1]
            patterns += [[]]
            
            for pattern in patterns[j]:
                ##print pattern
                p = pattern.split(r)
                if len(p) == 1:
                    break
                patterns[j+1] += [p[0]+ str(i).zfill(len(start)) +p[1] for i in range(int(start),int(stop)+1)]
                    
        self.stack = patterns[-1]
        return True
        
        
        
        
run = True
toy = worker()

while(run):
    ## https://en.wikipedia.org/wiki/Austrian_cuisine
    ## query href
    inp = raw_input(str(len(toy.stack))+'>').split(' ')
    try:
        run = toy( *inp )
    except Exception as e:
        print e
    

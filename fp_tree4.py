from tkinter import *

class Node:
    no = 0

    def __init__(self, isim, seviye):
        self.isim = isim
        self.adet = 1

        self.ana = None
        self.cocuklar = []

        self.no = Node.no
        Node.no += 1

        self.seviye = seviye
        self.kolon = 0
        self.sira = '0'
        
    def cocuk_ekle(self, cocuk):
        self.cocuklar.append(cocuk)
        cocuk.ana = self

    @property
    def bas(self):
        cb = ' - '.join(['No:%s, %s:%s' % (cocuk.no, cocuk.isim, cocuk.adet) for cocuk in self.cocuklar])
        mesajcocuk = 'Çocuklar:['+cb+']'
        if self.ana is None:
            mesajAna = 'None'
        else:
            mesajAna = '[No:%s, %s:%s]' % (self.ana.no, self.ana.isim, self.ana.adet)
            
        mesaj = '[No:%2s] %s:%s (sev:%s kol:%s) %s\tAna:%s \t%s' % (
            self.no, self.isim, self.adet, self.seviye, self.kolon, self.sira,
            mesajAna, mesajcocuk)
        return mesaj
    
class Fptree:
    def __init__(self):

        self.dosya = 'faturalar2.txt'
        self.frekans = 3

        self.girdiler = []
        self.sira = []
        self.adetler = {}
        self.frekanslar = []
        self.faturalar =[]

        self.kalem_yerleri = {}
        self.kok = None

        self.max_seviye = 0
        self.max_kolon  = 0
        
    def dosyayiOku(self):
        with open(self.dosya) as f:
            for line in f:
                self.girdiler.append(line.strip().split(','))
        
    def adetleriBul(self):
        for line in self.girdiler:
            for c in line:
                if self.adetler.get(c, 0) > 0:
                    self.adetler[c] += 1
                else:
                    self.adetler[c] = 1

                # faturalarda geçiş siralı kalemler
                if c not in self.sira:self.sira.append(c)

    def frekansBul(self):
        # Frekansı geçenleri bırakalım.
        # l = [(4,'f'), (3,'a'), ....] şeklinde
        l = [(self.adetler[s], s) for s in self.sira]
        l.sort(key = lambda x: (1000-x[0]))
        gecenler = ['%s:%s' % (y,x) for x,y in l if x >= self.frekans]
        print('Frekanslar:',gecenler)
        self.frekanslar = [y for x,y in l if x >= self.frekans]
        

            
    def kalanSiraliFaturalariBul(self):
        print('Faturalar:')
        for fatura in self.girdiler:
            yenifatura = [fr for fr in self.frekanslar if fr in fatura]
            self.faturalar.append(yenifatura)
            print(yenifatura)

    def alt_node_bul(self, node, kalem):
        for cocuk in node.cocuklar:
            if cocuk.isim == kalem:
                return cocuk
        return None 
            
    def agaciYap(self):
        #Üretilen her node kalem_yerleri sözlüğünde tutulacak
        #Mesela 'b' için nerelerde node üretilmişse kalem_yerleri'nde tutulacak.
        self.kalem_yerleri = {k: [] for k in self.frekanslar}

        self.kok = Node('Kök',0)
        
        node = self.kok
        for fatura in self.faturalar:
            for kalem in fatura:
                alt_node = self.alt_node_bul(node, kalem)
                if alt_node is None:
                    alt_node = Node(kalem, node.seviye+1)
                    node.cocuk_ekle(alt_node)

                    self.kalem_yerleri[kalem].append(alt_node)
                else:
                    alt_node.adet += 1

                node = alt_node

            node = self.kok

        #Ağaç tamamlandı.
        return

    def kolonHesapla(self):
        sirali =[]
        sirali.append(self.kok)
                      
        for k,v in self.kalem_yerleri.items():
            sirali.extend(v)
        sirali.sort(key=lambda x:x.seviye)

        #max_seviye'yi bulalım. Görsel basımda lazım.
        self.max_seviye = max([i.seviye for i in sirali])

        for i in sirali:
            for j in range(len(i.cocuklar)):
                i.cocuklar[j].sira = i.sira +'.'+str(j)

        #siralı'yi sira'ya göre tekrar sıralayalım.
        sirali.sort(key=lambda x:str(x.seviye*100)+'.'+x.sira)
        
        kolonlar = []
        for sev in range(self.max_seviye+1):
            kolon_adet = len([i for i in sirali if i.seviye == sev])
            kolonlar.append(kolon_adet)

        self.max_kolon = max(kolonlar)

        #max kolon olan seviyeden ustte doğru kolon numaralarını verelim.
        seviye = kolonlar.index(self.max_kolon)
        
        kol = 1
        for i in sirali:
            if i.seviye == seviye:
                i.kolon = kol
                kol += 1
                
        
        for sev in range(seviye-1, -1, -1):
            varskolon = 1
            for i in sirali:
                if i.seviye == sev:
                    adet = len(i.cocuklar)
                    if adet > 0:
                        i.kolon = int(sum(cocuk.kolon for cocuk in i.cocuklar) / adet)
                        varskolon = i.kolon
                    else:
                        i.kolon = varskolon + 1
                        varskolon += 1

        #max kolon olan seviyeden alta doğru kolon numaralarını verelim.
        for sev in range(seviye, self.max_seviye):
            varskolon = 1
            for i in sirali:
                if i.seviye == sev:
                    adet = len(i.cocuklar)
                    if adet > 0:
                        for cocuk in i.cocuklar:
                            cocuk.kolon = varskolon
                            varskolon += 1


            
       
    def hesapla(self):
        self.dosyayiOku()
        self.adetleriBul()
        self.frekansBul()
        self.kalanSiraliFaturalariBul()
        self.agaciYap()
        self.kolonHesapla()
        
    def bas(self, order=1):
        #Node'ları basalım.
        cizgi = '='*90
       
        sirali = []
        for k, v in self.kalem_yerleri.items():
            sirali.extend(v)
        
        if order == 1:
            baslik = "Node isimlerine göre sıralı Liste"
            sirali.sort(key=lambda x:self.frekanslar.index(x.isim))
        elif order == 2:
            baslik = "Node no'larına göre sıralı Liste"
            sirali.sort(key=lambda x:x.no)
        elif order == 3:
            baslik = "Node'ların seviyelerine göre sıralı Liste"
            sirali.sort(key=lambda x:str(x.seviye*100)+'.'+x.sira)

        print(cizgi)
        print(baslik.center(90))
        print(cizgi)
        print(self.kok.bas)
        print(cizgi)
        for i in sirali:
            print(i.bas)
        print(cizgi)
        
    def gorselBas(self):
        #Node'ları basalım.
            
        sirali = []
        for k, v in self.kalem_yerleri.items():
            sirali.extend(v)
        sirali.sort(key=lambda x:x.seviye*1000+x.kolon)
        

        width = 800
        height = 600
        dx = 25
        dy = 20
        
        nx = int(width / (self.max_kolon + 1))          # kolon: 1 - max_kolon
        ny = int(height / (self.max_seviye + 2))        # seviye:0 - max_seviye 

        font = "Times 14 bold"
        fg = 'blue'
        bg = 'white'
        fg2 = 'red'
        bg2 = 'orange'
        kalinlik = 3
        
        line_prop = dict(fill=fg, width=kalinlik,arrow='last',arrowshape='16 16 3')
        
        
        def xyBul(node):
            x = node.kolon * nx
            y = (node.seviye + 1) * ny
            return x, y
        
        root = Frame()
        root.pack()
        w = Canvas(root, width = width, height = height, bd = 8)
        w.pack()

        # Kök çizilecek
        x, y = xyBul(self.kok)
        w.create_oval(x - dx, y - dy, x + dx, y + dy, fill=bg2, outline=fg2, width=kalinlik)
        w.create_text(x,y,text='Kök',font = font, fill=fg)

        for cocuk in self.kok.cocuklar:
            x2,y2 = xyBul(cocuk)
            w.create_line(x, y + dy, x2, y2-dy, **line_prop)
            
        #Nodlar çizilecek
        for i in sirali:
            x = i.kolon * nx
            y = (i.seviye+1) * ny
            w.create_rectangle(x - dx, y - dy, x + dx, y + dy,fill=bg2, outline=fg2, width=kalinlik)
            w.create_text(x,y,text=i.isim+':'+str(i.adet), font = font, fill=fg)
            for cocuk in i.cocuklar:
                x2,y2 = xyBul(cocuk)
                w.create_line(x, y + dy, x2, y2-dy, **line_prop)
            
        root.mainloop()
        
        cizgi = '='*90
       
        
           
if __name__ == '__main__':
    
    for dosya in ('faturalar.txt','faturalar1.txt','faturalar2.txt','faturalar3.txt'):
        fp = Fptree()
        fp.dosya = dosya
             
        fp.hesapla()
        fp.bas(1)
        fp.bas(2)
        fp.bas(3)
        fp.gorselBas()
 

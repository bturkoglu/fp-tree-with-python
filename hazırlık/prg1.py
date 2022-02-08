class Node:
    no = 0
    def __init__(self, isim, adet):
        self.isim = isim
        self.adet = adet

        self.ana = None
        self.cocuklar = []

        self.no = Node.no
        Node.no += 1
        
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
            
        mesaj = '[No:%2s] %s:%s \tAna:%s \t%s' % (self.no, self.isim, self.adet, mesajAna, mesajcocuk)
        return mesaj
    
class Fptree:
    def __init__(self):

        self.dosya = 'faturalar.txt'
        self.frekans = 3
        self.girdiler = []
        self.sira = []
        self.adetler = {}
        self.frekanslar = []
        self.faturalar =[]

        self.kalem_yerleri = {}
        self.kok = None
        
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
                    alt_node = Node(kalem, 1)
                    node.cocuk_ekle(alt_node)

                    self.kalem_yerleri[kalem].append(alt_node)
                else:
                    alt_node.adet += 1

                node = alt_node

            node = self.kok

        #Ağaç tamamlandı.
        return

                           
        
    def hesapla(self):
        self.dosyayiOku()
        self.adetleriBul()
        self.frekansBul()
        self.kalanSiraliFaturalariBul()
        self.agaciYap()

    def bas(self):
        #Node'ları sıralı basalım.
        cizgi = '='*80
        
        sirali = []
        for k, v in self.kalem_yerleri.items():
            sirali.extend(v)
        
        sirali.sort(key=lambda x:x.no)

        print(cizgi)
        print(self.kok.bas)
        print(cizgi)
        for i in sirali:
            print(i.bas)
        print(cizgi)
        

if __name__ == '__main__':
    fp = Fptree()
    fp.hesapla()
    fp.bas()
 

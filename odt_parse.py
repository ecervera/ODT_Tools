import odf
import odf.text as text
import odf.style as style
import odf.opendocument as odt

import zipfile

meta_label = ['IC', 'CD', 'DS', 'EC', 'ED', 'EDf']
stat_label = ['Pages', 'Pars', 'Chars', 'NWSp']

from unidecode import unidecode

def str_decode(s):
    return unidecode(s).lower().replace('_20_','_').replace('_5f_','_').replace(' ','_')

class OdtData:
    def __init__(self, filename, par_prop=[], text_prop=[], page_prop=[]):
        self.filename = filename
        self.doc = None
        self.err = None
        try:
            self.doc = odt.load(filename)
            self._read_meta()
            self._read_stat()
            self._read_styles(par_prop, text_prop, page_prop)
            self._read_headings()
            self._read_pars()
        except FileNotFoundError:
            self.err = 'FileNotFound'
        except zipfile.BadZipFile:
            self.err = 'BadZipFile'
    
    def _read_meta(self):

        def format_time(t):
            t = t[2:]
            if 'H' in t:
                h, t = t.split('H')
            else:
                h = '0'
            if 'M' in t:
                m, t = t.split('M')
            else:
                m = '0'
            if 'S' in t:
                s, _ = t.split('S')
            else:
                s = '0'
            if int(s) >= 60:
                m = str(int(s) // 60)
                s = str(int(s) % 60)
                if int(m) >= 60:
                    h = str(int(m) // 60)
                    m = str(int(m) % 60)
            return h.zfill(2) + ':' + m.zfill(2) + ':' + s.zfill(2)

        self.meta = {}
        meta_type = [odf.meta.InitialCreator, odf.meta.CreationDate, 
                     odf.meta.DateString, odf.meta.EditingCycles, 
                     odf.meta.EditingDuration, odf.meta.EditingDuration]

        for l, t in zip(meta_label, meta_type):
            element = self.doc.meta.getElementsByType( t )
            if element:
                if l == 'EDf':
                    data = format_time( str(element[0]))
                else:
                    data = str(element[0])
            else:
                data = None
            self.meta[l] = data
            
    def _read_stat(self):
        self.stat = {}
        #stat_label = ['Pages', 'Pars', 'Chars', 'NWSp']
        stat_attr = ['pagecount', 'paragraphcount', 'charactercount', 'nonwhitespacecharactercount']

        ds = self.doc.meta.getElementsByType(odf.meta.DocumentStatistic)
        if ds:
            for (l,a) in zip(stat_label, stat_attr):
                self.stat[l] = ds[0].getAttribute( a )        
        
    def _read_styles(self, par_prop, text_prop, page_prop):
        self.style = {}
        self.style['paragraph'] = []
        self.style['text'] = []
        self.style['graphic'] = []
        self.style['page'] = []
        self.style['section'] = []
        
        for st in self.doc.getElementsByType(style.MasterPage):
            name = st.getAttribute('name')
            stdict = {'name': str_decode(name)} 
            for pp in page_prop:
                attr = st.getAttribute(pp)
                if attr:
                        stdict[pp] = str_decode(attr)
            self.style['page'].append(stdict)

        self.directFormat = 0
        for st in self.doc.getElementsByType(style.Style):
            name = st.getAttribute('name')
            parent = st.getAttribute('parentstylename')
            family = st.getAttribute('family')
            if parent:
                parent = str_decode(parent)
            stdict = {'name': str_decode(name), 
                      'parent': parent}
            stpp = st.getElementsByType(style.ParagraphProperties)
            if stpp:
                for pp in par_prop:
                    attr = stpp[0].getAttribute(pp)
                    if attr:
                        stdict[pp] = attr
            sttp = st.getElementsByType(style.TextProperties)
            if sttp:
                for tp in text_prop:
                    attr = sttp[0].getAttribute(tp)
                    if attr:
                        stdict[tp] = attr
            try:
                self.style[family].append(stdict)
                if family=='paragraph' and name[0]=='P' and name[1:].isdigit():
                    self.directFormat += 1
            except KeyError:
                pass
            
    def _read_headings(self):
        self.H = []
        self.emptyHeadings = 0
        for h in self.doc.getElementsByType(text.H):
            sn = h.getAttribute('stylename')
            if sn is None:
                sn = ''
            self.H.append({'style': str_decode(sn), 'text': str(h)})
            if len(str(h)) == 0:
                self.emptyHeadings += 1
            
    def _read_pars(self):
        self.P = []
        self.emptyPars = 0
        for p in self.doc.getElementsByType(text.P):
            self.P.append({'style': str_decode(str(p.getAttribute('stylename'))), 'text': str(p)})
            if len(str(p)) == 0:
                self.emptyPars += 1

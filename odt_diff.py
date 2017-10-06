from odt_parse import str_decode

def style_id(name, par_st):
    if name[0]=='P' or name[0]=='p':
        parent = [st['parent'] for st in par_st if st['name']==name]
        sid = 'formato directo sobre ' + parent[0]
    else:
        sid = name
    return sid

def find_style_by_name(stlist, name):
    dname = str_decode(name)
    st = [st for st in stlist if st['name'] == dname]
    if st:
          return st[0]
    else:
          return None

def find_heading_by_text(hlist, text):
    return [h for h in hlist if text in h['text']]  

def find_par_by_text(plist, text):
    return [p for p in plist if text in p['text']]

def odt_compare(ref, doc):
    s = ''

    s += '\nEstructura\n----------\n'
    if doc.emptyHeadings:
        s+= 'El documento tiene %d títulos vacíos.\n' % doc.emptyHeadings
    if doc.emptyPars:
        s+= 'El documento tiene %d párrafos vacíos.\n' % doc.emptyPars
    if len(doc.H)!=len(ref.H):
        s+= 'El documento tiene %d títulos en lugar de %d\n' % (len(doc.H), len(ref.H))
    if len(doc.P)!=len(ref.P):
        s+= 'El documento tiene %d párrafos en lugar de %d\n' % (len(doc.P), len(ref.P))
        
    s += '\nEstilos de títulos\n------------------\n'
    try:
        for i in range(len(ref.H)):
            ref_id = style_id(ref.H[i]['style'], ref.style['paragraph'])
            doc_id = style_id(doc.H[i]['style'], doc.style['paragraph'])
            if ref_id != doc_id:
                s += 'Título %2d "%s..." tiene estilo \n  %s en lugar de %s.\n\n' % (i, doc.H[i]['text'][:15],
                                                                                     doc_id, ref_id)
    except IndexError:
        pass

    try:
        s += '\nEstilos de párrafos\n-------------------\n'
        for i in range(len(ref.P)):
            ref_id = style_id(ref.P[i]['style'], ref.style['paragraph'])
            doc_id = style_id(doc.P[i]['style'], doc.style['paragraph'])
            if ref_id != doc_id:
                s += 'Párrafo %2d "%s..." tiene estilo \n  %s en lugar de %s.\n\n' % (i, doc.P[i]['text'][:30],
                                                                                      doc_id, ref_id)
    except IndexError:
        pass
    
    return s

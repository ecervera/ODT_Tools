import tornado
import tornado.ioloop
import tornado.web
import os, uuid

__UPLOADS__ = "uploads/"

import sys
sys.path.append('..')

from odt_parse import OdtData
from odt_diff import find_style_by_name

ref_name = '../libro_personalizados.odt'
par_prop = ['backgroundcolor', 'textalign', 'marginleft', 'marginright', 'margintop', 'marginbottom', 'breakbefore']
text_prop = ['fontsize', 'fontstyle', 'language']
ref = OdtData(ref_name, par_prop, text_prop)

sp_dict = {'Heading':'Título', 'Heading_1':'Título_1', 'breakbefore':'salto de página antes',
           'backgroundcolor':'color de fondo', 'textalign':'alineación', 
           'Quotations':'Cita', 'fontsize':'tamaño de letra', 'fontstyle':'efecto tipográfico', 
           'marginleft':'sangría izquierda', 'marginright':'sangría derecha', 
           'margintop':'espacio superior', 'marginbottom':'espacio inferior',
           'justify':'justificada', 'end':'derecha', 'start':'izquierda'}
           
def sp_trans(s):
    try:
        t = sp_dict[s]
    except KeyError:
        t = s
    return t
    
    
errors = []
import io

def compare_style_attr(ref, doc, family, style_name, attr_list):
    stref = find_style_by_name(ref.style[family], style_name)
    stdoc = find_style_by_name(doc.style[family], style_name)
    f = io.StringIO()
    if stdoc:
        for attr in attr_list:
            try:
                val_ref = stref[attr]
                try:
                    val_doc = stdoc[attr]
                    if val_ref != val_doc:
                        f.write('Estilo %s tiene %s <br>  %s en lugar de %s.<br><br>' % (sp_trans(style_name), sp_trans(attr),
                                                                                     sp_trans(val_doc), sp_trans(val_ref)))
                except KeyError:
                        f.write('Estilo %s no tiene %s definido.<br><br>' % (sp_trans(style_name), sp_trans(attr)))
                #except TypeError:
                #        f.write('Estilo %s no está definido.\n\n' % (sp_trans(style_name)))
            except KeyError:
                err = style_name + "_" + attr
                if not err in errors:
                    errors.append(err)
                    print('Estilo %s no tiene %s definido en el fichero de referencia.' % (sp_trans(style_name), sp_trans(attr)))
    else:
        f.write('Estilo %s no está definido.<br><br>' % (sp_trans(style_name)))
    return f.getvalue()
    
def compare_style_attrs(ref, doc):
    s = '<h4>libro_personalizados</h4><br>'
    errors = 0
    err = compare_style_attr(ref, doc, 'paragraph', 'Párrafo', 
                       ['fontsize', 'textalign'])
    if err:
        s += err
        errors += 1
    err = compare_style_attr(ref, doc, 'paragraph', 'Heading_1', 
                       ['margintop', 'breakbefore'])
    if err:
        s += err
        errors += 1
    err = compare_style_attr(ref, doc, 'paragraph', 'Nota', 
                       ['fontsize', 'backgroundcolor', 'marginleft'])
    if err:
        s += err
        errors += 1
    err = compare_style_attr(ref, doc, 'paragraph', 'Quotations', 
                       ['marginleft','marginright','textalign'])
    if err:
        s += err
        errors += 1
    err = compare_style_attr(ref, doc, 'paragraph', 'Cita_en_inglés', 
                       ['language'])
    if err:
        s += err
        errors += 1
    err = compare_style_attr(ref, doc, 'paragraph', 'Autor_de_cita', 
                       ['textalign'])
    if err:
        s += err
        errors += 1
    if not errors:
        s += "No s'han trobat errors."
    return s
                       
        
class Userform(tornado.web.RequestHandler):
    def get(self):
        self.render("Personalizados.html")


class UploadAndCheck(tornado.web.RequestHandler):
    def post(self):
        try:
            fileinfo = self.request.files['filearg'][0]
            fname = fileinfo['filename']
            extn = os.path.splitext(fname)[1]
            cname = str(uuid.uuid4()) + extn
            fname = __UPLOADS__ + cname
            fh = open(fname, 'wb')
            fh.write(fileinfo['body'])
            #self.finish(cname + " is uploaded!! Check %s folder" %__UPLOADS__)
            doc = OdtData( fname, par_prop, text_prop )
            if doc.err:
                s = 'Error de lectura del fitxer\n'
            else:
                s = compare_style_attrs(ref, doc)
        except KeyError:
            s = "No s'ha triat cap fitxer."
        s += '<br><hr><button type="button" onclick="javascript:history.back()">Back</button>'
        self.finish(s)


application = tornado.web.Application([
        (r"/", Userform),
        (r"/checkPersonalizados", UploadAndCheck),
        ], debug=True)


if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

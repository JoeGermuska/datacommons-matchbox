#!/usr/bin/env python
import os, sys
mbpath = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(mbpath, '..'))

from matchbox.api import LocalClient
import re, htmlentitydefs

ENTITIES = {'<': '&lt;', '>': '&gt;', '"': '&quot;', '\'': '&apos;', '&': '&amp;'}

def xmlclean(s):
    for o, n in ENTITIES.iteritems():
        s = s.replace(o, n)
    return re.sub(r'[\0\a\b\t\n\f\r\e]', '', s)

def main():
    mb = LocalClient('datacommons')
    
    sys.stdout.write("""<?xml version="1.0" encoding="utf-8"?>\n<sphinx:docset>\n""")
    
    for doc in mb.search(**{'_type': 'politician'}):
        
        data = {
            'id': doc['_suid'],
            'name': xmlclean(doc['name']),
            'type': doc['_type'],
        }
        
        if 'aliases' in doc:
            data['aliases'] = ', '.join((xmlclean(a) for a in doc['aliases']))
        else:
            data['aliases'] = ''
        
        content = """\t<sphinx:document id="%(id)s">\n\t\t<entity>%(name)s</entity>\n\t\t<aliases>%(aliases)s</aliases>\n\t\t<type>%(type)s</type>\n\t</sphinx:document>\n""" % data
        sys.stdout.write(content)
        
    sys.stdout.write("""</sphinx:docset>""")

if __name__ == '__main__':
    main()
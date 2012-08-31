
import difflib

from xml.etree import ElementTree as xml






# def compare_trees(a, b):
#
#
#     for c1, c2 in zip(a, b):
#
#         if c1.tag == c2.tag and sorted(c1.items()) == sorted(c2.items()) and c1.text == c2.text:
#             return compare_trees(c1, c2)
#         else:
#             print 'Not Equal', c1.tag, c2.tag
#             print 'c1', [c1.attrib, c1.text], 'c2', [c2.attrib, c2.text]
#             return False
#
#     return True




def compare_xml_strings(a, b):

    if a != b:
        d = difflib.context_diff(a.splitlines(), b.splitlines(), fromfile='a.py', tofile='b.py')

        for line in d:
            print line
        return False
    return True

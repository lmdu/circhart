import yattag

doc, tag, text = yattag.SimpleDoc(stag_end='>', nl2br=True).tagtext()

with tag('ideogram'):
	text('spacing = 0.5')
	text('show = yes')
	with tag('spacing'):
		text('default=0.005r')

doc.stag('include')

res = yattag.indent(doc.getvalue(), indentation=' ', newline='\n', indent_text=True)

print(res)
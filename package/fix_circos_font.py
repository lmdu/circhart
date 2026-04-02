import os

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
svg_script = os.path.join(root_dir, 'src', 'circos', 'lib', 'Circos', 'SVG.pm')
old_script = os.path.join(root_dir, 'src', 'circos', 'lib', 'Circos', 'SVG1.pm')
os.rename(svg_script, old_script)

target = '''my $svg = sprintf(qq{<text x="%.1f" y="%.1f" font-size="%.1fpx" font-family="%s" style="%s" transform="rotate(%.1f,%.1f,%.1f)" %s>%s</text>},'''

script="""
	my $font_weight="normal";
	my $font_style="normal";

	if ($font_name eq "") {

	} else if ()
"""

with open(svg_script, 'w') as fw:
	with open(old_script) as fh:
		for line in fh:
			if line.strip() == target:
				print("\tmy $font_weight='normal';", file=fw)
				print("\tmy $font_style='normal';", file=fw)



import os

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
svg_script = os.path.join(root_dir, 'src', 'circos', 'lib', 'Circos', 'SVG.pm')
old_script = os.path.join(root_dir, 'src', 'circos', 'lib', 'Circos', 'SVG1.pm')
os.rename(svg_script, old_script)

target = '''my $svg = sprintf(qq{<text x="%.1f" y="%.1f" font-size="%.1fpx" font-family="%s" style="%s" transform="rotate(%.1f,%.1f,%.1f)" %s>%s</text>},'''

script="""
	my $font_weight="normal";
	my $font_style="normal";

	if ($params{font} eq "light") {
		$font_weight = "200";
	} elsif ($font_name eq "CMUBright-Semibold") {
		$font_weight="500";
	} elsif ($font_name eq "CMUBright-Bold") {
		$font_weight="bold";
	} elsif ($font_name eq "CMUBright-Oblique") {
		$font_style="italic";
	} elsif ($font_name eq "CMUBright-BoldOblique") {
		$font_weight="bold";
		$font_style="italic";
	}

	my $svg = sprintf(qq{<text x="%.1f" y="%.1f" font-size="%.1fpx" font-family="Arial" font-style="%s" font-weight="%s" style="%s" transform="rotate(%.1f,%.1f,%.1f)" %s>%s</text>},
"""

with open(svg_script, 'w') as fw:
	with open(old_script) as fh:
		for line in fh:
			if line.strip() == target:
				print(script, end='', file=fw)

			elif line.strip() == '$font_name,':
				print("\t\t\t\t\t\t\t\t\t\t$font_style,", file=fw)
				print("\t\t\t\t\t\t\t\t\t\t$font_weight,", file=fw)

			else:
				print(line, end='', file=fw)

import webview

class Api:
	def log(self, value):
		print(value)

if __name__ == '__main__':
	window = webview.create_window('Circhart', 'assets/index.html',
		js_api = Api()
	)
	webview.start()

from .newspaper import Newspaper

# And add the extension to Krita's list of extensions:
app = Krita.instance()
# Instantiate your class:
extension = Newspaper(parent=app)
app.addExtension(extension)

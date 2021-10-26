import sys
import os
import time
import ctypes

# Import the source to obtain version number for building
from ovlc import __version__

class product:
	def __init__(self):
		self.info = """VSVersionInfo(
   ffi=FixedFileInfo(
    filevers=(0, 0, 0, 0),
    prodvers=(0, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u''),
        StringStruct(u'FileDescription', u'Fullscreen Media Player with hotkey support'),
        StringStruct(u'FileVersion', u'{version}.0'),
        StringStruct(u'InternalName', u'ovlc'),
        StringStruct(u'LegalCopyright', u''),
        StringStruct(u'OriginalFilename', u''),
        StringStruct(u'ProductName', u'Media Player'),
        StringStruct(u'ProductVersion', u'{version}.0')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)"""
		self.pi_file = "pi.txt"
		self.py_file = "ovlc.py"

	def productInformation(self):
		"""
		Write product information to disk
		"""
		with open(self.pi_file, "a") as file:
			file.write(self.info.format(version=__version__))
		
		if os.path.isfile(self.pi_file):
			return True
		else:
			return False

	def build(self):
		"""
		Start pyinstaller and buld the executable
		"""
		if self.productInformation() == False:
			sys.exit()
		
		try:
			ctypes.windll.shell32.ShellExecuteW(None, "open", 'pyinstaller',
								'--icon "icon.ico" --onefile --noconsole {file} --version-file={pi_file}'.format(file=self.py_file,
								pi_file=self.pi_file), None, 0)
		except Exception:
			return False
		
		while True:
			if os.path.isfile(os.path.join("dist", "ovlc.exe")):
				return True
			else:
				time.sleep(1)

	def cleanup(self):
		"""
		Delete all the temporary files created while building
		"""
		cmds = ["del {pi_file} /S /Q >nul".format(pi_file=self.pi_file),
			"del {py_file}.spec /S /Q >nul".format(py_file=self.py_file.strip(".py")),
			"rmdir build /S /Q >nul",
			"rmdir __pycache__ /S /Q >nul"]

		for cmd in cmds:
			os.system(cmd)

		return True

def main():
	p = product()
	if p.build():
		print("Build completed!")
	if p.cleanup():
		print("Cleanup completed!")

if __name__ == "__main__":
	main()

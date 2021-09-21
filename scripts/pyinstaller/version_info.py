import os
import re

exe_name = os.environ["XAPPT_EXE_NAME"]
exe_version = os.environ["XAPPT_EXE_VERSION"]
company_name = os.environ.get("XAPPT_COMPANY_NAME", "")
copyright_message = os.environ.get("XAPPT_COPYRIGHT", "")

VERSION_RE = re.compile(r"^(\d+)\.(\d+).(\d+)-(.*)$")

version_match = VERSION_RE.match(exe_version)
if version_match is None:
    raise RuntimeError("XAPPT_EXE_VERSION must be in the form of '0.0.0-abc'")

major = version_match.group(1)
minor = version_match.group(2)
revision = version_match.group(3)
build = version_match.group(4)

version_info_str = f"""
VSVersionInfo(
  ffi=FixedFileInfo(
filevers=({major}, {minor}, {revision}, 0),
prodvers=({major}, {minor}, {revision}, 0),
mask=0x3f,
flags=0x0,
OS=0x4,
fileType=0x1,
subtype=0x0,
date=(0, 0)
),
  kids=[
StringFileInfo(
  [
  StringTable(
    u'040904B0',
    [StringStruct(u'CompanyName', u'{company_name}'),
    StringStruct(u'FileDescription', u'{exe_name}'),
    StringStruct(u'FileVersion', u'{major}.{minor}.{revision}'),
    StringStruct(u'InternalName', u'{exe_name}'),
    StringStruct(u'LegalCopyright', u'{copyright_message}'),
    StringStruct(u'OriginalFilename', u'{exe_name}.exe'),
    StringStruct(u'ProductName', u'{exe_name}'),
    StringStruct(u'ProductVersion', u'{exe_version}')])
  ]), 
VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""

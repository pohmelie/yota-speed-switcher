from cx_Freeze import setup, Executable
import requests.certs


options = {
    "build_exe": {
        "includes": [],
        "create_shared_zip": False,
        "packages": ["html5lib", "docopt"],
        "include_files": [
            (requests.certs.where(), 'cacert.pem'),
            "logo-yota.png",
            "logo-yota-gray.png",
            "login.ui",
        ]
    }
}

executables = [
    Executable(
        script="yota-speed-switcher.py",
        base="Win32GUI",
        targetName="yota-speed-switcher.exe",
        compress=True,
        copyDependentFiles=True,
        appendScriptToExe=True,
        appendScriptToLibrary=False,
        icon="logo-yota.ico"
    )
]

setup(
    name="yota speed switcher",
    version="0.0.1",
    description="",
    options=options,
    executables=executables,
)

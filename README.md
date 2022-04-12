# DeepShapeGrammars

Implementation of shape grammars with deep learning template matching in GIMP 3.

# WARNING

This plugin is not fully implemented yet!

# Installation

The plug-in is implemented in Python 3, so you need the 2.99 development version of GIMP to install it. To get the GIMP development version install flatpak if you haven't already:

```console
sudo apt install flatpak
```

Add repositories to flatpak:

```console
flatpak remote-add flathub https://flathub.org/repo/flathub.flatpakrepo
flatpak remote-add flathub-beta https://flathub.org/beta-repo/flathub-beta.flatpakrepo
```

Install GIMP:

```console
flatpak install flathub-beta org.gimp.GIMP
```

Test if Gimp installation is working:

```console
flatpak run org.gimp.GIMP//beta
```

Under Filter > Development > Python-Fu > Python Console you should see something like:

```console
GIMP 2.99.10 Python Console 
Python 3.9.9 (main, Nov 10 2011, 15:00:00) 
[GCC 11.2.0]
```

Now close GIMP, and get the pip3 installation script:

```console
wget https://bootstrap.pypa.io/get-pip.py
```

Run the script with the Gimp internal Python 3 interpreter:

```console
flatpak run --command=python org.gimp.GIMP get-pip.py
```

Now position yourself into the folder where you have downloaded Deep Shape Grammars and install the requirements.txt:

```console
flatpak run --command=python org.gimp.GIMP -m pip install -r requirements.txt
```

Now with everything setup, run the installation script:

```console
./install.sh
```

Start GIMP again, and if everything worked well, you should now see Deep Shape Grammars in the Filters > Artistic menu.



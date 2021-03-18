#!/usr/bin/env python3

import os
import shutil

os.mkdir("build")
shutil.copy("index.html", "build/index.html")

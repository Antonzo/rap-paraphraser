#!/usr/bin/python3
# -*- coding: utf-8 -*-
import warnings
warnings.filterwarnings("ignore")

import io, cgi, cgitb, sys, re, gensim
import pymorphy2 as pm 

cgitb.enable()

if hasattr(sys.stdout, "buffer"):
  def bwrite(s):
    sys.stdout.flush()
    sys.stdout.buffer.write(s)
  write = sys.stdout.write
else:
  wrapper = io.TextIOWrapper(sys.stdout)
  def bwrite(s):
    wrapper.flush()
    sys.stdout.write(s)
  write = wrapper.write
write("Location: http://www.muam.nichost.ru/\n\n")
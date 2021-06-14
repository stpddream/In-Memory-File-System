# In-Memory-File-System

All the basic functions are supported and also
  * copy with collision handling
  * Operations on paths, including auto create directories
are implemented.
  
Code Structure is simple. file_system_view is a thin presentation layer that handles 
any printing to the user. FileSystem class is the main file system API. file.py contains the
abstraction used to represent files

Note that the notion of 'files' as actual non directory files and 'files' to represent abstract
concept of files (since both directories and actual files are 'files') are sometimes 
used interchangeably. I probably should have changed that but did not get a chance to.

Also user experience in error scenarios can be improved as well. Currently it mostly just print out
the exception. There are some exceptions not catched at the view layer as well, expecially for bad input.

file names are stored both on parent and as metadata in files as I find it easier to use in many
scenarios.

I've written some tests.

```
# To run demo: 
python3 demo.py

# To run tests:
python3 -m unittest file_system_test.py

```

Enjoy!

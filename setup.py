import setuptools
setuptools.setup()

"""
What is the relationship between setup.py and setup.cfg?

- Historically, setup.py was the primary file for defining package 
  configurations. Over time, as the community sought more standardized 
  and less error-prone methods, the static setup.cfg emerged as a 
  preferred alternative for specifying package metadata.
- In modern packaging practices, it's common to see the combination 
  of a minimal setup.py with the majority of configurations in setup.cfg. 
  This allows for a cleaner separation between the build script and 
  the package metadata/configuration.
- When both setup.py and setup.cfg are present, setuptools will combine 
  the configurations from both. If there are conflicts, the values in 
  setup.py typically take precedence.
"""
from distutils.core import setup

license_text = open('LICENSE').read()
long_description = open('README.rst').read()

setup(name="matchbox",
      version=__version__,
      py_modules=["matchbox"],
      description="store for matching entities used by Sunlight Data Commons",
      author="James Turk",
      author_email = "jturk@sunlightfoundation.com",
      license=license_text,
      url="http://github.com/sunlightlabs/datacommons-matchbox/",
      long_description=long_description,
      platforms=["any"],
      classifiers=["Development Status :: 3 - Alpha",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: BSD License",
                   "Natural Language :: English",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   ],
      )


import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='htrc-text-processing',  
    version='1.1.0',
    #scripts=['htrc-text-processing'] ,
    author="Ashan Liyanage, Elizabeth Schwartz, Daniel Evans, Ryan Dubnicek",
    author_email=" feedback@issues.hathitrust.org",
    description="Text processing and analysis for HathiTrust Research Center",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/htrc/ht-text-prep",
    packages=setuptools.find_packages(),
    classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: University of Illinois/NCSA Open Source License",
         "Operating System :: OS Independent",
         ],
    python_requires='>=3.6',
 )

import glob,setuptools,os
from pathlib import Path
from setuptools import setup

DISTNAME = 'j_kernel'
DESCRIPTION = 'A Jupyter kernel for J.'
LONG_DESCRIPTION = open('README.md').read()
MAINTAINER = 'Jeremy Howard'
MAINTAINER_EMAIL = 'info@howard.fm'
URL = 'http://github.com/fastai/j_kernel'
LICENSE = 'GPL'
REQUIRES = ["jupyter_client (>=4.3.0)", "ipykernel"]
INSTALL_REQUIRES = REQUIRES

CLASSIFIERS = """\
Intended Audience :: Science/Research
License :: OSI Approved :: GPL License
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Topic :: Scientific/Engineering
Topic :: Software Development
Topic :: System :: Shells
"""

import notebook
nb_dir = Path(notebook.__file__).parent.relative_to(os.environ['CONDA_PREFIX'])
DATA_FILES = [
    (f'{nb_dir}/static/components/codemirror/mode/j', ['syntax/J.js']),
    ('share/jupyter/kernels/j', glob.glob('kernel_definition/*.*')),
]

setup(
    name=DISTNAME,
    version='0.0.1',
    maintainer=MAINTAINER, maintainer_email=MAINTAINER_EMAIL,
    packages = setuptools.find_packages(),
    data_files=DATA_FILES,
    url=URL, download_url=URL,
    license=LICENSE,
    platforms=["Any"],
    description=DESCRIPTION, long_description=LONG_DESCRIPTION, long_description_content_type='text/x-rst',
    classifiers=list(filter(None, CLASSIFIERS.split('\n'))),
    install_requires=INSTALL_REQUIRES
)


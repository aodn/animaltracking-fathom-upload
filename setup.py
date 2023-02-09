from distutils.core import setup

setup(
    name='animaltracking',
    packages=['animaltracking'],
    version='0.1.2',
    license='GPL',
    description='Animal Tracking Fathom Upload Tool',
    author='Viet Nguyen',
    author_email='vh.nguyen@utas.edu.au',
    url='https://github.com/aodn/animaltracking-fathom-upload',
    download_url='https://github.com/aodn/animaltracking-fathom-upload/archive/v_012.tar.gz',
    keywords=['fathom', 'upload', 'toolkit'],
    install_requires=[
        'argparse',
        'tqdm',
        'requests'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Software Development :: Libraries ',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)

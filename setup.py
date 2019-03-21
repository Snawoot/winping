from setuptools import setup

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='winping',
      version='0.2.0',
      description="Ping implementation which utilizes Windows ICMP API",
      url='https://github.com/Snawoot/winping',
      author='Vladislav Yarmak',
      author_email='vladislav-ex-src@vm-0.com',
      license='MIT',
      packages=['winping'],
      python_requires='>=3.5.3',
      setup_requires=[
          'wheel',
      ],
      install_requires=[
      ],
      entry_points={
          'console_scripts': [
              'winping=winping.__main__:main',
          ],
      },
      classifiers=[
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "License :: OSI Approved :: MIT License",
          "Operating System :: Microsoft :: Windows",
          "Operating System :: Microsoft :: Windows :: Windows Server 2003",
          "Operating System :: Microsoft :: Windows :: Windows Server 2008",
          "Operating System :: Microsoft :: Windows :: Windows XP",
          "Operating System :: Microsoft :: Windows :: Windows Vista",
          "Operating System :: Microsoft :: Windows :: Windows 7",
          "Operating System :: Microsoft :: Windows :: Windows 8",
          "Operating System :: Microsoft :: Windows :: Windows 8.1",
          "Operating System :: Microsoft :: Windows :: Windows 10",
          "Development Status :: 4 - Beta",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "Natural Language :: English",
          "Topic :: Internet",
          "Topic :: Software Development :: Libraries",
          "Topic :: System :: Networking",
          "Topic :: Utilities",
      ],
      long_description=long_description,
      long_description_content_type='text/markdown',
      zip_safe=True)

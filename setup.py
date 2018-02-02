from setuptools import setup

def readme():
  with open('README.rst') as f:
    return f.read()

setup(
  name="tfset",
  version="1.2",
  description="Set Tensor values during training in Tensorflow.",
  long_description=readme(),
  classifiers=[
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Programming Language :: Python :: 3",
    "Topic :: Scientific/Engineering :: Artificial Intelligence"
  ],
  keywords="tensorflow interactive",
  url="https://github.com/ondrejba/tfset",
  author="Ondrej Biza",
  author_email="ondrej.biza@gmail.com",
  license="MIT",
  packages=["tfset"],
  scripts=["tfset/bin/tfset"],
  install_requires=[
    "tensorflow>=1.0"
  ],
  include_package_data=True,
  zip_safe=False,
  test_suite='tests'
)

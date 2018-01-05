from setuptools import setup
setup(
  name="tfset",
  version="1.0",
  describe="Set Tensor values during training in Tensorflow.",
  url="https://github.com/ondrejba/interactive-tensorflow",
  author="Ondrej Biza",
  author_email="ondrej.biza@gmail.com",
  license="MIT",
  packages=["tfset"],
  install_requires=[
    "tensorflow"
  ]
)

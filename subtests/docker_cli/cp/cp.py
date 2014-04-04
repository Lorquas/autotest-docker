"""
Test output of the docker cp command

1. Look for an image or container
2. Run the docker cp command on it
3. Make sure the file was successfully copied
"""

# Okay to be less-strict for these cautions/warnings in subtests
# pylint: disable=C0103,C0111,R0904,C0103


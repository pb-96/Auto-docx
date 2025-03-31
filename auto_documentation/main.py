import argparse


def main_parse():
    msg = "Adding description"
    # Initialize parser
    parser = argparse.ArgumentParser(description=msg)
    parser.parse_args()



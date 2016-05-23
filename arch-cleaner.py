#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import argparse
import sys
import subprocess


__VERSION__ = "0.2"
packagePattern = "([^ ]+)/([^ ]+) ([^ ]+)(\\( [^ ]+\\)|)?"


def parse():
	parser = argparse.ArgumentParser(
		prog="./uninstall_selector.py",
		description="List all installed Arch packages and ask to remove them.",
	)
	parser.add_argument("-c", "--collect", default=False, action="store_true", help="don't delete right away, store and delete on SIGTERM or finish.")
	parser.add_argument("-d", "--show-desc", default=False, action="store_true", help="don't ask to show description, do it right away.")
	parser.add_argument("--core", default=False, action="store_true", help="suggest packages from core repository as well.")
	parser.add_argument("--version", action="version", version="{} {}".format(parser.prog, __VERSION__))
	return parser.parse_args()


def run(cmd):
	return os.popen(cmd).read()


def runThrough(cmd):
	return subprocess.run(cmd, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr, shell=True)


def getSortedPackageList(includeCore=False):
	repoOrder = ["core", "extra", "community", "multilib", "testing", ""]
	packageList = run("package-query -Qett").splitlines()
	if not includeCore:
		packageList = [package for package in packageList if not package.startswith("core")]
	return sorted(packageList, key=lambda word: [repoOrder.index(r) for r in repoOrder if word.startswith(r)])


def removePackages(packages, config=False):
	runThrough("sudo pacman -R{}s {}".format("n" if config else "", packages))


def choose(message, options=["y", "n", "Y", "N", ""]):
	choice = None
	while choice not in options:
		print(message, end="")
		choice = input()
		# print()
	return choice


def main():
	args = parse()
	
	packagesForDeletion = []
	packagesForDeletionWithConfigs = []
	try:
		print("Loading package list...")
		packages = getSortedPackageList(args.core)
		for package in packages:
			if not args.show_desc:
				choice = choose("{} - Show description? [y/N]".format(package))
			else:
				choice = "y"
			if choice in ["y", "Y"]:
				match = re.match(packagePattern, package)
				if match is None:
					print("Error, package {} does not match pattern".format(package))
					continue
				try:
					repo, name, version, group = match.groups()
				except ValueError as ve:
					print("Unexpected mismatch in package name string:", str(ve), "({})".format(match.groups()))
					continue
				info = run("yaourt -Qi {}".format(name)).splitlines()
				for line in info:
					if line.startswith("Description"):
						line = re.match("Description +: (.+)", line).group(1)
						description = "{}: {}".format(package, line)
				choice = choose("{}. --- Uninstall? [y/N]".format(description))
				if choice in ["y", "Y"]:
					choice = choose("Remove configuration files as well? [y/N]")
					removeConfigs = choice in ["y", "Y"]
					if args.collect:
						if removeConfigs:
							packagesForDeletionWithConfigs.append(name)
						else:
							packagesForDeletion.append(name)
					else:
						removePackages(name, removeConfigs)
	except KeyboardInterrupt:
		print()
		if (len(packagesForDeletion) + len(packagesForDeletionWithConfigs)) > 0:
			try:
				choice = choose("Delete {} packages now? List them? [y/N/l]".format(
					len(packagesForDeletion) + len(packagesForDeletionWithConfigs)),
					["y", "n", "Y", "N", "l", "L", ""])
				if choice in ["l", "L"]:
					for package in packagesForDeletion + packagesForDeletionWithConfigs:
						print(package)
					choice = choose("Continue? [y/N]")
				if choice in ["y", "Y"]:
					if len(packagesForDeletion) > 0:
						removePackages(" ".join(packagesForDeletion))
					if len(packagesForDeletionWithConfigs) > 0:
						removePackages(" ".join(packagesForDeletionWithConfigs), configs=True)
			except KeyboardInterrupt:
				print()
		else:
			pass

if __name__ == "__main__":
	main()

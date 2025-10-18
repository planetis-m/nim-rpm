srpm:
	dnf -y install git rpm-build
	dnf -y copr enable planetis/nim
	dnf -y install nim
	rpkg srpm --outdir $(outdir)

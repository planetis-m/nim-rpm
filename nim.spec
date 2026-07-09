%global debug_package %{nil}
%global _build_id_links none

Summary: A statically typed compiled systems programming language
Name: nim
Version: 2.2.8
Release: %autorelease
License: MIT
Group: Development/Languages

# Define all sources unconditionally
Source0: https://github.com/nim-lang/nightlies/releases/download/2026-02-23-version-2-2-4f500679b196fad944caa50a753f5bbfaefda001/nim-2.2.8-linux_x64.tar.xz
Source1: https://github.com/nim-lang/nightlies/releases/download/2026-02-23-version-2-2-4f500679b196fad944caa50a753f5bbfaefda001/nim-2.2.8-linux_arm64.tar.xz

# Exclude unsupported architectures
ExclusiveArch: x86_64 aarch64

URL: https://nim-lang.org/
BuildRequires: gcc
BuildRequires: pcre2-devel
BuildRequires: openssl-devel
Requires: gcc

%description
Nim is a statically typed compiled systems programming language.
It combines successful concepts from mature languages like Python,
Ada and Modula.

%prep
# Extract prebuilt binaries
%ifarch x86_64
%setup -q -c -T -a 0
%endif
%ifarch aarch64
%setup -q -c -T -a 1
%endif

%build
# No build needed, using prebuilt binaries

%install
# Create directory structure
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_libdir}/nim
mkdir -p %{buildroot}%{_libdir}/nim/bin
mkdir -p %{buildroot}%{_libdir}/nim/doc
mkdir -p %{buildroot}%{_datadir}/nim
mkdir -p %{buildroot}%{_sysconfdir}/nim
mkdir -p %{buildroot}%{_datadir}/bash-completion/completions
mkdir -p %{buildroot}%{_datadir}/zsh/site-functions

# Install binaries to /usr/lib/nim/bin
install -Dm 755 nim-%{version}/bin/* -t %{buildroot}%{_libdir}/nim/bin

# Create symlinks in /usr/bin
ln -sf ../%{_lib}/nim/bin/atlas %{buildroot}%{_bindir}/atlas
ln -sf ../%{_lib}/nim/bin/nim %{buildroot}%{_bindir}/nim
ln -sf ../%{_lib}/nim/bin/nimble %{buildroot}%{_bindir}/nimble
ln -sf ../%{_lib}/nim/bin/nim_dbg %{buildroot}%{_bindir}/nim_dbg
ln -sf ../%{_lib}/nim/bin/nim-gdb %{buildroot}%{_bindir}/nim-gdb
ln -sf ../%{_lib}/nim/bin/nimgrep %{buildroot}%{_bindir}/nimgrep
ln -sf ../%{_lib}/nim/bin/nimpretty %{buildroot}%{_bindir}/nimpretty
ln -sf ../%{_lib}/nim/bin/nimsuggest %{buildroot}%{_bindir}/nimsuggest
ln -sf ../%{_lib}/nim/bin/testament %{buildroot}%{_bindir}/testament

# Install library files
cp -R nim-%{version}/lib %{buildroot}%{_libdir}/nim/

# Install config files to /etc/nim
install -Dm 644 nim-%{version}/config/* -t %{buildroot}%{_sysconfdir}/nim

# Install other Nim components
cp -R nim-%{version}/compiler %{buildroot}%{_libdir}/nim/
cp -R nim-%{version}/dist %{buildroot}%{_libdir}/nim/
cp -R nim-%{version}/doc %{buildroot}%{_datadir}/nim/

# Install nim.nimble to the compiler directory
install -Dm 644 nim-%{version}/nim.nimble -t %{buildroot}%{_libdir}/nim/compiler

# Install documentation files to proper location
install -Dm 644 nim-%{version}/doc/nimdoc.css -t %{buildroot}%{_libdir}/nim/doc
install -Dm 644 nim-%{version}/doc/nimdoc.cls -t %{buildroot}%{_libdir}/nim/doc
install -Dm 644 nim-%{version}/doc/basicopt.txt -t %{buildroot}%{_libdir}/nim/doc
install -Dm 644 nim-%{version}/doc/advopt.txt -t %{buildroot}%{_libdir}/nim/doc
install -Dm 644 nim-%{version}/doc/grammar.txt -t %{buildroot}%{_libdir}/nim/doc

# Install tools
install -Dm 644 nim-%{version}/tools/debug/nim-gdb.py -t %{buildroot}%{_libdir}/nim/tools
install -Dm 644 nim-%{version}/tools/dochack/dochack.nim -t %{buildroot}%{_libdir}/nim/tools/dochack
install -Dm 644 nim-%{version}/tools/dochack/dochack.js -t %{buildroot}%{_libdir}/nim/tools/dochack

# Install shell completions from tools directory
for comp in nim-%{version}/tools/*.bash-completion; do
  install -Dm 644 "${comp}" "%{buildroot}%{_datadir}/bash-completion/completions/$(basename "${comp%.bash-completion}")"
done

for comp in nim-%{version}/tools/*.zsh-completion; do
  install -Dm 644 "${comp}" "%{buildroot}%{_datadir}/zsh/site-functions/_$(basename "${comp%.zsh-completion}")"
done

# Create symlinks for configuration
ln -sf %{_sysconfdir}/nim %{buildroot}%{_libdir}/nim/config

%files
%{_bindir}/atlas
%{_bindir}/nim
%{_bindir}/nimble
%{_bindir}/nim_dbg
%{_bindir}/nim-gdb
%{_bindir}/nimgrep
%{_bindir}/nimpretty
%{_bindir}/nimsuggest
%{_bindir}/testament
%{_libdir}/nim
%{_datadir}/nim
%{_sysconfdir}/nim
# Include all bash completion files that were installed
%{_datadir}/bash-completion/completions/*
# Include all zsh completion files that were installed
%{_datadir}/zsh/site-functions/_*
# Exclude tests directories
%exclude %{_libdir}/nim/dist/*/tests
%exclude %{_libdir}/nim/dist/*/vendor/*/tests
%exclude %{_libdir}/nim/dist/*/dist/*/tests
%exclude %{_libdir}/nim/dist/*/src/*/tests
%exclude %{_libdir}/nim/dist/*/dist/*/.github
%exclude %{_libdir}/nim/dist/*/.github
%exclude %{_libdir}/nim/dist/nimble/nimble-guide
# Exclude build cache, VCS, and AI assistant files
%exclude %{_libdir}/nim/dist/*/.nimcache
%exclude %{_libdir}/nim/dist/*/.gitignore
%exclude %{_libdir}/nim/dist/*/AGENTS.md
%exclude %{_libdir}/nim/dist/*/CLAUDE.md
# Exclude .idx files in doc/html
%exclude %{_datadir}/nim/doc/html/*.idx
%exclude %{_datadir}/nim/doc/html/compiler/*.idx
%exclude %{_datadir}/nim/doc/html/compiler/*/*.idx

%changelog
* Mon Jan 01 2024 Packager <packager@example.com> - 2.2.5-1
- Initial package

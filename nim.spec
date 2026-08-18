%global debug_package %{nil}
%global _build_id_links none

Summary: A statically typed compiled systems programming language
Name: nim
Version: 2.2.10
Release: %autorelease
License: MIT
Group: Development/Languages

# Build from the upstream release source. The bootstrap compiler is compiled
# from csources_v3, then koch bootstraps the full compiler and bundled tools.
# csources_v3, checksums, atlas and sat are git-cloned during the build at the
# commits pinned in the Nim tree. Nimble is deliberately not shipped.
Source0: https://github.com/nim-lang/Nim/archive/refs/tags/v%{version}.tar.gz#/nim-%{version}.tar.gz

# Exclude unsupported architectures
ExclusiveArch: x86_64 aarch64

URL: https://nim-lang.org/
BuildRequires: gcc
BuildRequires: make
BuildRequires: git
BuildRequires: pcre2-devel
BuildRequires: openssl-devel
Requires: gcc

%description
Nim is a statically typed compiled systems programming language.
It combines successful concepts from mature languages like Python,
Ada and Modula.

%prep
%setup -q -n Nim-%{version}

%build
# Compile the bootstrap compiler from the pre-generated C sources.
# The csources makefile appends its own flags to CFLAGS, so start from a
# clean set instead of the distro defaults. Restore the RPM build flags for
# the compiler and tools built afterwards.
csources_CFLAGS="${CFLAGS-}"
csources_LDFLAGS="${LDFLAGS-}"
export CFLAGS=
export LDFLAGS=
. ci/funs.sh
nimBuildCsourcesIfNeeded
export CFLAGS="${csources_CFLAGS}"
export LDFLAGS="${csources_LDFLAGS}"
unset csources_CFLAGS csources_LDFLAGS

nim_compile_koch() {
  if [ -n "${LDFLAGS}" ]; then
    bin/nim c "$@" "--passL:${LDFLAGS}" koch
  else
    bin/nim c "$@" koch
  fi
}

koch_with_linker_flags() {
  command="$1"
  shift
  if [ -n "${LDFLAGS}" ]; then
    ./koch "${command}" "--passL:${LDFLAGS}" "$@"
  else
    ./koch "${command}" "$@"
  fi
}

# Compile koch with the bootstrap compiler, then bootstrap the full compiler.
nim_compile_koch --noNimblePath --skipUserCfg --skipParentCfg --hints:off
koch_with_linker_flags boot -d:release --skipUserCfg --skipParentCfg --hints:off

# Build the bundled tools without Nimble, then build atlas.
koch_with_linker_flags toolsNoExternal --skipUserCfg --skipParentCfg --hints:off
koch_with_linker_flags atlas --skipUserCfg --skipParentCfg --hints:off

# Generate the documentation helper required by `nim doc --index:on`.
bin/nim js -d:release --noNimblePath --skipUserCfg --skipParentCfg --hints:off tools/dochack/dochack.nim

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
install -Dm 755 bin/atlas bin/nim bin/nim_dbg bin/nimgrep bin/nimpretty bin/nimsuggest bin/testament -t %{buildroot}%{_libdir}/nim/bin
install -Dm 755 bin/nim-gdb -t %{buildroot}%{_libdir}/nim/bin

# Create symlinks in /usr/bin
ln -sf ../%{_lib}/nim/bin/atlas %{buildroot}%{_bindir}/atlas
ln -sf ../%{_lib}/nim/bin/nim %{buildroot}%{_bindir}/nim
ln -sf ../%{_lib}/nim/bin/nim_dbg %{buildroot}%{_bindir}/nim_dbg
ln -sf ../%{_lib}/nim/bin/nim-gdb %{buildroot}%{_bindir}/nim-gdb
ln -sf ../%{_lib}/nim/bin/nimgrep %{buildroot}%{_bindir}/nimgrep
ln -sf ../%{_lib}/nim/bin/nimpretty %{buildroot}%{_bindir}/nimpretty
ln -sf ../%{_lib}/nim/bin/nimsuggest %{buildroot}%{_bindir}/nimsuggest
ln -sf ../%{_lib}/nim/bin/testament %{buildroot}%{_bindir}/testament

# Install library files
cp -R lib %{buildroot}%{_libdir}/nim/

# Install config files to /etc/nim
install -Dm 644 config/* -t %{buildroot}%{_sysconfdir}/nim

# Install other Nim components
cp -R compiler %{buildroot}%{_libdir}/nim/
# Strip VCS metadata from the build-time git clones before installing.
find dist -name .git -type d -prune -exec rm -rf {} +
cp -R dist %{buildroot}%{_libdir}/nim/
cp -R doc %{buildroot}%{_datadir}/nim/

# Install nim.nimble to the compiler directory
install -Dm 644 nim.nimble -t %{buildroot}%{_libdir}/nim/compiler

# Install documentation files to proper location
install -Dm 644 doc/nimdoc.css -t %{buildroot}%{_libdir}/nim/doc
install -Dm 644 doc/nimdoc.cls -t %{buildroot}%{_libdir}/nim/doc
install -Dm 644 doc/basicopt.txt -t %{buildroot}%{_libdir}/nim/doc
install -Dm 644 doc/advopt.txt -t %{buildroot}%{_libdir}/nim/doc
install -Dm 644 doc/grammar.txt -t %{buildroot}%{_libdir}/nim/doc

# Install tools
install -Dm 644 tools/debug/nim-gdb.py -t %{buildroot}%{_libdir}/nim/tools
install -Dm 644 tools/dochack/dochack.js -t %{buildroot}%{_libdir}/nim/tools/dochack

# Install shell completions from tools directory
for comp in tools/*.bash-completion; do
  install -Dm 644 "${comp}" "%{buildroot}%{_datadir}/bash-completion/completions/$(basename "${comp%.bash-completion}")"
done

for comp in tools/*.zsh-completion; do
  install -Dm 644 "${comp}" "%{buildroot}%{_datadir}/zsh/site-functions/_$(basename "${comp%.zsh-completion}")"
done

# Create symlinks for configuration
ln -sf %{_sysconfdir}/nim %{buildroot}%{_libdir}/nim/config

%files
%{_bindir}/atlas
%{_bindir}/nim
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
%exclude %{_libdir}/nim/lib/impure/nre/.gitignore
# Exclude .idx files in doc/html
%exclude %{_datadir}/nim/doc/html/*.idx
%exclude %{_datadir}/nim/doc/html/compiler/*.idx
%exclude %{_datadir}/nim/doc/html/compiler/*/*.idx

%changelog
* Mon Jan 01 2024 Packager <packager@example.com> - 2.2.5-1
- Initial package

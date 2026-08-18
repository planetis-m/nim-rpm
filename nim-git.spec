%global debug_package %{nil}
%global _build_id_links none

%global snapshot_date %(date -u +%Y%m%d)
%global nim_version 2.3.1

Name:           nim-git
Version:        %{nim_version}~devel.%{snapshot_date}
Release:        %autorelease
Summary:        Statically typed compiled systems programming language (development snapshot)
License:        MIT
URL:            https://nim-lang.org/

ExclusiveArch:  x86_64 aarch64

BuildRequires:  gcc
BuildRequires:  git
BuildRequires:  make
BuildRequires:  redhat-rpm-config

Requires:       gcc
Requires:       git
Provides:       nim = %{version}-%{release}
Conflicts:      nim

%description
Nim is a statically typed compiled systems programming language combining
concepts from languages such as Python, Ada, and Modula.

This package tracks the development branch and is bootstrapped entirely from
source. Nimble is not included.

%prep
%autosetup -c -T -n Nim-devel
git clone -q --depth 1 --branch devel https://github.com/nim-lang/Nim.git .

%build
%set_build_flags

# csources_v3 appends its own bootstrap flags to CFLAGS. Keep RPM's flags out
# of that bootstrap build. The upstream helper fetches its pinned csources.
rpm_cflags="${CFLAGS-}"
rpm_ldflags="${LDFLAGS-}"
export CFLAGS=
export LDFLAGS=
. ci/funs.sh
nimBuildCsourcesIfNeeded
export CFLAGS="${rpm_cflags}"
export LDFLAGS="${rpm_ldflags}"

nim_compile_koch() {
  if [ -n "${rpm_cflags}" ]; then
    set -- "--passC:${rpm_cflags}" "$@"
  fi
  if [ -n "${rpm_ldflags}" ]; then
    set -- "--passL:${rpm_ldflags}" "$@"
  fi
  bin/nim c "$@" koch
}

# koch() forwards the distro flags to the koch commands. `-d:release` must
# stay first: koch boot only inserts the `c` command when its cmdLineRest
# starts with '-', and parseopt single-quotes multi-word args like --passC.
koch() {
  command="$1"
  shift
  if [ -n "${rpm_cflags}" ]; then
    set -- "--passC:${rpm_cflags}" "$@"
  fi
  if [ -n "${rpm_ldflags}" ]; then
    set -- "--passL:${rpm_ldflags}" "$@"
  fi
  ./koch "${command}" -d:release "$@"
}

nim_compile_koch --noNimblePath --skipUserCfg --skipParentCfg --hints:off
koch boot --skipUserCfg --skipParentCfg --hints:off
koch toolsNoExternal --skipUserCfg --skipParentCfg --hints:off
koch atlas --skipUserCfg --skipParentCfg --hints:off

# nim doc --index:on invokes this generated JavaScript helper.
bin/nim js -d:release --noNimblePath --skipUserCfg --skipParentCfg \
  --hints:off tools/dochack/dochack.nim

%install
install -d \
  %{buildroot}%{_bindir} \
  %{buildroot}%{_libdir}/nim/bin \
  %{buildroot}%{_libdir}/nim/dist \
  %{buildroot}%{_libdir}/nim/doc \
  %{buildroot}%{_libdir}/nim/tools/dochack \
  %{buildroot}%{_datadir}/nim \
  %{buildroot}%{_sysconfdir}/nim \
  %{buildroot}%{_datadir}/bash-completion/completions \
  %{buildroot}%{_datadir}/zsh/site-functions

install -m 0755 -t %{buildroot}%{_libdir}/nim/bin \
  bin/atlas bin/nim bin/nim_dbg bin/nim-gdb bin/nimgrep bin/nimpretty \
  bin/nimsuggest bin/testament bin/nifler bin/nifmake

for tool in atlas nim nim_dbg nim-gdb nimgrep nimpretty nimsuggest testament; do
  ln -s "../%{_lib}/nim/bin/${tool}" "%{buildroot}%{_bindir}/${tool}"
done

# nifler and nifmake are the compiler's pinned private helpers. nim ic finds
# them beside nim; the public commands are owned by nimony-git.
cp -a lib compiler %{buildroot}%{_libdir}/nim/
cp -a dist/checksums dist/nimony %{buildroot}%{_libdir}/nim/dist/
rm -rf \
  %{buildroot}%{_libdir}/nim/dist/checksums/.git \
  %{buildroot}%{_libdir}/nim/dist/nimony/.git

install -m 0644 -t %{buildroot}%{_sysconfdir}/nim config/*
cp -a doc %{buildroot}%{_datadir}/nim/
install -m 0644 nim.nimble -t %{buildroot}%{_libdir}/nim/compiler
install -m 0644 -t %{buildroot}%{_libdir}/nim/doc \
  doc/nimdoc.css doc/nimdoc.cls doc/basicopt.txt doc/advopt.txt doc/grammar.txt
install -m 0644 tools/debug/nim-gdb.py -t %{buildroot}%{_libdir}/nim/tools
install -m 0644 tools/dochack/dochack.js -t %{buildroot}%{_libdir}/nim/tools/dochack

install -m 0644 tools/nim.bash-completion \
  %{buildroot}%{_datadir}/bash-completion/completions/nim
install -m 0644 tools/nimgrep.bash-completion \
  %{buildroot}%{_datadir}/bash-completion/completions/nimgrep
install -m 0644 tools/nimpretty.bash-completion \
  %{buildroot}%{_datadir}/bash-completion/completions/nimpretty
install -m 0644 tools/nimsuggest.bash-completion \
  %{buildroot}%{_datadir}/bash-completion/completions/nimsuggest
install -m 0644 tools/nim.zsh-completion \
  %{buildroot}%{_datadir}/zsh/site-functions/_nim

ln -s %{_sysconfdir}/nim %{buildroot}%{_libdir}/nim/config

%files
%license copying.txt
%doc readme.md
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
%dir %{_sysconfdir}/nim
%config(noreplace) %{_sysconfdir}/nim/*
%{_datadir}/bash-completion/completions/nim
%{_datadir}/bash-completion/completions/nimgrep
%{_datadir}/bash-completion/completions/nimpretty
%{_datadir}/bash-completion/completions/nimsuggest
%{_datadir}/zsh/site-functions/_nim

%exclude %{_libdir}/nim/dist/*/tests
%exclude %{_libdir}/nim/dist/*/vendor/*/tests
%exclude %{_libdir}/nim/dist/*/.github
%exclude %{_libdir}/nim/dist/*/.nimcache
%exclude %{_libdir}/nim/dist/*/.gitignore
%exclude %{_libdir}/nim/dist/*/AGENTS.md
%exclude %{_libdir}/nim/dist/*/CLAUDE.md
%exclude %{_libdir}/nim/lib/impure/nre/.gitignore
%exclude %{_datadir}/nim/doc/html/*.idx
%exclude %{_datadir}/nim/doc/html/compiler/*.idx
%exclude %{_datadir}/nim/doc/html/compiler/*/*.idx

%changelog
%autochangelog

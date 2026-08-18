%global debug_package %{nil}
%global _build_id_links none

%global snapshot_date %(date -u +%Y%m%d)
%global upstream_version 0.4.0

Name:           nimony-git
Version:        %{upstream_version}~devel.%{snapshot_date}
Release:        %autorelease
Summary:        Nimony compiler and toolchain (development snapshot)
License:        MIT
URL:            https://github.com/nim-lang/nimony
Source0:        https://github.com/nim-lang/nimony/archive/refs/heads/master.tar.gz#/nimony-master-%{version}.tar.gz
Source1:        https://github.com/nim-lang/mimalloc/archive/refs/heads/master.tar.gz#/mimalloc-master.tar.gz

BuildRequires:  gcc
BuildRequires:  nim
BuildRequires:  redhat-rpm-config

Requires:       gcc
Requires:       git
Provides:       nimony = %{version}-%{release}
Conflicts:      nimony

%description
Nimony is a new Nim implementation under active development. This package
tracks its master branch and includes the compiler's private supporting tools.

%prep
%autosetup -n nimony-master
tar -xzf %{SOURCE1} -C vendor/mimalloc --strip-components=1

%build
%set_build_flags

# Pass matching compiler and linker flags to hastur and every host-Nim tool it
# builds. Fedora's hardened linker flags require objects compiled as PIE/PIC.
if [ -n "${LDFLAGS-}" ]; then
  hastur_flags="--forward:--passC:\"${CFLAGS}\" --passL:\"${LDFLAGS}\""
  nim c "--passC:${CFLAGS}" "--passL:${LDFLAGS}" -r src/hastur \
    build all --release "${hastur_flags}"
else
  hastur_flags="--forward:--passC:\"${CFLAGS}\""
  nim c "--passC:${CFLAGS}" -r src/hastur \
    build all --release "${hastur_flags}"
fi

%install
install -d \
  %{buildroot}%{_bindir} \
  %{buildroot}%{_libdir}/nimony/bin \
  %{buildroot}%{_libdir}/nimony/doc \
  %{buildroot}%{_libdir}/nimony/src/nimony \
  %{buildroot}%{_libdir}/nimony/vendor/mimalloc \
  %{buildroot}%{_datadir}/nimony

# All generated tools are installed privately because the compiler locates
# them beside itself. Expose only the established user-facing commands.
install -m 0755 bin/* -t %{buildroot}%{_libdir}/nimony/bin
for tool in dagon nifler nifmake nimony pnak; do
  ln -s "../%{_lib}/nimony/bin/${tool}" "%{buildroot}%{_bindir}/${tool}"
done

cp -a lib tools %{buildroot}%{_libdir}/nimony/
cp -a doc %{buildroot}%{_datadir}/nimony/

# validator searches for this grammar relative to its private bin directory.
install -m 0644 doc/tags.md -t %{buildroot}%{_libdir}/nimony/doc

# Sources required for compiling Nimony plugins.
cp -a src/lib src/models %{buildroot}%{_libdir}/nimony/src/
install -m 0644 src/nimony/nif_annotations.nim \
  -t %{buildroot}%{_libdir}/nimony/src/nimony
cp -a src/nimony/lib %{buildroot}%{_libdir}/nimony/src/nimony/

# The standard library compiles mimalloc into user programs.
cp -a vendor/mimalloc/src vendor/mimalloc/include \
  %{buildroot}%{_libdir}/nimony/vendor/mimalloc/
install -m 0644 vendor/mimalloc/LICENSE \
  -t %{buildroot}%{_libdir}/nimony/vendor/mimalloc

%files
%license license.txt
%doc README.md
%{_bindir}/dagon
%{_bindir}/nifler
%{_bindir}/nifmake
%{_bindir}/nimony
%{_bindir}/pnak
%{_libdir}/nimony
%{_datadir}/nimony

%changelog
%autochangelog
